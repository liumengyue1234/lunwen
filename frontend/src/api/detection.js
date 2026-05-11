import request from './request'

/**
 * 上传CT图像进行检测
 */
export function uploadDetect(formData) {
  return request.post('/detection/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000
  })
}

/**
 * 获取检测历史
 */
export function getHistory(page = 1, pageSize = 10) {
  return request.get('/detection/history', { params: { page, pageSize } })
}

/**
 * 获取单条记录
 */
export function getRecord(id) {
  return request.get(`/detection/${id}`)
}

/**
 * 获取统计信息
 */
export function getStats() {
  return request.get('/detection/stats')
}
