"""
评估指标计算
Dice系数、IoU、精确率、召回率等分割指标
"""

import numpy as np
import torch


class SegmentationMetrics:
    """图像分割评估指标"""

    def __init__(self, n_classes: int = 2, smooth: float = 1e-6):
        self.n_classes = n_classes
        self.smooth = smooth
        self.reset()

    def reset(self):
        self.tp = np.zeros(self.n_classes)
        self.fp = np.zeros(self.n_classes)
        self.fn = np.zeros(self.n_classes)
        self.tn = np.zeros(self.n_classes)

    def update(self, pred: torch.Tensor, target: torch.Tensor):
        """
        Args:
            pred: [B, C, H, W] 模型logits 或 [B, H, W] 预测类别
            target: [B, H, W] 真实标注
        """
        if pred.dim() == 4:
            pred = pred.argmax(dim=1)  # [B, H, W]

        pred = pred.cpu().numpy().flatten()
        target = target.cpu().numpy().flatten()

        for cls in range(self.n_classes):
            pred_cls = (pred == cls)
            target_cls = (target == cls)

            self.tp[cls] += (pred_cls & target_cls).sum()
            self.fp[cls] += (pred_cls & ~target_cls).sum()
            self.fn[cls] += (~pred_cls & target_cls).sum()
            self.tn[cls] += (~pred_cls & ~target_cls).sum()

    def dice(self):
        """Dice系数 (F1-score)"""
        dice = (2 * self.tp + self.smooth) / (2 * self.tp + self.fp + self.fn + self.smooth)
        return dice

    def iou(self):
        """交并比 (Jaccard Index)"""
        iou = (self.tp + self.smooth) / (self.tp + self.fp + self.fn + self.smooth)
        return iou

    def precision(self):
        """精确率"""
        prec = (self.tp + self.smooth) / (self.tp + self.fp + self.smooth)
        return prec

    def recall(self):
        """召回率"""
        rec = (self.tp + self.smooth) / (self.tp + self.fn + self.smooth)
        return rec

    def accuracy(self):
        """像素准确率"""
        total = self.tp + self.fp + self.fn + self.tn
        acc = (self.tp + self.tn + self.smooth) / (total + self.smooth)
        return acc

    def get_results(self):
        """返回所有指标汇总"""
        dice = self.dice()
        iou = self.iou()
        prec = self.precision()
        rec = self.recall()
        acc = self.accuracy()

        return {
            'dice_foreground': float(dice[1]),  # 前景（病变区域）
            'iou_foreground': float(iou[1]),
            'precision_foreground': float(prec[1]),
            'recall_foreground': float(rec[1]),
            'accuracy': float(acc.mean()),
            'mean_dice': float(dice.mean()),
            'mean_iou': float(iou.mean()),
        }

    def print_results(self, epoch=None):
        """打印评估结果"""
        results = self.get_results()
        prefix = f"[Epoch {epoch}] " if epoch is not None else ""
        print(f"\n{prefix}评估结果:")
        print(f"  Dice (前景):    {results['dice_foreground']:.4f}")
        print(f"  IoU  (前景):    {results['iou_foreground']:.4f}")
        print(f"  精确率 (前景):  {results['precision_foreground']:.4f}")
        print(f"  召回率 (前景):  {results['recall_foreground']:.4f}")
        print(f"  像素准确率:     {results['accuracy']:.4f}")
        print(f"  平均Dice:       {results['mean_dice']:.4f}")
        print(f"  平均IoU:        {results['mean_iou']:.4f}")
        return results
