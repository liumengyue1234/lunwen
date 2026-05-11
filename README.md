# 松材线虫病CT检测系统

> 基于CT的松材线虫病检测系统 | 东北林业大学 软件工程 2022级4班 刘昕月

## 项目简介

本系统基于深度学习技术，对松材CT图像进行病变区域自动分割与可视化标记，辅助林业工作者快速诊断松材线虫病。

**核心功能：**
- 🌲 CT影像上传与自动去噪声处理
- 🤖 U-Net深度学习模型病变区域分割
- 📊 病变面积、置信度等指标可视化
- 📋 检测记录管理与历史查询
- 📈 系统统计面板

## 技术架构

```
pine-wilt-detection/
├── model/              # Python深度学习模块（PyTorch）
│   ├── unet.py             # U-Net模型定义
│   ├── dataset.py          # 数据集加载器
│   ├── loss.py             # 损失函数（Dice + BCE）
│   ├── metrics.py          # 评估指标（Dice/IoU/Precision/Recall）
│   ├── train.py            # 模型训练脚本
│   ├── evaluate.py         # 模型评估脚本
│   ├── inference_server.py # FastAPI推理服务
│   └── requirements.txt    # Python依赖
│
├── backend/            # Java后端（Spring Boot 3 + MyBatis）
│   ├── pom.xml
│   └── src/main/
│       ├── java/com/pinewilt/detection/
│       │   ├── controller/     # REST API控制器
│       │   ├── service/        # 业务逻辑层
│       │   ├── mapper/         # MyBatis数据访问层
│       │   ├── entity/         # 实体类
│       │   └── config/         # 配置类（CORS、文件上传等）
│       └── resources/
│           ├── application.yml # 配置文件
│           ├── schema.sql      # 数据库建表脚本
│           └── data.sql        # 初始数据
│
└── frontend/           # Vue3前端（Element Plus）
    ├── src/
    │   ├── views/          # 页面视图
    │   ├── components/     # 公共组件
    │   ├── api/            # API调用封装
    │   ├── router/         # 路由配置
    │   └── stores/         # Pinia状态管理
    ├── package.json
    └── vite.config.js
```

## 快速开始

### 环境要求

| 组件 | 版本要求 |
|------|---------|
| Python | 3.9+ |
| Java (JDK) | 17+ |
| Node.js | 18+ |
| Maven | 3.8+ |

### 1. 启动Python推理服务

```bash
cd model

# 安装依赖
pip install -r requirements.txt

# 训练模型（可选，没有数据集时会使用模拟数据）
python train.py --epochs 50 --batch_size 8

# 评估模型
python evaluate.py

# 启动推理API服务（端口8000）
python inference_server.py
```

### 2. 启动Spring Boot后端

```bash
cd backend

# 编译并运行（端口8080）
mvn spring-boot:run
```

> 默认使用H2内存数据库，无需安装MySQL。  
> H2控制台访问地址：http://localhost:8080/api/h2-console  
> （JDBC URL: `jdbc:h2:mem:pinewiltdb`，用户名: `sa`，密码为空）

### 3. 启动Vue3前端

```bash
cd frontend

# 安装依赖
npm install

# 开发模式运行（端口3000）
npm run dev

# 生产构建
npm run build
```

### 4. 访问系统

打开浏览器访问：**http://localhost:3000**

## API文档

### 后端接口（Spring Boot，端口8080）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/detection/upload` | POST | 上传CT图像进行检测 |
| `/api/detection/history` | GET | 获取检测历史记录 |
| `/api/detection/{id}` | GET | 获取单条检测记录 |
| `/api/detection/stats` | GET | 获取系统统计信息 |
| `/api/detection/health` | GET | 健康检查 |

### 推理服务接口（FastAPI，端口8000）

| 接口 | 方法 | 说明 |
|------|------|------|
| `/predict` | POST | 上传CT图像，返回分割结果 |
| `/health` | GET | 健康检查 |
| `/docs` | GET | 自动生成的API文档 |

## 数据集准备

将CT图像放置在以下目录结构中：

```
model/data/
├── train/
│   ├── images/    # 训练CT图像 (.png/.jpg/.tif)
│   └── masks/     # 对应的标注掩码（白色=病变区域，黑色=背景）
└── val/
    ├── images/    # 验证CT图像
    └── masks/     # 对应的标注掩码
```

> 如果没有数据集，系统会自动使用模拟数据进行演示。

## 模型训练参数说明

```bash
python train.py \
  --data_dir ./data \        # 数据集目录
  --epochs 50 \              # 训练轮数
  --batch_size 8 \           # 批量大小
  --lr 1e-4 \                # 学习率
  --img_size 256 \           # 图像尺寸
  --save_dir ./checkpoints   # 模型保存目录
```

## 评估指标

训练完成后会输出以下评估指标：

| 指标 | 说明 |
|------|------|
| Dice系数 | 分割区域重叠程度，越高越好（理想值 > 0.85） |
| IoU | 交并比，越高越好（理想值 > 0.75） |
| 精确率 | 减少误报（假阳性） |
| 召回率 | 减少漏报（假阴性） |
| 像素准确率 | 正确分类像素占比 |

## 开发信息

- **学生：** 刘昕月（2022222997）
- **班级：** 软件工程 2022 级 4 班
- **指导教师：** 邱兆文 教授 / 高启 工程师
- **学院：** 计算机与控制工程学院
- **学校：** 东北林业大学

## 许可证

本项目仅用于学术毕业设计，不得用于商业用途。
