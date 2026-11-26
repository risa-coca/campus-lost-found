<template>
  <el-table :data="claims" border stripe>
    <el-table-column prop="item.title" label="认领物品" />
    <el-table-column prop="claim.answers" label="认领验证信息" />
    <el-table-column label="操作" width="200">
      <template #default="{ row }">
        <el-button type="success" size="small" @click="handleReview(row.claim.id, 'approve')">同意</el-button>
        <el-button type="danger" size="small" @click="handleReview(row.claim.id, 'reject')">拒绝</el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../utils/request'
import { ElMessage } from 'element-plus'

const claims = ref([])
const loadData = async () => {
  claims.value = await request.get('/admin/claims')
}

const handleReview = async (id, action) => {
  await request.post(`/claims/${id}/${action}`) // 复用原有的审核接口
  ElMessage.success('操作成功')
  loadData()
}

onMounted(loadData)
</script>