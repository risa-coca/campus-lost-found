<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>拾光校园 - 后台管理</h2>
      
      <el-form :model="form" style="margin-top: 20px;">
        <el-form-item>
          <el-input v-model="form.username" placeholder="请输入管理员账号" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password size="large" @keyup.enter="login" />
        </el-form-item>
        <el-button type="primary" size="large" style="width: 100%" @click="login" :loading="loading">
          登录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const form = ref({
  username: 'admin', // 方便测试默认填好
  password: '123456'
})

const login = async () => {
  if (!form.value.username || !form.value.password) {
    return ElMessage.warning('请输入账号和密码')
  }
  
  loading.value = true
  try {
    // 这里请求新的 admin_login 接口
    const res = await request.post('/auth/admin_login', form.value)
    
    localStorage.setItem('admin_token', res.token)
    localStorage.setItem('admin_user', JSON.stringify(res.user))
    
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e) {
    // 错误处理已经在 request.js 里统一做了
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f0f2f5;
}
.login-card {
  width: 400px;
  text-align: center;
  padding: 20px;
  border-radius: 12px;
}
</style>