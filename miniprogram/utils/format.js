function formatTime(value) {
  if (!value) return ''
  const d = new Date(value.replace(/-/g, '/'))
  if (isNaN(d.getTime())) return value
  const now = new Date()
  const diff = (now - d) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  if (diff < 86400 * 7) return `${Math.floor(diff / 86400)} 天前`
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${mm}-${dd}`
}

const CATEGORIES = ['证件', '电子产品', '钥匙', '书籍', '衣物', '其他']

function formatMsgTime(timeStr) {
  if (!timeStr) return ''
  
  let safeTimeStr = timeStr.replace('T', ' ').replace(/-/g, '/')
  
  // 如果带有毫秒或时区，截断它
  if (safeTimeStr.includes('.')) {
    safeTimeStr = safeTimeStr.split('.')[0]
  }
  if (safeTimeStr.includes('Z')) {
    safeTimeStr = safeTimeStr.replace('Z', '')
  }

  const d = new Date(safeTimeStr)
  
  // 如果解析失败，直接返回原字符串，防止报错
  if (isNaN(d.getTime())) {
    return timeStr.substring(5, 16) // 简单兜底，取 MM-DD HH:mm
  }

  const now = new Date()
  
  // 如果是今天，显示 HH:mm
  if (d.toDateString() === now.toDateString()) {
    const h = String(d.getHours()).padStart(2, '0')
    const m = String(d.getMinutes()).padStart(2, '0')
    return `${h}:${m}`
  }
  
  // 如果是昨天
  const yesterday = new Date(now)
  yesterday.setDate(now.getDate() - 1)
  if (d.toDateString() === yesterday.toDateString()) {
    return '昨天'
  }
  
  // 更早的显示 MM-DD
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${mm}-${dd}`
}

module.exports = { formatTime, CATEGORIES, formatMsgTime } 