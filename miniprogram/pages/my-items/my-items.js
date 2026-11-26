const { request } = require('../../utils/request')

Page({
  data: { items: [], loading: false },
  onShow() { this.loadItems() },
  async loadItems() {
    this.setData({ loading: true })
    try {
      const res = await request({ url: '/api/items/mine', data: { page: 1, page_size: 50 } })
      this.setData({ items: res.items })
    } catch (e) {} finally { this.setData({ loading: false }) }
  }
})