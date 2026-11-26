const { request } = require('../utils/request')
Component({
  data: {
    selected: 0,
    unreadTotal: 0,
    list: [
      { pagePath: "/pages/index/index", text: "首页", iconPath: "/images/tabbar/home.png", selectedIconPath: "/images/tabbar/home-active.png" },
      { pagePath: "/pages/chat/chat", text: "AI助手", iconPath: "/images/tabbar/AI.png", selectedIconPath: "/images/tabbar/AI-active.png" },
      { pagePath: "/pages/publish/publish", text: "发布", isPublish: true }, // 中间按钮保留红色凸起设计
      { pagePath: "/pages/messages/messages", text: "消息", iconPath: "/images/tabbar/chat.png", selectedIconPath: "/images/tabbar/chat-active.png" }, 
      { pagePath: "/pages/mine/mine", text: "我的", iconPath: "/images/tabbar/mine.png", selectedIconPath: "/images/tabbar/mine-active.png" }
    ]
  },
  attached() {
    this.getUnreadCount() // 组件挂载时拉取一次
  },
  methods: {
    switchTab(e) {
      const data = e.currentTarget.dataset
      const url = data.path
      wx.switchTab({ url })
    },
    //获取未读总数
    async getUnreadCount() {
      const token = wx.getStorageSync('token')
      if (!token) return
      try {
        const res = await request({ url: '/api/messages/unread_total' })
        this.setData({ unreadTotal: res.count })
      } catch (e) {}
    }
  }
})