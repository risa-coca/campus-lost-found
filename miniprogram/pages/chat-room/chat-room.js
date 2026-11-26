const { request, uploadImage } = require('../../utils/request')

Page({
  data: {
    otherId: null,
    itemId: null,
    messages: [],
    inputValue: '',
    myId: null,
    myAvatar: '',    
    otherAvatar: '',
    showEmoji: false,
    emojis: ['😀', '😂', '😊', '😍', '🤔', '😎', '😭', '😡', '👍', '👎', '❤️', '🎉', '🔥', '🌟', '📍', '🤝'] 
  },
  onLoad(options) {
    const myInfo = getApp().globalData.userInfo
    const myAvatar = myInfo?.avatar_url || ''
    
    let otherAvatar = ''
    if (options.other_avatar) {
      otherAvatar = decodeURIComponent(options.other_avatar)
    }

    this.setData({ 
      otherId: Number(options.other_id), 
      itemId: Number(options.item_id),
      myId: getApp().globalData.userInfo?.id,
      myAvatar: myAvatar,
      otherAvatar: otherAvatar
    })
    this.loadHistory()
    // 3秒轮询新消息
    this.timer = setInterval(() => this.loadHistory(), 3000)
  },
  onUnload() { 
    if(this.timer) clearInterval(this.timer)  
  },
  async loadHistory() {
    try {
      const res = await request({ 
        url: `/api/messages/history?receiver_id=${this.data.otherId}&item_id=${this.data.itemId}` 
      })
       
       //提前判断是否是图片
       const formattedMsgs = res.map(m => {
        const content = (m.content || '').trim()
        const isImage = content && (
          content.endsWith('.png') || 
          content.endsWith('.jpg') || 
          content.endsWith('.jpeg') || 
          content.indexOf('uploads/') !== -1
        );
        return { ...m, is_image: isImage, content: content }
      })
      
      // 🔥 核心修复：这里必须传入 formattedMsgs，而不是 res
      this.setData({ messages: formattedMsgs }, () => {
        wx.pageScrollTo({ scrollTop: 99999, duration: 0 })
      })
    } catch(e) {}
  },
   // 切换表情面板
   toggleEmoji() {
    this.setData({ showEmoji: !this.data.showEmoji })
  },

  // 选择表情
  onSelectEmoji(e) {
    const emoji = e.currentTarget.dataset.emoji
    this.setData({ 
      inputValue: this.data.inputValue + emoji 
    })
  },

  //发送图片
  onChooseImage() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sizeType: ['compressed'],
      success: async (res) => {
        const tempPath = res.tempFiles[0].tempFilePath
        wx.showLoading({ title: '发送中...', mask: true })
        
        try {
          const serverUrl = await uploadImage(tempPath)
          
          await request({
            url: '/api/messages',
            method: 'POST',
            data: { 
              receiver_id: this.data.otherId, 
              item_id: this.data.itemId, 
              content: serverUrl 
            }
          })
          
          this.loadHistory()
        } catch (e) {
          wx.showToast({ title: '发送失败', icon: 'none' })
        } finally {
          wx.hideLoading()
        }
      }
    })
  },

  // 点击放大图片
  previewImage(e) {
    const url = e.currentTarget.dataset.url
    wx.previewImage({
      urls: [url]
    })
  },

  onInput(e) { this.setData({ inputValue: e.detail.value }) },
  
  async onSend() {
    const content = this.data.inputValue.trim()
    if (!content) return
    this.setData({ inputValue: '' })
    try {
      await request({
        url: '/api/messages',
        method: 'POST',
        data: { receiver_id: this.data.otherId, item_id: this.data.itemId, content }
      })
      this.loadHistory()
    } catch(e) {}
  }
})