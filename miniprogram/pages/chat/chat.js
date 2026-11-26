const { request, uploadImage } = require('../../utils/request')

Page({
  data: {
    messages: [
      { role: 'ai', content: '你好！我是校园寻物助手。你可以直接问我：“昨天在图书馆丢的黑色耳机有线索吗？”，或者发一张物品的照片给我。' }
    ],
    inputValue: '',
    loading: false,
    myAvatar: '',
    lastUserId: null
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 1 }) 
      this.getTabBar().getUnreadCount()
    }
    const userInfo = getApp().globalData.userInfo
    const currentUserId = userInfo ? userInfo.id : null

    if (currentUserId !== this.data.lastUserId) {
      // 如果账号变了，重置聊天记录
      this.setData({
        lastUserId: currentUserId,
        messages: [
          { role: 'ai', content: '你好！我是校园寻物助手。你可以直接问我：“昨天在图书馆丢的黑色耳机有线索吗？”，或者发一张物品的照片给我。' }
        ]
      })
    }

    if (userInfo && userInfo.avatar_url) {
      this.setData({ myAvatar: userInfo.avatar_url })
    }
  },

  onInput(e) {
    this.setData({ inputValue: e.detail.value })
  },

  // 🔥 发送文字
  async onSend() {
    const q = this.data.inputValue.trim()
    if (!q || this.data.loading) return

    const msgs = this.data.messages.concat({ role: 'user', content: q })
    this.setData({ messages: msgs, inputValue: '', loading: true })

    try {
      const res = await request({ url: '/api/chat', method: 'POST', data: { query: q } })
     
      this.setData({
        messages: this.data.messages.concat({ 
          role: 'ai', 
          content: res.reply,
          matches: res.matches || [] 
        })
      })
    } catch (e) {
      this.setData({
        messages: this.data.messages.concat({ role: 'ai', content: '抱歉，网络异常或 AI 离线了，请稍后再试。' })
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 🔥 发送图片
  onChooseImage() {
    if (this.data.loading) return
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sizeType: ['compressed'],
      success: async (res) => {
        const tempPath = res.tempFiles[0].tempFilePath
        wx.showLoading({ title: '上传中...', mask: true })
        
        try {
          const serverUrl = await uploadImage(tempPath)
          
          // 1. 把图片显示在聊天框
          const msgs = this.data.messages.concat({ 
            role: 'user', 
            content: serverUrl, 
            is_image: true 
          })
          this.setData({ messages: msgs, loading: true })
          
          // 2. 发送给后端让 AI 匹配
          const aiRes = await request({ 
            url: '/api/chat', 
            method: 'POST', 
            data: { query: '请帮我找找图片里的东西有没有线索', image_url: serverUrl } 
          })
          
          // 3. 接收 AI 回复
           this.setData({
            messages: this.data.messages.concat({ 
              role: 'ai', 
              content: aiRes.reply,
              matches: aiRes.matches || []
            })
          })
          
        } catch (e) {
          wx.showToast({ title: '发送失败', icon: 'none' })
        } finally {
          wx.hideLoading()
          this.setData({ loading: false })
        }
      }
    })
  },

   goToDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/detail/detail?id=${id}` })
  },

  // 🔥 预览图片
  previewImage(e) {
    const url = e.currentTarget.dataset.url
    wx.previewImage({ urls: [url] })
  }
})