import sys
sys.path.insert(0, '.')
import torch
from unet import UNet
from dataset import PineWiltDataset, get_dataloader
from loss import DiceBCELoss
from metrics import SegmentationMetrics

print('=== Model Validation Tests ===')

# 1. Test UNet model
model = UNet(n_channels=1, n_classes=2)
x = torch.randn(2, 1, 256, 256)
out = model(x)
print(f'[PASS] UNet forward: input{list(x.shape)} -> output{list(out.shape)}')
total = sum(p.numel() for p in model.parameters())
print(f'[INFO] Total params: {total:,}')

# 2. Test dataset (synthetic)
dataset = PineWiltDataset('./data', split='train', img_size=256)
sample = dataset[0]
print(f'[PASS] Dataset: image={list(sample["image"].shape)}, mask={list(sample["mask"].shape)}')

# 3. Test loss function
criterion = DiceBCELoss()
target = torch.randint(0, 2, (2, 256, 256))
loss = criterion(out, target)
print(f'[PASS] Loss: {loss.item():.4f}')

# 4. Test metrics
metrics = SegmentationMetrics(n_classes=2)
metrics.update(out, target)
results = metrics.get_results()
print(f'[PASS] Metrics: Dice={results["dice_foreground"]:.4f}, IoU={results["iou_foreground"]:.4f}')

print()
print('=== All tests passed! ===')
