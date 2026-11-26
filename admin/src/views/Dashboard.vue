<template>
  <el-row :gutter="20">
    <el-col :span="6">
      <el-card shadow="hover">
        <div class="stat-title">注册用户</div>
        <div class="stat-value">{{ stats.total_users }}</div>
      </el-card>
    </el-col>
    <el-col :span="6">
      <el-card shadow="hover">
        <div class="stat-title">发布物品</div>
        <div class="stat-value">{{ stats.total_items }}</div>
      </el-card>
    </el-col>
    <el-col :span="6">
      <el-card shadow="hover">
        <div class="stat-title">成功归还</div>
        <div class="stat-value" style="color: #67C23A">{{ stats.returned_items }}</div>
      </el-card>
    </el-col>
    <el-col :span="6">
      <el-card shadow="hover">
        <div class="stat-title">待审核认领</div>
        <div class="stat-value" style="color: #E6A23C">{{ stats.pending_claims }}</div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../utils/request'

const stats = ref({ total_users: 0, total_items: 0, returned_items: 0, pending_claims: 0 })

onMounted(async () => {
  stats.value = await request.get('/admin/dashboard')
})
</script>

<style scoped>
.stat-title { color: #909399; font-size: 14px; margin-bottom: 10px; }
.stat-value { font-size: 28px; font-weight: bold; }
</style>