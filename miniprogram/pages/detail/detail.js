const { request } = require('../../utils/request')
const { formatTime } = require('../../utils/format')

Page({
  data: {
    item: null,
    timeText: '',
    matches: [],
    canClaim: false
  },

  onLoad(options) {
    if (options.id) this.loadDetail(options.id)
  },

  async loadDetail(id) {
    try {
      // 1. 获取详情
      const item = await request({ url: `/api/items/${id}` })
      this.setData({ 
        item, 
        timeText: formatTime(item.created_at) 
      })

      // 2. 判断是否可以认领（必须是招领、状态为0、且不是自己发布的）
      const currentUserId = getApp().globalData.userInfo?.id
      this.setData({
        canClaim: item.type === 1 && item.status === 0 && item.user_id !== currentUserId
      })

      this.setData({
        canContact: item.type === 0 && item.status === 0 && item.user_id !== currentUserId
      })
      
      // 3. 获取匹配结果
      const matches = await request({ url: `/api/matches/item/${id}` })
      this.setData({ matches })
      
    } catch (e) {
      console.error('加载详情失败', e)
    }
  },

  onPreview() {
    const { item } = this.data
    if (item && item.image_url) {
      wx.previewImage({ urls: [item.image_url] })
    }
  },

  onClose() {
    wx.showModal({
      title: '关闭信息',
      content: '确认物品已找回或已归还，关闭后不再展示？',
      success: async (res) => {
        if (!res.confirm) return
        try {
          await request({ url: `/api/items/${this.data.item.id}/close`, method: 'PATCH' })
          wx.showToast({ title: '已关闭', icon: 'success' })
          setTimeout(() => wx.navigateBack(), 600)
        } catch (e) {}
      }
    })
  },

  goToMatch(e) {
    const { lost, found } = e.currentTarget.dataset
    const currentId = this.data.item.id
    
    // 如果当前物品 ID 是丢失 ID，那目标就是招领 ID；反之亦然
    const targetId = currentId === lost ? found : lost
    
    if (targetId && targetId !== currentId) {
      wx.navigateTo({ url: `/pages/detail/detail?id=${targetId}` })
    } else {
      wx.showToast({ title: '无法找到对应物品', icon: 'none' })
    }
  },

  onClaim() {
    wx.showModal({
      title: '申请认领',
      editable: true,
      placeholderText: '请描述物品的隐藏特征（如密码、划痕等）',
      success: async (res) => {
        if (res.confirm && res.content) {
          try {
            await request({
              url: '/api/claims',
              method: 'POST',
              data: {
                item_id: this.data.item.id,
                answers: res.content
              }
            })
            wx.showToast({ title: '申请已提交', icon: 'success' })
            setTimeout(() => wx.navigateBack(), 600)
          } catch (e) {}
        }
      }
    })
  },

    //联系失主/拾主
    onContactOwner() {
      if (!getApp().globalData.userInfo) {
        wx.showToast({ title: '请先登录', icon: 'none' })
        setTimeout(() => wx.navigateTo({ url: '/pages/login/login' }), 800)
        return
      }
      
      // 跳转到聊天室，带上对方的 ID 和物品 ID
      const { item } = this.data
      wx.navigateTo({ 
        url: `/pages/chat-room/chat-room?other_id=${item.user_id}&item_id=${item.id}` 
      })
    }
})