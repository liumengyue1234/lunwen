<template>
  <div class="detect-page">
    <div class="page-header">
      <h2>CT影像检测</h2>
      <p class="subtitle">上传松材CT图像，系统将自动完成去噪声、分割与病变标记</p>
    </div>

    <el-row :gutter="24">
      <!-- 左侧：上传区域 -->
      <el-col :span="10">
        <el-card class="upload-card">
          <template #header>
            <span>上传CT影像</span>
          </template>

          <el-upload
            ref="uploadRef"
            class="ct-uploader"
            drag
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleFileChange"
            accept="image/*"
          >
            <div v-if="!previewUrl" class="upload-placeholder">
              <el-icon size="60" color="#409EFF"><UploadFilled /></el-icon>
              <p class="upload-text">拖拽CT图像到此处</p>
              <p class="upload-hint">或 <em>点击上传</em></p>
              <p class="upload-hint">支持 PNG / JPEG / TIFF / BMP 格式</p>
            </div>
            <div v-else class="preview-container">
              <img :src="previewUrl" alt="CT影像预览" class="preview-img" />
              <div class="preview-overlay">
                <span>{{ selectedFile?.name }}</span>
              </div>
            </div>
          </el-upload>

          <div v-if="selectedFile" class="file-info">
            <el-tag>{{ selectedFile.name }}</el-tag>
            <el-tag type="info">{{ formatSize(selectedFile.size) }}</el-tag>
          </div>

          <div class="btn-row">
            <el-button
              type="primary"
              size="large"
              :loading="detecting"
              :disabled="!selectedFile"
              @click="startDetect"
            >
              <el-icon><Search /></el-icon>
              {{ detecting ? '检测中...' : '开始检测' }}
            </el-button>
            <el-button size="large" @click="clearFile">清除</el-button>
          </div>

          <!-- 进度条 -->
          <el-progress
            v-if="detecting"
            :percentage="progress"
            :status="progress === 100 ? 'success' : undefined"
            class="progress"
            striped
            striped-flow
          />
        </el-card>
      </el-col>

      <!-- 右侧：检测结果 -->
      <el-col :span="14">
        <el-card class="result-card">
          <template #header>
            <span>检测结果</span>
            <el-tag v-if="result" :type="result.data?.hasLesion ? 'danger' : 'success'" class="result-tag">
              {{ result.data?.hasLesion ? '⚠ 检测到病变' : '✓ 未见异常' }}
            </el-tag>
          </template>

          <!-- 空状态 -->
          <div v-if="!result" class="empty-result">
            <el-icon size="64" color="#ddd"><PictureFilled /></el-icon>
            <p>上传CT影像后，检测结果将在这里展示</p>
          </div>

          <!-- 结果展示 -->
          <div v-else class="result-content">
            <!-- 指标卡片 -->
            <el-row :gutter="12" class="metrics">
              <el-col :span="8">
                <div class="metric-card" :class="result.data?.hasLesion ? 'red' : 'green'">
                  <div class="metric-val">{{ result.data?.hasLesion ? '阳性' : '阴性' }}</div>
                  <div class="metric-name">诊断结论</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="metric-card blue">
                  <div class="metric-val">{{ (result.data?.lesionRatio * 100).toFixed(2) }}%</div>
                  <div class="metric-name">病变面积比</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="metric-card purple">
                  <div class="metric-val">{{ (result.data?.confidence * 100).toFixed(1) }}%</div>
                  <div class="metric-name">检测置信度</div>
                </div>
              </el-col>
            </el-row>

            <!-- 图像对比 -->
            <div class="image-compare">
              <div class="img-item">
                <h4>原始CT影像</h4>
                <img v-if="previewUrl" :src="previewUrl" alt="原图" />
              </div>
              <div class="img-item">
                <h4>病变区域叠加图</h4>
                <img
                  v-if="result.data?.overlayPath"
                  :src="result.data.overlayPath"
                  alt="叠加图"
                />
                <img
                  v-else-if="overlayDataUrl"
                  :src="overlayDataUrl"
                  alt="叠加图"
                />
                <div v-else class="img-placeholder">图像处理中...</div>
              </div>
            </div>

            <!-- 详细信息 -->
            <el-descriptions :column="2" border size="small" class="details">
              <el-descriptions-item label="检测ID">{{ result.data?.id }}</el-descriptions-item>
              <el-descriptions-item label="文件名">{{ result.data?.filename }}</el-descriptions-item>
              <el-descriptions-item label="病变像素">{{ result.data?.lesionPixels?.toLocaleString() }}</el-descriptions-item>
              <el-descriptions-item label="总像素">{{ result.data?.totalPixels?.toLocaleString() }}</el-descriptions-item>
              <el-descriptions-item label="处理状态">
                <el-tag :type="result.data?.status === 'SUCCESS' ? 'success' : 'danger'" size="small">
                  {{ result.data?.status }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="诊断建议">
                {{ result.data?.hasLesion ? '建议进一步人工核查，及时采取防治措施' : '影像未见明显病变，继续定期监测' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { uploadDetect } from '@/api/detection'

const uploadRef = ref()
const selectedFile = ref(null)
const previewUrl = ref(null)
const detecting = ref(false)
const progress = ref(0)
const result = ref(null)
const overlayDataUrl = ref(null)

function handleFileChange(file) {
  selectedFile.value = file.raw
  previewUrl.value = URL.createObjectURL(file.raw)
  result.value = null
  overlayDataUrl.value = null
}

function clearFile() {
  selectedFile.value = null
  previewUrl.value = null
  result.value = null
  overlayDataUrl.value = null
  progress.value = 0
}

async function startDetect() {
  if (!selectedFile.value) return
  detecting.value = true
  progress.value = 0
  result.value = null

  // 模拟进度
  const timer = setInterval(() => {
    if (progress.value < 90) progress.value += 10
  }, 300)

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    const res = await uploadDetect(formData)
    progress.value = 100
    result.value = res
    ElMessage.success('检测完成！')
  } catch (e) {
    ElMessage.error('检测失败，请确认后端服务已启动')
    progress.value = 0
  } finally {
    clearInterval(timer)
    detecting.value = false
  }
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}
</script>

<style scoped>
.detect-page { max-width: 1200px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 24px; color: #1a2940; }
.subtitle { color: #666; margin-top: 4px; }

.upload-card, .result-card { border-radius: 12px; min-height: 500px; }

.ct-uploader { width: 100%; }
.ct-uploader :deep(.el-upload), .ct-uploader :deep(.el-upload-dragger) { width: 100%; }

.upload-placeholder {
  padding: 40px 20px;
  text-align: center;
}
.upload-text { font-size: 16px; color: #333; margin: 12px 0 6px; }
.upload-hint { font-size: 13px; color: #999; }
.upload-hint em { color: #409EFF; }

.preview-container { position: relative; padding: 8px; }
.preview-img { width: 100%; max-height: 260px; object-fit: contain; border-radius: 8px; }
.preview-overlay {
  position: absolute;
  bottom: 12px;
  left: 12px;
  right: 12px;
  background: rgba(0,0,0,0.5);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.file-info { display: flex; gap: 8px; margin: 12px 0; flex-wrap: wrap; }
.btn-row { display: flex; gap: 12px; margin-top: 16px; }
.progress { margin-top: 16px; }

.result-tag { margin-left: 12px; }

.empty-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: #ccc;
  gap: 16px;
}

.result-content { padding: 4px; }

.metrics { margin-bottom: 16px; }
.metric-card {
  text-align: center;
  padding: 16px;
  border-radius: 8px;
  color: white;
}
.metric-card.red { background: linear-gradient(135deg, #e53935, #c62828); }
.metric-card.green { background: linear-gradient(135deg, #43a047, #2e7d32); }
.metric-card.blue { background: linear-gradient(135deg, #1e88e5, #1565c0); }
.metric-card.purple { background: linear-gradient(135deg, #8e24aa, #6a1b9a); }
.metric-val { font-size: 22px; font-weight: 700; }
.metric-name { font-size: 12px; margin-top: 4px; opacity: 0.9; }

.image-compare {
  display: flex;
  gap: 12px;
  margin: 16px 0;
}
.img-item { flex: 1; }
.img-item h4 { font-size: 13px; color: #666; margin-bottom: 8px; }
.img-item img {
  width: 100%;
  max-height: 200px;
  object-fit: contain;
  border: 1px solid #eee;
  border-radius: 8px;
  background: #f5f5f5;
}
.img-placeholder {
  width: 100%;
  height: 180px;
  background: #f5f5f5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

.details { margin-top: 12px; }
</style>
