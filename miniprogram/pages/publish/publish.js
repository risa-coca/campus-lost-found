const { request, uploadImage, compressImage } = require('../../utils/request')
const { CATEGORIES } = require('../../utils/format')

Page({
  data: {
    categories: CATEGORIES,
    type: 0,
    categoryIndex: 0,
    title: '',
    description: '',
    location: '',
    eventTime: '',
    imagePath: '',
    imageUrl: '',
    uploading: false,
    submitting: false
  },

  onTypeTap(e) {
    this.setData({ type: Number(e.currentTarget.dataset.type) })
  },

  onCategoryChange(e) {
    this.setData({ categoryIndex: Number(e.detail.value) })
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [field]: e.detail.value })
  },

  onTimeChange(e) {
    this.setData({ eventTime: e.detail.value })
  },

  async onChooseImage() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: async (res) => {
        let path = res.tempFiles[0].tempFilePath
        this.setData({ uploading: true })
        
        try {
          // 1. 压缩图片
          path = await compressImage(path)
          this.setData({ imagePath: path })
          
          // 2. 上传压缩后的图片
          const url = await uploadImage(path)
          this.setData({ imageUrl: url })
        } catch (e) {
          wx.showToast({ title: '图片处理失败', icon: 'none' })
          this.setData({ imagePath: '', imageUrl: '' })
        } finally {
          this.setData({ uploading: false })
        }
      }
    })
  },

  onRemoveImage() {
    this.setData({ imagePath: '', imageUrl: '' })
  },

  async onSubmit() {
    const { type, categoryIndex, categories, title, description, location, eventTime, imageUrl, submitting } = this.data
    if (submitting) return
    
    if (!title.trim()) return wx.showToast({ title: '请填写标题', icon: 'none' })
    if (!description.trim()) return wx.showToast({ title: '请填写描述', icon: 'none' })

    // 1. 整理要提交的数据
    const payloadData = {
      type,
      category: categories[categoryIndex],
      title: title.trim(),
      description: description.trim(),
      location: location.trim(),
      event_time: eventTime ? `${eventTime} 00:00:00` : null,
      image_url: imageUrl || null
    }

    // 2. 先请求订阅消息（必须在用户点击的同步调用栈中）
    wx.requestSubscribeMessage({
      tmplIds: ['u9xcCjPbEyFOpMSmaUGA-1Bs4s1GGGG5BXk7ajD9dFI'],
      complete: () => {
        // 无论用户同意还是拒绝，都继续提交数据
        this.doSubmit(payloadData)
      }
    })
  },

  async doSubmit(payloadData) {
    this.setData({ submitting: true })
    try {
      await request({
        url: '/api/items',
        method: 'POST',
        data: payloadData
      })
      
      wx.showToast({ title: '发布成功', icon: 'success' })
      
      // 重置表单
      this.setData({
        title: '', description: '', location: '', eventTime: '',
        imagePath: '', imageUrl: '', categoryIndex: 0
      })
      
      setTimeout(() => wx.switchTab({ url: '/pages/index/index' }), 800)
    } catch (e) {
      // 错误已在 request 中统一 toast
    } finally {
      this.setData({ submitting: false })
    }
  }
})