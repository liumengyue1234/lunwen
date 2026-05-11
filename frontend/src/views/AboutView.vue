<template>
  <div class="about-page">
    <div class="page-header">
      <h2>关于系统</h2>
      <p class="subtitle">基于CT的松材线虫病检测系统 · 技术说明</p>
    </div>

    <el-row :gutter="24">
      <el-col :span="16">
        <el-card class="about-card">
          <template #header>项目概述</template>
          <div class="section">
            <p>
              本系统旨在开发一个基于CT影像的<strong>松材线虫病可视化检测系统</strong>，
              通过对松材CT图像进行去噪声处理、病变区域分割与标记，实现对松材线虫病的
              可视化检测与分析。
            </p>
            <p>
              系统引入深度学习与图像处理技术，对CT影像进行高效预处理，提取并标记松材
              线虫病相关特征，构建一套用于林业病害智能诊断的可视化系统。
            </p>
          </div>
          <el-divider />
          <div class="section">
            <h3>使用流程</h3>
            <el-steps :active="5" align-center style="margin-top: 20px;">
              <el-step title="上传影像" description="上传松材CT图像" />
              <el-step title="自动去噪" description="图像预处理增强" />
              <el-step title="深度分割" description="U-Net模型推理" />
              <el-step title="区域标记" description="病变区域可视化" />
              <el-step title="生成报告" description="输出分析结果" />
            </el-steps>
          </div>
          <el-divider />
          <div class="section">
            <h3>技术架构</h3>
            <el-table :data="techStack" style="margin-top: 12px;" border size="small">
              <el-table-column prop="layer" label="层次" width="100" />
              <el-table-column prop="tech" label="技术" width="200" />
              <el-table-column prop="desc" label="说明" />
            </el-table>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="model-card" style="margin-bottom: 16px;">
          <template #header>模型信息</template>
          <div class="model-info">
            <div class="info-item">
              <span class="info-label">模型架构</span>
              <el-tag>U-Net</el-tag>
            </div>
            <div class="info-item">
              <span class="info-label">框架</span>
              <el-tag type="warning">PyTorch 2.0+</el-tag>
            </div>
            <div class="info-item">
              <span class="info-label">输入通道</span>
              <span>1（灰度图）</span>
            </div>
            <div class="info-item">
              <span class="info-label">输出类别</span>
              <span>2（背景 / 病变）</span>
            </div>
            <div class="info-item">
              <span class="info-label">图像尺寸</span>
              <span>256 × 256</span>
            </div>
            <div class="info-item">
              <span class="info-label">损失函数</span>
              <span>Dice + BCE Loss</span>
            </div>
            <div class="info-item">
              <span class="info-label">优化器</span>
              <span>AdamW + CosineAnnealing</span>
            </div>
          </div>
        </el-card>

        <el-card class="project-card">
          <template #header>项目信息</template>
          <div class="project-info">
            <div class="info-item">
              <span class="info-label">项目名称</span>
              <span>松材线虫病CT检测系统</span>
            </div>
            <div class="info-item">
              <span class="info-label">学生姓名</span>
              <span>刘昕月</span>
            </div>
            <div class="info-item">
              <span class="info-label">专业班级</span>
              <span>软件工程 2022 级 4 班</span>
            </div>
            <div class="info-item">
              <span class="info-label">指导教师</span>
              <span>邱兆文 教授</span>
            </div>
            <div class="info-item">
              <span class="info-label">学院</span>
              <span>计算机与控制工程学院</span>
            </div>
            <div class="info-item">
              <span class="info-label">学校</span>
              <span>东北林业大学</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
const techStack = [
  { layer: '前端', tech: 'Vue 3 + Element Plus', desc: '响应式UI框架，组件化开发' },
  { layer: '后端', tech: 'Spring Boot 3 + MyBatis', desc: 'RESTful API，数据库访问层' },
  { layer: '数据库', tech: 'H2 / MySQL', desc: '存储检测记录与统计数据' },
  { layer: 'AI推理', tech: 'PyTorch + FastAPI', desc: 'U-Net模型推理HTTP服务' },
  { layer: '模型', tech: 'U-Net CNN', desc: '像素级图像分割，病变区域提取' },
  { layer: '图像处理', tech: 'OpenCV + PIL', desc: '去噪声、增强、可视化' },
]
</script>

<style scoped>
.about-page { max-width: 1200px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 24px; color: #1a2940; }
.subtitle { color: #666; margin-top: 4px; }

.about-card, .model-card, .project-card { border-radius: 12px; }

.section { margin: 8px 0; }
.section p { line-height: 1.8; color: #555; margin-bottom: 10px; }
.section h3 { font-size: 16px; color: #1a2940; margin-bottom: 8px; }

.model-info, .project-info { padding: 4px 0; }
.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
  font-size: 13px;
}
.info-item:last-child { border-bottom: none; }
.info-label { color: #666; flex-shrink: 0; }
</style>
