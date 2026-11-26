<template>
  <el-table :data="items" border stripe style="width: 100%">
    <el-table-column prop="id" label="ID" width="80" />
    <el-table-column prop="type" label="类型" width="100">
      <template #default="{ row }">
        <el-tag :type="row.type === 0 ? 'danger' : 'success'">{{ row.type === 0 ? '寻物' : '招领' }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="title" label="标题" />
    <el-table-column prop="description" label="描述" show-overflow-tooltip />
    <el-table-column prop="location" label="地点" width="150" />
    <el-table-column prop="status" label="状态" width="120">
      <template #default="{ row }">
        <el-tag v-if="row.status === 0" type="warning">待匹配</el-tag>
        <el-tag v-else-if="row.status === 2" type="success">已归还</el-tag>
        <el-tag v-else type="info">已关闭</el-tag>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../utils/request'

const items = ref([])
onMounted(async () => {
  items.value = await request.get('/admin/items')
})
</script>