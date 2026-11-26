const { request } = require('../../utils/request')
const { CATEGORIES } = require('../../utils/format')

Page({
  data: {
    categories: ['全部', ...CATEGORIES],
    activeCategory: '全部',
    activeType: -1,
    keyword: '',
    items: [],
    page: 1,
    pageSize: 10,
    total: 0,
    loading: false,
    finished: false,
    fabLeft: 0,       // 悬浮球 X 坐标
    fabTop: 0,        // 悬浮球 Y 坐标
    startX: 0,        // 触摸起点 X
    startY: 0,        // 触摸起点 Y
    startLeft: 0,     // 拖动前悬浮球 X
    startTop: 0,      // 拖动前悬浮球 Y
    isDragging: false // 是否正在拖动
  },

  onLoad() {
    this.loadItems(true)
    //初始化悬浮球位置（默认在屏幕右下角）
    const sysInfo = wx.getSystemInfoSync()
    this.setData({
      fabLeft: sysInfo.windowWidth - 70, 
      fabTop: sysInfo.windowHeight - 250 
    })
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 0 })
      this.getTabBar().getUnreadCount()
    }
    if (this.data.items.length > 0) this.loadItems(true)
  },

  onPullDownRefresh() {
    this.loadItems(true).then(() => wx.stopPullDownRefresh())
  },

  onReachBottom() {
    if (!this.data.finished && !this.data.loading) this.loadItems(false)
  },

  onKeywordInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  onSearch() {
    this.loadItems(true)
  },

  onCategoryTap(e) {
    const category = e.currentTarget.dataset.category
    this.setData({ activeCategory: category })
    this.loadItems(true)
  },

  onTypeTap(e) {
    const type = Number(e.currentTarget.dataset.type)
    this.setData({ activeType: type })
    this.loadItems(true)
  },

  async loadItems(reset) {
    if (this.data.loading) return
    this.setData({ loading: true })
    const page = reset ? 1 : this.data.page

    const params = { page, page_size: this.data.pageSize, status: 0 }
    if (this.data.activeType >= 0) params.type = this.data.activeType
    if (this.data.activeCategory !== '全部') params.category = this.data.activeCategory
    if (this.data.keyword) params.keyword = this.data.keyword

    try {
      const res = await request({ url: '/api/items', data: params })
      const items = reset ? res.items : this.data.items.concat(res.items)
      this.setData({
        items,
        total: res.total,
        page: page + 1,
        finished: items.length >= res.total
      })
    } catch (e) {
      // toast 已在 request 中处理
    } finally {
      this.setData({ loading: false })
    }
  },

  //1. 手指按下
  onTouchStart(e) {
    this.setData({
      startX: e.touches[0].clientX,
      startY: e.touches[0].clientY,
      startLeft: this.data.fabLeft,
      startTop: this.data.fabTop,
      isDragging: false
    })
  },

  //2. 手指移动
  onTouchMove(e) {
    const touch = e.touches[0]
    const dx = touch.clientX - this.data.startX
    const dy = touch.clientY - this.data.startY

    // 如果移动距离超过 5px，判定为拖动，防止误触
    if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
      this.setData({ isDragging: true })
    }

    if (this.data.isDragging) {
      const sysInfo = wx.getSystemInfoSync()
      let newLeft = this.data.startLeft + dx
      let newTop = this.data.startTop + dy

      // 边界限制（防止拖出屏幕）
      const maxLeft = sysInfo.windowWidth - 60
      const maxTop = sysInfo.windowHeight - 60
      
      if (newLeft < 10) newLeft = 10
      if (newLeft > maxLeft) newLeft = maxLeft
      if (newTop < 10) newTop = 10
      if (newTop > maxTop) newTop = maxTop

      this.setData({ fabLeft: newLeft, fabTop: newTop })
    }
  },

  //3. 手指抬起
  onTouchEnd(e) {
    // 如果没有发生拖动（移动距离很小），则判定为点击事件
    if (!this.data.isDragging) {
      this.goChat()
    } else {
      // 拖动结束后，实现“边缘吸附”效果（丝滑体验）
      const sysInfo = wx.getSystemInfoSync()
      // 如果位置在左半边，吸到左边；在右半边，吸到右边
      const isLeft = this.data.fabLeft < sysInfo.windowWidth / 2
      this.setData({
        fabLeft: isLeft ? 20 : sysInfo.windowWidth - 70
      })
    }
  },

  goChat() {
    wx.switchTab({ url: '/pages/chat/chat' })
  },

  goPublish() {
    wx.switchTab({ url: '/pages/publish/publish' })
  }
})