const { request } = require('../../utils/request')

Page({
  data: {
    type: 'sent', // sent 或 received
    claims: [],
    loading: false
  },

  onLoad(options) {
    if (options.type) {
      this.setData({ type: options.type })
      wx.setNavigationBarTitle({
        title: options.type === 'sent' ? '我申请认领的' : '收到的认领申请'
      })
      this.loadData()
    }
  },

  async loadData() {
    this.setData({ loading: true })
    try {
      const url = this.data.type === 'sent' ? '/api/claims/sent' : '/api/claims/received'
      const res = await request({ url })
      this.setData({ claims: res })
    } catch (e) {} finally { this.setData({ loading: false }) }
  },

  async handleClaim(e) {
    const { id, action } = e.currentTarget.dataset
    try {
      await request({ url: `/api/claims/${id}/${action}`, method: 'POST' })
      wx.showToast({ title: action === 'approve' ? '已同意' : '已拒绝', icon: 'success' })
      this.loadData()
    } catch (e) {}
  },

  goToChatRoom(e) {
    const { other, item } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/chat-room/chat-room?other_id=${other}&item_id=${item}` })
  }
})