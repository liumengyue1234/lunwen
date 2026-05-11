<template>
  <div class="history-page">
    <div class="page-header">
      <h2>检测历史记录</h2>
      <p class="subtitle">查看所有CT影像检测记录与分析结果</p>
    </div>

    <el-card class="table-card">
      <el-table
        :data="records"
        v-loading="loading"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="filename" label="文件名" min-width="160" show-overflow-tooltip />
        <el-table-column label="检测结论" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="row.hasLesion ? 'danger' : 'success'" size="small">
              {{ row.hasLesion ? '⚠ 阳性' : '✓ 阴性' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="病变面积比" width="120" align="center">
          <template #default="{ row }">
            <span :class="row.hasLesion ? 'danger-text' : ''">
              {{ (row.lesionRatio * 100).toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="置信度" width="100" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="Math.round(row.confidence * 100)"
              :color="row.confidence > 0.8 ? '#67c23a' : '#e6a23c'"
              :stroke-width="8"
              :show-text="false"
            />
            <span style="font-size:12px">{{ (row.confidence * 100).toFixed(1) }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'SUCCESS' ? 'success' : row.status === 'PENDING' ? 'warning' : 'danger'"
              size="small"
            >
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="检测时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="检测详情" width="600px">
      <div v-if="selectedRecord" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ selectedRecord.id }}</el-descriptions-item>
          <el-descriptions-item label="文件名">{{ selectedRecord.filename }}</el-descriptions-item>
          <el-descriptions-item label="诊断结论">
            <el-tag :type="selectedRecord.hasLesion ? 'danger' : 'success'">
              {{ selectedRecord.hasLesion ? '阳性（检测到病变）' : '阴性（未见异常）' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="病变面积比">
            {{ (selectedRecord.lesionRatio * 100).toFixed(4) }}%
          </el-descriptions-item>
          <el-descriptions-item label="病变像素数">
            {{ selectedRecord.lesionPixels?.toLocaleString() }}
          </el-descriptions-item>
          <el-descriptions-item label="总像素数">
            {{ selectedRecord.totalPixels?.toLocaleString() }}
          </el-descriptions-item>
          <el-descriptions-item label="置信度">
            {{ (selectedRecord.confidence * 100).toFixed(2) }}%
          </el-descriptions-item>
          <el-descriptions-item label="处理状态">
            <el-tag :type="selectedRecord.status === 'SUCCESS' ? 'success' : 'danger'" size="small">
              {{ selectedRecord.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="检测时间" :span="2">
            {{ formatDate(selectedRecord.createdAt) }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedRecord.overlayPath" class="overlay-preview">
          <h4>病变区域叠加图</h4>
          <img :src="selectedRecord.overlayPath" alt="叠加图" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getHistory } from '@/api/detection'

const records = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const detailVisible = ref(false)
const selectedRecord = ref(null)

async function loadData() {
  loading.value = true
  try {
    const res = await getHistory(currentPage.value, pageSize.value)
    if (res.success) {
      records.value = res.data.records || []
      total.value = res.data.total || 0
    }
  } catch (e) {
    records.value = []
  } finally {
    loading.value = false
  }
}

function viewDetail(row) {
  selectedRecord.value = row
  detailVisible.value = true
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(loadData)
</script>

<style scoped>
.history-page { max-width: 1200px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 24px; color: #1a2940; }
.subtitle { color: #666; margin-top: 4px; }
.table-card { border-radius: 12px; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
.danger-text { color: #e53935; font-weight: 600; }
.detail-content { padding: 4px; }
.overlay-preview { margin-top: 16px; }
.overlay-preview h4 { margin-bottom: 8px; color: #666; }
.overlay-preview img { width: 100%; border-radius: 8px; border: 1px solid #eee; }
</style>
