const { request, uploadImage } = require('../../utils/request')

Page({
  data: {
    user: null,
    isUploadingAvatar: false 
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 4 }) 
      this.getTabBar().getUnreadCount()
    }
    this.setData({ user: getApp().globalData.userInfo })
  },

  // 点击去登录/改昵称
  handleProfileTap() {
    if (!this.data.user) {
      // 跳转到登录页面
      wx.navigateTo({ url: '/pages/login/login' })
      return
    }
    this.onEditNickname()
  },

  // 点击头像：打开相册选图并上传
  async onChooseAvatar(e) {
    // 1. 如果没登录，先去登录页
    if (!this.data.user) {
      wx.navigateTo({ url: '/pages/login/login' })
      return
    }
    
    // 2. 防抖锁：如果正在上传，直接 return
    if (this.data.isUploadingAvatar) {
      wx.showToast({ title: '正在处理中...', icon: 'none' })
      return
    }

    // 3. 处理用户取消的情况
    const avatarUrl = e.detail.avatarUrl
    if (!avatarUrl) return

    this.setData({ isUploadingAvatar: true })
    wx.showLoading({ title: '上传中...', mask: true })
    
    try {
      let serverUrl = avatarUrl
      if (avatarUrl.startsWith('http://tmp') || avatarUrl.startsWith('wxfile://')) {
        serverUrl = await uploadImage(avatarUrl)
      }
      
      const updatedUser = await request({
        url: '/api/auth/profile',
        method: 'PATCH',
        data: { avatar_url: serverUrl }
      })
      
      getApp().globalData.userInfo = updatedUser
      this.setData({ user: updatedUser })
      wx.showToast({ title: '头像已更新', icon: 'success' })
    } catch (err) {
      wx.showToast({ title: '更新失败', icon: 'none' })
    } finally {
      wx.hideLoading() 
      this.setData({ isUploadingAvatar: false }) 
    }
  },

  // 微信官方：用户修改昵称
  async onChooseNickname(e) {
    // 1. 如果没登录，先去登录页
    if (!this.data.user) {
      wx.navigateTo({ url: '/pages/login/login' })
      return
    }
    
    const nickname = e.detail.value
    if (!nickname || nickname === this.data.user?.nickname) return

    try {
      const updatedUser = await request({
        url: '/api/auth/profile',
        method: 'PATCH',
        data: { nickname }
      })
      getApp().globalData.userInfo = updatedUser
      this.setData({ user: updatedUser })
      wx.showToast({ title: '昵称已更新', icon: 'success' })
    } catch (err) {}
  },

  // 菜单跳转
  goToMyItems() { wx.navigateTo({ url: '/pages/my-items/my-items' }) },
  goToClaims(e) {
    const type = e.currentTarget.dataset.type
    wx.navigateTo({ url: `/pages/my-claims/my-claims?type=${type}` })
  },
  goToSettings() { wx.navigateTo({ url: '/pages/settings/settings' }) }
})