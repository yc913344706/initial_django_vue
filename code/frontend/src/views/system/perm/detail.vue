<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>权限详情</span>
          <div>
            <el-button type="primary" @click="handleEdit" v-if="!isEditing">编辑</el-button>
            <el-button @click="$router.back()">返回</el-button>
          </div>
        </div>
      </template>

      <el-form :model="form" label-width="120px" :rules="rules" ref="formRef" v-if="isEditing">
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入权限名称" />
        </el-form-item>
        <el-form-item label="权限代码" prop="code">
          <el-input v-model="form.code" placeholder="请输入权限代码" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">保存</el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>

      <template v-else>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="权限名称">{{ permissionInfo.name }}</el-descriptions-item>
          <el-descriptions-item label="权限代码">{{ permissionInfo.code }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ permissionInfo.description }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ permissionInfo.created_at }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ permissionInfo.updated_at }}</el-descriptions-item>
        </el-descriptions>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { http } from '@/utils/http'
import { apiMap } from '@/config/api'

const route = useRoute()
const isEditing = ref(false)
const formRef = ref<FormInstance>()
const permissionInfo = ref({
  uuid: '',
  name: '',
  code: '',
  description: '',
  created_at: '',
  updated_at: ''
})

const form = ref({
  uuid: '',
  name: '',
  code: '',
  description: ''
})

const rules = {
  name: [
    { required: true, message: '请输入权限名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入权限代码', trigger: 'blur' }
  ]
}

// 获取权限详情
const getPermissionDetail = async () => {
  try {
    const res = await http.request('get', import.meta.env.VITE_BACKEND_URL + apiMap.permission.permission, {
      params: { uuid: route.query.uuid }
    })
    if (res.success) {
      permissionInfo.value = res.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error('获取权限详情失败')
  }
}

// 编辑
const handleEdit = () => {
  form.value = {
    uuid: permissionInfo.value.uuid,
    name: permissionInfo.value.name,
    code: permissionInfo.value.code,
    description: permissionInfo.value.description
  }
  isEditing.value = true
}

// 取消编辑
const handleCancel = () => {
  isEditing.value = false
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const res = await http.request('put', import.meta.env.VITE_BACKEND_URL + apiMap.permission.permission, {
          data: form.value
        })
        if (res.success) {
          ElMessage.success('更新成功')
          isEditing.value = false
          getPermissionDetail()
        } else {
          ElMessage.error(res.msg)
        }
      } catch (error) {
        ElMessage.error('更新失败')
      }
    }
  })
}

onMounted(() => {
  getPermissionDetail()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 