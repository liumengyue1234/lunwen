"""
损失函数定义
Dice Loss + BCE Loss 组合用于图像分割
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class DiceLoss(nn.Module):
    """Dice损失函数，适合处理类别不平衡问题"""

    def __init__(self, smooth=1.0):
        super().__init__()
        self.smooth = smooth

    def forward(self, logits, targets):
        """
        Args:
            logits: [B, C, H, W] 模型原始输出
            targets: [B, H, W] 标注掩码 (0 or 1)
        """
        probs = F.softmax(logits, dim=1)  # [B, C, H, W]
        
        # 取前景类（类别1）的预测概率
        pred = probs[:, 1, :, :]  # [B, H, W]
        target = targets.float()

        intersection = (pred * target).sum(dim=(1, 2))
        union = pred.sum(dim=(1, 2)) + target.sum(dim=(1, 2))

        dice = (2.0 * intersection + self.smooth) / (union + self.smooth)
        return 1.0 - dice.mean()


class DiceBCELoss(nn.Module):
    """Dice Loss + BCE Loss 组合"""

    def __init__(self, smooth=1.0, bce_weight=0.5):
        super().__init__()
        self.dice_loss = DiceLoss(smooth)
        self.bce_weight = bce_weight

    def forward(self, logits, targets):
        dice = self.dice_loss(logits, targets)
        
        # BCE loss: 需要将targets转为one-hot形式
        bce = F.cross_entropy(logits, targets)
        
        return dice + self.bce_weight * bce


class FocalLoss(nn.Module):
    """Focal Loss，对难分样本给予更大权重"""

    def __init__(self, alpha=0.8, gamma=2):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, logits, targets):
        ce_loss = F.cross_entropy(logits, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        return focal_loss.mean()
