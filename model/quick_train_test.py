"""
快速训练验证脚本 - 用合成数据训练3个epoch验证流程
"""
import sys
sys.path.insert(0, '.')
import argparse
args = argparse.Namespace(
    data_dir='./data',
    save_dir='./checkpoints',
    results_dir='./results',
    epochs=3,
    batch_size=4,
    lr=1e-4,
    weight_decay=1e-4,
    img_size=128,
    num_workers=0,
    bilinear=False,
    save_interval=10
)

import sys
sys.argv = ['train.py']

from train import train
print("=== Quick Training Test (3 epochs, synthetic data) ===")
history = train(args)
print(f"\nFinal val Dice: {history[-1]['val_dice']:.4f}")
print(f"Final val IoU:  {history[-1]['val_iou']:.4f}")
print("=== Training pipeline OK ===")
