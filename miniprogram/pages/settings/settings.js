Page({
  onLogout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出当前账号吗？',
      success: (res) => {
        if (res.confirm) {
          // 1. 清除 Token
          wx.removeStorageSync('token')
          // 2. 写入主动退出标记，防止自动登录
          wx.setStorageSync('isLogout', true) 
          // 3. 清空全局用户信息
          getApp().globalData.userInfo = null
          
          wx.showToast({ title: '已退出', icon: 'success' })
          setTimeout(() => {
            // 跳回首页
            wx.switchTab({ url: '/pages/index/index' })
          }, 800)
        }
      }
    })
  },
  
  clearCache() {
    wx.showToast({ title: '缓存已清理', icon: 'success' })
  },
  
  about() {
    wx.showModal({
      title: '关于拾光校园',
      content: '一款基于AI大模型的校园失物招领系统 v1.0.0',
      showCancel: false
    })
  }
})