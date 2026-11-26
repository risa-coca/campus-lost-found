function request({ url, method = 'GET', data = {}, header = {} }) {
  const BASE_URL = getApp().globalData.baseUrl
  const token = wx.getStorageSync('token')

  return new Promise((resolve, reject) => {
    wx.request({
      url: BASE_URL + url,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...header
      },
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          wx.removeStorageSync('token')
          getApp().silentLogin()
          reject(new Error('未登录'))
        } else {
          const msg = (res.data && res.data.detail) || '请求失败'
          wx.showToast({ title: String(msg), icon: 'none' })
          reject(new Error(msg))
        }
      },
      fail(err) {
        wx.showToast({ title: '网络异常', icon: 'none' })
        reject(err)
      }
    })
  })
}

function uploadImage(filePath) {
  const BASE_URL = getApp().globalData.baseUrl
  const token = wx.getStorageSync('token')

  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: `${BASE_URL}/api/upload`,
      filePath,
      name: 'file',
      header: { Authorization: `Bearer ${token}` },
      success(res) {
        try {
          const data = JSON.parse(res.data)
          if (data.url) resolve(data.url)
          else reject(new Error(data.detail || '上传失败'))
        } catch (e) {
          reject(e)
        }
      },
      fail: reject
    })
  })
}

function compressImage(src) {
  return new Promise((resolve) => {
    wx.compressImage({
      src,
      quality: 70, // 压缩质量，范围 0~100
      success: (res) => resolve(res.tempFilePath),
      fail: () => resolve(src) // 失败则回退原图
    })
  })
}

module.exports = { request, uploadImage, compressImage }