const { request } = require('../../utils/request')
const { formatMsgTime } = require('../../utils/format') // 引入

Page({
  data: { conversations: [] },
  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 3 })
      this.getTabBar().getUnreadCount()
    }
    this.loadData() 
  },

  async loadData() {
    try {
      const res = await request({ url: '/api/messages/conversations' })
      // 给每条消息加上格式化后的时间
      const list = res.map(item => {
        return { ...item, timeText: formatMsgTime(item.time) }
      })
      this.setData({ conversations: list })
    } catch (e) {}
  },

  goToChat(e) {
    const { id, item, avatar } = e.currentTarget.dataset
    const safeAvatar = avatar ? encodeURIComponent(avatar) : ''
    wx.navigateTo({ url: `/pages/chat-room/chat-room?other_id=${id}&item_id=${item}&other_avatar=${safeAvatar}`})
  }
})