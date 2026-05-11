"""
模型推理API服务
FastAPI接口，供Spring Boot后端调用
"""

import io
import os
import sys
import base64
import logging
import numpy as np
from pathlib import Path
from datetime import datetime

import torch
import uvicorn
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# 添加模型目录到PATH
sys.path.insert(0, str(Path(__file__).parent))
from unet import UNet
from evaluate import predict_single

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化FastAPI
app = FastAPI(
    title="松材线虫病CT检测API",
    description="基于U-Net的CT影像病变区域分割服务",
    version="1.0.0"
)

# CORS配置（允许Spring Boot后端调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局模型变量
model = None
device = None
IMG_SIZE = 256
CHECKPOINT_PATH = "./checkpoints/best_model.pth"


def load_model():
    """加载模型"""
    global model, device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = UNet(n_channels=1, n_classes=2).to(device)

    if Path(CHECKPOINT_PATH).exists():
        ckpt = torch.load(CHECKPOINT_PATH, map_location=device)
        model.load_state_dict(ckpt['model_state_dict'])
        logger.info(f"模型加载成功: {CHECKPOINT_PATH}")
    else:
        logger.warning("未找到检查点文件，使用随机初始化权重（演示模式）")

    model.eval()


@app.on_event("startup")
async def startup_event():
    load_model()
    logger.info("松材线虫病CT检测服务启动完成")


class PredictResponse(BaseModel):
    success: bool
    lesion_detected: bool
    lesion_ratio: float
    lesion_pixels: int
    total_pixels: int
    confidence: float
    mask_base64: str
    overlay_base64: str
    message: str
    timestamp: str


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "device": str(device),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/predict", response_model=PredictResponse)
async def predict(file: UploadFile = File(...)):
    """
    上传CT影像进行病变检测

    Returns:
        - 是否检测到病变
        - 病变区域面积比
        - 分割掩码（Base64）
        - 可视化叠加图（Base64）
    """
    # 验证文件类型
    allowed_types = {'image/png', 'image/jpeg', 'image/tiff', 'image/bmp'}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}，请上传PNG/JPEG/TIFF/BMP格式"
        )

    try:
        # 读取上传的图像
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('L')
        orig_size = image.size

        # 保存临时文件
        tmp_path = f"/tmp/ct_upload_{datetime.now().timestamp()}.png"
        image.save(tmp_path)

        # 模型推理
        result = _run_inference(image)

        # 生成可视化
        mask_img = Image.fromarray((result['pred_mask'] * 255).astype(np.uint8))
        overlay_img = _create_overlay(image, result['pred_mask'])

        # 转Base64
        mask_b64 = _img_to_base64(mask_img)
        overlay_b64 = _img_to_base64(overlay_img)

        # 清理临时文件
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        return PredictResponse(
            success=True,
            lesion_detected=result['has_lesion'],
            lesion_ratio=round(result['lesion_ratio'], 6),
            lesion_pixels=result['lesion_pixels'],
            total_pixels=result['total_pixels'],
            confidence=round(float(result['confidence_map'].mean() / 255), 4),
            mask_base64=mask_b64,
            overlay_base64=overlay_b64,
            message="检测到病变区域，请及时处理" if result['has_lesion'] else "未检测到明显病变",
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"预测失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")


def _run_inference(image: Image.Image) -> dict:
    """执行模型推理"""
    import torchvision.transforms.functional as TF

    orig_size = image.size
    image_resized = image.resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR)
    img_tensor = TF.to_tensor(image_resized).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(img_tensor)
        probs = torch.softmax(logits, dim=1)
        pred_mask = probs.argmax(dim=1).squeeze().cpu().numpy()
        confidence = probs[0, 1].cpu().numpy()

    # 还原尺寸
    pred_pil = Image.fromarray((pred_mask * 255).astype(np.uint8))
    pred_pil = pred_pil.resize(orig_size, Image.NEAREST)
    pred_final = np.array(pred_pil) // 255

    conf_pil = Image.fromarray((confidence * 255).astype(np.uint8))
    conf_pil = conf_pil.resize(orig_size, Image.NEAREST)

    total_pixels = pred_final.size
    lesion_pixels = int(pred_final.sum())
    lesion_ratio = lesion_pixels / total_pixels

    return {
        'pred_mask': pred_final,
        'confidence_map': np.array(conf_pil),
        'lesion_pixels': lesion_pixels,
        'total_pixels': total_pixels,
        'lesion_ratio': lesion_ratio,
        'has_lesion': lesion_ratio > 0.01,
    }


def _create_overlay(orig_img: Image.Image, mask: np.ndarray) -> Image.Image:
    """创建原图+掩码叠加可视化"""
    orig_rgb = orig_img.convert('RGB')
    overlay = np.array(orig_rgb, dtype=np.float32)

    # 病变区域染红色
    red_overlay = np.zeros_like(overlay)
    red_overlay[:, :, 0] = 255  # R通道
    alpha = 0.4
    overlay[mask == 1] = (1 - alpha) * overlay[mask == 1] + alpha * red_overlay[mask == 1]

    return Image.fromarray(overlay.astype(np.uint8))


def _img_to_base64(img: Image.Image) -> str:
    """图像转Base64字符串"""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


if __name__ == '__main__':
    uvicorn.run(
        "inference_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
