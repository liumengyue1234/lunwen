"""
模型训练脚本
松材线虫病CT影像分割模型训练
"""

import os
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime

import torch
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
from tqdm import tqdm

from unet import UNet
from dataset import get_dataloader
from loss import DiceBCELoss
from metrics import SegmentationMetrics

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def train_one_epoch(model, loader, optimizer, criterion, device, epoch):
    """训练一个epoch"""
    model.train()
    total_loss = 0.0
    metrics = SegmentationMetrics(n_classes=2)

    pbar = tqdm(loader, desc=f'Epoch {epoch} [Train]', leave=False)
    for batch in pbar:
        images = batch['image'].to(device)
        masks = batch['mask'].to(device)

        optimizer.zero_grad()
        logits = model(images)
        loss = criterion(logits, masks)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        metrics.update(logits, masks)
        pbar.set_postfix({'loss': f'{loss.item():.4f}'})

    avg_loss = total_loss / len(loader)
    results = metrics.get_results()
    return avg_loss, results


@torch.no_grad()
def validate(model, loader, criterion, device, epoch):
    """验证集评估"""
    model.eval()
    total_loss = 0.0
    metrics = SegmentationMetrics(n_classes=2)

    pbar = tqdm(loader, desc=f'Epoch {epoch} [Val]', leave=False)
    for batch in pbar:
        images = batch['image'].to(device)
        masks = batch['mask'].to(device)

        logits = model(images)
        loss = criterion(logits, masks)

        total_loss += loss.item()
        metrics.update(logits, masks)

    avg_loss = total_loss / len(loader)
    results = metrics.get_results()
    return avg_loss, results


def train(args):
    """主训练函数"""
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"使用设备: {device}")

    # 创建输出目录
    save_dir = Path(args.save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    # 数据加载
    train_loader = get_dataloader(
        args.data_dir, split='train',
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        img_size=args.img_size
    )
    val_loader = get_dataloader(
        args.data_dir, split='val',
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        img_size=args.img_size
    )
    logger.info(f"训练批次: {len(train_loader)}, 验证批次: {len(val_loader)}")

    # 模型
    model = UNet(n_channels=1, n_classes=2, bilinear=args.bilinear).to(device)
    total_params = sum(p.numel() for p in model.parameters())
    logger.info(f"模型参数量: {total_params:,}")

    # 损失函数和优化器
    criterion = DiceBCELoss(bce_weight=0.5)
    optimizer = optim.AdamW(
        model.parameters(),
        lr=args.lr,
        weight_decay=args.weight_decay
    )
    scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)

    # 训练循环
    best_dice = 0.0
    history = []

    for epoch in range(1, args.epochs + 1):
        train_loss, train_metrics = train_one_epoch(
            model, train_loader, optimizer, criterion, device, epoch
        )
        val_loss, val_metrics = validate(
            model, val_loader, criterion, device, epoch
        )
        scheduler.step()

        # 记录历史
        epoch_record = {
            'epoch': epoch,
            'train_loss': train_loss,
            'val_loss': val_loss,
            'train_dice': train_metrics['dice_foreground'],
            'val_dice': val_metrics['dice_foreground'],
            'train_iou': train_metrics['iou_foreground'],
            'val_iou': val_metrics['iou_foreground'],
            'lr': scheduler.get_last_lr()[0]
        }
        history.append(epoch_record)

        logger.info(
            f"Epoch {epoch:03d}/{args.epochs} | "
            f"Train Loss: {train_loss:.4f} | "
            f"Val Loss: {val_loss:.4f} | "
            f"Val Dice: {val_metrics['dice_foreground']:.4f} | "
            f"Val IoU: {val_metrics['iou_foreground']:.4f}"
        )

        # 保存最优模型
        if val_metrics['dice_foreground'] > best_dice:
            best_dice = val_metrics['dice_foreground']
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_dice': best_dice,
                'args': vars(args)
            }, save_dir / 'best_model.pth')
            logger.info(f">>> 保存最优模型, Val Dice: {best_dice:.4f}")

        # 定期保存检查点
        if epoch % args.save_interval == 0:
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'history': history
            }, save_dir / f'checkpoint_epoch{epoch:03d}.pth')

    # 保存训练历史
    history_path = results_dir / 'training_history.json'
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    logger.info(f"训练历史保存至: {history_path}")

    logger.info(f"训练完成! 最优 Val Dice: {best_dice:.4f}")
    return history


def parse_args():
    parser = argparse.ArgumentParser(description='松材线虫病CT影像分割模型训练')
    parser.add_argument('--data_dir', type=str, default='./data',
                        help='数据集目录')
    parser.add_argument('--save_dir', type=str, default='./checkpoints',
                        help='模型保存目录')
    parser.add_argument('--results_dir', type=str, default='./results',
                        help='结果保存目录')
    parser.add_argument('--epochs', type=int, default=50,
                        help='训练轮数')
    parser.add_argument('--batch_size', type=int, default=8,
                        help='批量大小')
    parser.add_argument('--lr', type=float, default=1e-4,
                        help='学习率')
    parser.add_argument('--weight_decay', type=float, default=1e-4,
                        help='权重衰减')
    parser.add_argument('--img_size', type=int, default=256,
                        help='图像尺寸')
    parser.add_argument('--num_workers', type=int, default=0,
                        help='数据加载线程数')
    parser.add_argument('--bilinear', action='store_true',
                        help='使用双线性插值上采样')
    parser.add_argument('--save_interval', type=int, default=10,
                        help='检查点保存间隔（epoch）')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    logger.info("开始训练松材线虫病CT影像分割模型")
    logger.info(f"配置: {vars(args)}")
    history = train(args)
