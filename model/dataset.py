"""
数据集加载器
松材线虫病CT影像数据集处理
"""

import os
import numpy as np
from pathlib import Path
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import torchvision.transforms.functional as TF
import random


class PineWiltDataset(Dataset):
    """
    松材线虫病CT影像数据集
    
    目录结构:
        data/
            train/
                images/   # CT原始图像 (.png/.jpg/.tif)
                masks/    # 分割标注掩码 (.png)
            val/
                images/
                masks/
    """

    def __init__(self, data_dir: str, split: str = 'train',
                 img_size: int = 256, augment: bool = True):
        """
        Args:
            data_dir: 数据根目录
            split: 'train' or 'val'
            img_size: 图像尺寸（正方形）
            augment: 是否进行数据增强
        """
        self.data_dir = Path(data_dir)
        self.split = split
        self.img_size = img_size
        self.augment = augment and (split == 'train')

        self.img_dir = self.data_dir / split / 'images'
        self.mask_dir = self.data_dir / split / 'masks'

        # 获取图像列表
        self.image_files = sorted([
            f for f in self.img_dir.glob('*')
            if f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp']
        ])

        if len(self.image_files) == 0:
            print(f"[WARNING] {split} 数据集为空，将使用模拟数据进行演示")
            self._use_synthetic = True
            self._synthetic_size = 100 if split == 'train' else 20
        else:
            self._use_synthetic = False
            print(f"[INFO] {split} 数据集共 {len(self.image_files)} 张图像")

    def __len__(self):
        if self._use_synthetic:
            return self._synthetic_size
        return len(self.image_files)

    def __getitem__(self, idx):
        if self._use_synthetic:
            return self._get_synthetic_sample(idx)

        img_path = self.image_files[idx]
        mask_path = self.mask_dir / (img_path.stem + '.png')

        # 读取图像（灰度）
        image = Image.open(img_path).convert('L')
        
        # 读取掩码
        if mask_path.exists():
            mask = Image.open(mask_path).convert('L')
        else:
            # 如果没有掩码文件，创建全黑掩码
            mask = Image.new('L', image.size, 0)

        # 调整尺寸
        image = image.resize((self.img_size, self.img_size), Image.BILINEAR)
        mask = mask.resize((self.img_size, self.img_size), Image.NEAREST)

        # 数据增强
        if self.augment:
            image, mask = self._augment(image, mask)

        # 转换为Tensor
        image = TF.to_tensor(image)  # [1, H, W], 值域[0,1]
        mask = torch.from_numpy(np.array(mask)).long()  # [H, W], 0或1
        
        # 二值化掩码（阈值127）
        mask = (mask > 127).long()

        return {
            'image': image,
            'mask': mask,
            'filename': img_path.name
        }

    def _get_synthetic_sample(self, idx):
        """生成模拟数据（用于演示和测试）"""
        torch.manual_seed(idx)
        image = torch.randn(1, self.img_size, self.img_size) * 0.3 + 0.5
        image = torch.clamp(image, 0, 1)
        
        # 模拟病变区域（圆形）
        mask = torch.zeros(self.img_size, self.img_size, dtype=torch.long)
        cx = torch.randint(60, self.img_size - 60, (1,)).item()
        cy = torch.randint(60, self.img_size - 60, (1,)).item()
        r = torch.randint(20, 50, (1,)).item()
        y, x = torch.meshgrid(torch.arange(self.img_size), torch.arange(self.img_size), indexing='ij')
        circle = ((x - cx) ** 2 + (y - cy) ** 2) <= r ** 2
        mask[circle] = 1
        
        return {
            'image': image,
            'mask': mask,
            'filename': f'synthetic_{idx}.png'
        }

    def _augment(self, image, mask):
        """数据增强（随机翻转、旋转、亮度调整）"""
        # 随机水平翻转
        if random.random() > 0.5:
            image = TF.hflip(image)
            mask = TF.hflip(mask)

        # 随机垂直翻转
        if random.random() > 0.5:
            image = TF.vflip(image)
            mask = TF.vflip(mask)

        # 随机旋转
        if random.random() > 0.5:
            angle = random.uniform(-30, 30)
            image = TF.rotate(image, angle)
            mask = TF.rotate(mask, angle)

        # 随机亮度/对比度调整（仅图像）
        if random.random() > 0.5:
            image = TF.adjust_brightness(image, random.uniform(0.8, 1.2))
        if random.random() > 0.5:
            image = TF.adjust_contrast(image, random.uniform(0.8, 1.2))

        return image, mask


def get_dataloader(data_dir: str, split: str = 'train',
                   batch_size: int = 8, num_workers: int = 0,
                   img_size: int = 256) -> DataLoader:
    """获取数据加载器"""
    dataset = PineWiltDataset(data_dir, split=split, img_size=img_size)
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=(split == 'train'),
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available()
    )
    return loader


if __name__ == '__main__':
    # 测试数据集
    loader = get_dataloader('./data', split='train', batch_size=4)
    batch = next(iter(loader))
    print(f"图像形状: {batch['image'].shape}")
    print(f"掩码形状: {batch['mask'].shape}")
    print(f"图像值域: [{batch['image'].min():.3f}, {batch['image'].max():.3f}]")
    print(f"掩码唯一值: {batch['mask'].unique()}")
