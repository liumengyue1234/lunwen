"""
模型评估与测试脚本
生成详细评估报告
"""

import os
import json
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime

import torch
from PIL import Image, ImageDraw, ImageFont
import torchvision.transforms.functional as TF
from tqdm import tqdm

from unet import UNet
from dataset import get_dataloader, PineWiltDataset
from metrics import SegmentationMetrics


def predict_single(model, image_path: str, device, img_size: int = 256,
                   threshold: float = 0.5):
    """
    对单张CT图像进行预测

    Returns:
        dict: 包含预测掩码、置信度图、病变面积等
    """
    model.eval()

    # 读取图像
    image = Image.open(image_path).convert('L')
    orig_size = image.size  # (W, H)

    # 预处理
    image_resized = image.resize((img_size, img_size), Image.BILINEAR)
    img_tensor = TF.to_tensor(image_resized).unsqueeze(0).to(device)  # [1,1,H,W]

    with torch.no_grad():
        logits = model(img_tensor)  # [1, 2, H, W]
        probs = torch.softmax(logits, dim=1)
        pred_mask = probs.argmax(dim=1).squeeze().cpu().numpy()  # [H, W]
        confidence = probs[0, 1].cpu().numpy()  # 前景置信度

    # 还原到原始尺寸
    pred_pil = Image.fromarray((pred_mask * 255).astype(np.uint8))
    pred_pil = pred_pil.resize(orig_size, Image.NEAREST)
    pred_final = np.array(pred_pil) // 255

    conf_pil = Image.fromarray((confidence * 255).astype(np.uint8))
    conf_pil = conf_pil.resize(orig_size, Image.NEAREST)

    # 计算病变面积
    total_pixels = pred_final.size
    lesion_pixels = pred_final.sum()
    lesion_ratio = lesion_pixels / total_pixels

    return {
        'pred_mask': pred_final,
        'confidence_map': np.array(conf_pil),
        'lesion_pixels': int(lesion_pixels),
        'total_pixels': total_pixels,
        'lesion_ratio': float(lesion_ratio),
        'has_lesion': lesion_ratio > 0.01,  # 病变面积超过1%视为阳性
        'original_size': orig_size
    }


def evaluate_dataset(model, val_loader, device):
    """在验证集上评估模型"""
    metrics = SegmentationMetrics(n_classes=2)
    model.eval()

    with torch.no_grad():
        for batch in tqdm(val_loader, desc='评估中'):
            images = batch['image'].to(device)
            masks = batch['mask'].to(device)
            logits = model(images)
            metrics.update(logits, masks)

    return metrics.get_results()


def generate_report(results: dict, output_path: str, args_dict: dict):
    """生成评估报告（JSON + 文本）"""
    report = {
        'project': '基于CT的松材线虫病检测系统',
        'model': 'U-Net',
        'evaluation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'config': args_dict,
        'metrics': results,
        'interpretation': {
            'dice_score': f"{results['dice_foreground']:.2%} Dice系数（越高越好，理想值>0.85）",
            'iou_score': f"{results['iou_foreground']:.2%} IoU交并比（越高越好，理想值>0.75）",
            'precision': f"{results['precision_foreground']:.2%} 精确率（减少误报）",
            'recall': f"{results['recall_foreground']:.2%} 召回率（减少漏报）",
        }
    }

    # 保存JSON报告
    report_path = Path(output_path) / 'evaluation_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # 保存文本报告
    txt_path = Path(output_path) / 'evaluation_report.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("   基于CT的松材线虫病检测系统 - 评估报告\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"评估时间: {report['evaluation_time']}\n")
        f.write(f"模型架构: {report['model']}\n\n")
        f.write("-" * 40 + "\n")
        f.write("分割性能指标\n")
        f.write("-" * 40 + "\n")
        f.write(f"Dice��数 (前景):   {results['dice_foreground']:.4f}  ({results['dice_foreground']:.2%})\n")
        f.write(f"IoU (前景):        {results['iou_foreground']:.4f}  ({results['iou_foreground']:.2%})\n")
        f.write(f"精确率 (前景):     {results['precision_foreground']:.4f}\n")
        f.write(f"召回率 (前景):     {results['recall_foreground']:.4f}\n")
        f.write(f"像素准确率:        {results['accuracy']:.4f}\n")
        f.write(f"平均Dice:          {results['mean_dice']:.4f}\n")
        f.write(f"平均IoU:           {results['mean_iou']:.4f}\n\n")
        f.write("-" * 40 + "\n")
        f.write("指标说明\n")
        f.write("-" * 40 + "\n")
        for key, val in report['interpretation'].items():
            f.write(f"  {val}\n")
        f.write("\n" + "=" * 60 + "\n")

    print(f"\n报告已保存至:\n  {report_path}\n  {txt_path}")
    return report


def parse_args():
    parser = argparse.ArgumentParser(description='松材线虫病CT影像分割模型评估')
    parser.add_argument('--checkpoint', type=str, default='./checkpoints/best_model.pth',
                        help='模型权重文件路径')
    parser.add_argument('--data_dir', type=str, default='./data',
                        help='数据集目录')
    parser.add_argument('--output_dir', type=str, default='./results',
                        help='输出目录')
    parser.add_argument('--batch_size', type=int, default=8)
    parser.add_argument('--img_size', type=int, default=256)
    parser.add_argument('--num_workers', type=int, default=0)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")

    # 加载模型
    model = UNet(n_channels=1, n_classes=2).to(device)
    if Path(args.checkpoint).exists():
        ckpt = torch.load(args.checkpoint, map_location=device)
        model.load_state_dict(ckpt['model_state_dict'])
        print(f"加载检查点: {args.checkpoint} (Epoch {ckpt.get('epoch', '?')})")
    else:
        print("[WARNING] 未找到检查点，使用随机初始化权重进行演示")

    # 评估
    val_loader = get_dataloader(
        args.data_dir, split='val',
        batch_size=args.batch_size,
        img_size=args.img_size
    )
    results = evaluate_dataset(model, val_loader, device)

    # 生成报告
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    report = generate_report(results, args.output_dir, vars(args))

    print("\n=== 评估完成 ===")
    print(f"Dice系数: {results['dice_foreground']:.4f}")
    print(f"IoU:      {results['iou_foreground']:.4f}")
    print(f"精确率:   {results['precision_foreground']:.4f}")
    print(f"召回率:   {results['recall_foreground']:.4f}")
