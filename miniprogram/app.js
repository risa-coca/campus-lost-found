const BASE_URL = 'http://127.0.0.1:8000'

App({
  globalData: {
    baseUrl: BASE_URL,
    userInfo: null
  },

  onLaunch() {
    // 如果用户之前主动退出了，就不再自动静默登录
    const isLogout = wx.getStorageSync('isLogout')
    if (!isLogout) {
      this.silentLogin()
    }
  },

  silentLogin() {
    return new Promise((resolve) => {
      wx.login({
        success: (res) => {
          if (!res.code) return resolve(null)
          wx.request({
            url: `${BASE_URL}/api/auth/login`,
            method: 'POST',
            data: { code: res.code },
            success: (r) => {
              if (r.statusCode === 200) {
                wx.setStorageSync('token', r.data.token)
                this.globalData.userInfo = r.data.user
                resolve(r.data.user)
              } else {
                resolve(null)
              }
            },
            fail: () => resolve(null)
          })
        },
        fail: () => resolve(null)
      })
    })
  }
})