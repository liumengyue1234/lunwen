<template>
  <div class="dashboard">
    <div class="page-header">
      <h2>系统概览</h2>
      <p class="subtitle">松材线虫病CT影像智能检测平台 · 实时监控</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card total">
          <div class="stat-icon"><el-icon><DataAnalysis /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalDetections }}</div>
            <div class="stat-label">总检测次数</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card danger">
          <div class="stat-icon"><el-icon><Warning /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.positiveCases }}</div>
            <div class="stat-label">阳性病例</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card success">
          <div class="stat-icon"><el-icon><SuccessFilled /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.negativeCases }}</div>
            <div class="stat-label">阴性（健康）</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card info">
          <div class="stat-icon"><el-icon><Odometer /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ (stats.avgConfidence * 100).toFixed(1) }}%</div>
            <div class="stat-label">平均置信度</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>病例分布</template>
          <div class="pie-chart">
            <div v-if="stats.totalDetections === 0" class="no-data">
              <el-icon><PieChart /></el-icon>
              <p>暂无数据，请先进行CT影像检测</p>
            </div>
            <div v-else>
              <!-- 简单饼图展示 -->
              <div class="simple-pie">
                <div class="pie-item positive">
                  <span class="dot red"></span>
                  <span>阳性病例：{{ stats.positiveCases }} 例 ({{ positiveRate }}%)</span>
                </div>
                <div class="pie-item negative">
                  <span class="dot green"></span>
                  <span>阴性病例：{{ stats.negativeCases }} 例 ({{ negativeRate }}%)</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>快速操作</template>
          <div class="quick-actions">
            <el-button type="primary" size="large" @click="$router.push('/detect')">
              <el-icon><Upload /></el-icon> 上传CT影像检测
            </el-button>
            <el-button size="large" @click="$router.push('/history')">
              <el-icon><List /></el-icon> 查看检测历史
            </el-button>
          </div>
          <el-divider />
          <div class="system-info">
            <div class="info-row">
              <span class="label">模型架构：</span>
              <el-tag size="small">U-Net (PyTorch)</el-tag>
            </div>
            <div class="info-row">
              <span class="label">后端服务：</span>
              <el-tag size="small" type="success">Spring Boot 3.2</el-tag>
            </div>
            <div class="info-row">
              <span class="label">前端框架：</span>
              <el-tag size="small" type="warning">Vue 3 + Element Plus</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统说明 -->
    <el-card class="intro-card">
      <template #header>系统简介</template>
      <el-row :gutter="24">
        <el-col :span="8">
          <div class="feature-item">
            <el-icon size="32" color="#409EFF"><Monitor /></el-icon>
            <h3>CT影像处理</h3>
            <p>自动对松材CT图像进行去噪声预处理，增强病变区域特征，为分割提供高质量输入。</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="feature-item">
            <el-icon size="32" color="#67C23A"><Crop /></el-icon>
            <h3>深度学习分割</h3>
            <p>采用U-Net卷积神经网络，对松材线虫病变区域进行精准像素级分割与标记。</p>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="feature-item">
            <el-icon size="32" color="#E6A23C"><DataAnalysis /></el-icon>
            <h3>可视化报告</h3>
            <p>生成直观的病害分析报告，包含分割结果叠加图、病变面积比例等详细数据。</p>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getStats } from '@/api/detection'

const stats = ref({
  totalDetections: 0,
  positiveCases: 0,
  negativeCases: 0,
  positiveRate: 0,
  avgConfidence: 0
})

const positiveRate = computed(() =>
  stats.value.totalDetections > 0
    ? ((stats.value.positiveCases / stats.value.totalDetections) * 100).toFixed(1)
    : 0
)
const negativeRate = computed(() =>
  stats.value.totalDetections > 0
    ? ((stats.value.negativeCases / stats.value.totalDetections) * 100).toFixed(1)
    : 0
)

onMounted(async () => {
  try {
    const res = await getStats()
    if (res.success) {
      stats.value = res.data
    }
  } catch (e) {
    // 服务未启动时使用默认值
  }
})
</script>

<style scoped>
.dashboard { max-width: 1200px; }

.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 24px; color: #1a2940; }
.subtitle { color: #666; margin-top: 4px; }

.stats-row { margin-bottom: 24px; }

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  color: white;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.stat-card.total { background: linear-gradient(135deg, #1a73e8, #0d47a1); }
.stat-card.danger { background: linear-gradient(135deg, #e53935, #b71c1c); }
.stat-card.success { background: linear-gradient(135deg, #43a047, #1b5e20); }
.stat-card.info { background: linear-gradient(135deg, #0288d1, #01579b); }

.stat-icon { font-size: 36px; opacity: 0.9; }
.stat-value { font-size: 32px; font-weight: 700; }
.stat-label { font-size: 13px; opacity: 0.85; margin-top: 4px; }

.chart-row { margin-bottom: 24px; }
.chart-card { border-radius: 12px; }

.no-data {
  text-align: center;
  padding: 40px;
  color: #999;
}
.no-data .el-icon { font-size: 48px; margin-bottom: 12px; }

.simple-pie { padding: 20px; }
.pie-item { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; font-size: 15px; }
.dot { width: 14px; height: 14px; border-radius: 50%; flex-shrink: 0; }
.dot.red { background: #e53935; }
.dot.green { background: #43a047; }

.quick-actions {
  display: flex;
  gap: 16px;
  padding: 8px 0;
  flex-wrap: wrap;
}

.system-info { padding-top: 8px; }
.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.label { color: #666; min-width: 80px; }

.intro-card { border-radius: 12px; }
.feature-item {
  text-align: center;
  padding: 24px 16px;
}
.feature-item h3 { margin: 12px 0 8px; color: #1a2940; }
.feature-item p { color: #666; font-size: 14px; line-height: 1.7; }
</style>
