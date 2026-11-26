<template>
  <el-container style="height: 100vh;">
    <el-aside width="200px" style="background: #304156;">
      <div class="logo">拾光校园</div>
      <el-menu
        active-text-color="#409EFF"
        background-color="#304156"
        text-color="#bfcbd9"
        :default-active="$route.path"
        router
      >
        <el-menu-item index="/dashboard">仪表盘</el-menu-item>
        <el-menu-item index="/items">物品管理</el-menu-item>
        <el-menu-item index="/claims">认领审核</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="background: #fff; display: flex; justify-content: space-between; align-items: center;">
        <div>{{ $route.meta.title }}</div>
        <el-button link type="danger" @click="logout">退出登录</el-button>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const logout = () => {
  localStorage.removeItem('admin_token')
  router.push('/login')
}
</script>

<style scoped>
.logo {
  color: #fff;
  font-size: 20px;
  text-align: center;
  padding: 20px 0;
  font-weight: bold;
}
</style>