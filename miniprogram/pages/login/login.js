const { request } = require('../../utils/request')

Page({
  data: {
    mode: 'login', // 'login' 或 'register'
    username: '',
    password: '',
    nickname: '',
    loading: false
  },

  switchMode(e) {
    this.setData({ mode: e.currentTarget.dataset.mode })
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [field]: e.detail.value })
  },

  // 账号密码登录
  async onAccountLogin() {
    const { username, password } = this.data
    if (!username || !password) return wx.showToast({ title: '请填写账号密码', icon: 'none' })

    this.setData({ loading: true })
    try {
      const res = await request({
        url: '/api/auth/account_login',
        method: 'POST',
        data: { username, password }
      })
      this.handleLoginSuccess(res)
    } catch (e) {} finally {
      this.setData({ loading: false })
    }
  },

  // 注册
  async onRegister() {
    const { username, password, nickname } = this.data
    if (!username || !password || !nickname) return wx.showToast({ title: '请填写完整信息', icon: 'none' })

    this.setData({ loading: true })
    try {
      const res = await request({
        url: '/api/auth/register',
        method: 'POST',
        data: { username, password, nickname }
      })
      wx.showToast({ title: '注册成功', icon: 'success' })
      this.handleLoginSuccess(res)
    } catch (e) {} finally {
      this.setData({ loading: false })
    }
  },

  // 微信授权登录（复用之前的静默登录）
  async onWxLogin() {
    this.setData({ loading: true })
    try {
      wx.removeStorageSync('isLogout')
      const user = await getApp().silentLogin()
      if (user) {
        wx.showToast({ title: '登录成功', icon: 'success' })
        setTimeout(() => wx.navigateBack(), 600)
      } else {
        wx.showToast({ title: '登录失败', icon: 'none' })
      }
    } catch (e) {
      wx.showToast({ title: '登录异常', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  handleLoginSuccess(res) {
    wx.setStorageSync('token', res.token)
    getApp().globalData.userInfo = res.user
    setTimeout(() => wx.navigateBack(), 600)
  }
})