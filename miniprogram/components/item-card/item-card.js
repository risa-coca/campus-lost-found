const { formatTime } = require('../../utils/format')

Component({
  properties: {
    item: { type: Object, value: {} }
  },
  data: {
    timeText: ''
  },
  observers: {
    item(item) {
      if (item && item.created_at) {
        this.setData({ timeText: formatTime(item.created_at) })
      }
    }
  },
  methods: {
    onTap() {
      wx.navigateTo({ url: `/pages/detail/detail?id=${this.data.item.id}` })
    }
  }
})