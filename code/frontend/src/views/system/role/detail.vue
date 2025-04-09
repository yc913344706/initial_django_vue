<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>角色详情</span>
          <div>
            <el-button type="primary" @click="handleEdit" v-if="!isEditing && hasPerms('system.role:update')">编辑</el-button>
            <el-button @click="$router.back()"
            >返回</el-button>
          </div>
        </div>
      </template>

      <template v-if="isEditing && hasPerms('system.role:update')">
        <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
          <el-form-item label="角色名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入角色名称" />
          </el-form-item>
          <el-form-item label="角色代码" prop="code">
            <el-input v-model="form.code" placeholder="请输入角色代码" />
          </el-form-item>
          <el-form-item label="描述" prop="description">
            <el-input v-model="form.description" type="textarea" placeholder="请输入描述" />
          </el-form-item>
          <el-form-item label="权限">
            <el-select
              v-model="form.permissions"
              multiple
              filterable
              placeholder="请选择权限"
              style="width: 100%"
            >
              <el-option
                v-for="item in permissionList"
                :key="item.uuid"
                :label="item.name"
                :value="item.uuid"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSubmit">保存</el-button>
            <el-button @click="handleCancel">取消</el-button>
          </el-form-item>
        </el-form>
      </template>

      <template v-if="!isEditing && hasPerms('system.role:read')">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="角色名称">{{ roleInfo.name }}</el-descriptions-item>
          <el-descriptions-item label="角色代码">{{ roleInfo.code }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ roleInfo.description }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ roleInfo.created_time }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ roleInfo.updated_time }}</el-descriptions-item>
        </el-descriptions>

        <div class="section-title">权限列表</div>
        <el-table :data="roleInfo.permissions" style="width: 100%; margin-bottom: 20px">
          <el-table-column prop="name" label="权限名称">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/permission/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" />
        </el-table>

        <div class="section-title">授予此角色的用户列表</div>
        <el-table :data="roleInfo.users" style="width: 100%; margin-bottom: 20px">
          <el-table-column prop="username" label="用户名">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/user/detail?uuid=${row.uuid}`)">{{ row.username }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="nickname" label="昵称" />
          <el-table-column prop="is_active" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div class="section-title">授予此角色的用户组列表</div>
        <el-table :data="roleInfo.groups" style="width: 100%">
          <el-table-column prop="name" label="用户组名称">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/group/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" />
        </el-table>
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
import { hasPerms } from "@/utils/auth";
import router from '@/router'

const route = useRoute()
const isEditing = ref(false)
const formRef = ref<FormInstance>()
const roleInfo = ref({
  uuid: '',
  name: '',
  code: '',
  description: '',
  created_time: '',
  updated_time: '',
  permissions: [],
  users: [],
  groups: []
})

const form = ref({
  uuid: '',
  name: '',
  code: '',
  description: '',
  permissions: [] as string[]
})

const permissionList = ref([])

const rules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入角色代码', trigger: 'blur' }
  ]
}

// 获取角色详情
const getRoleDetail = async () => {
  try {
    const res = await http.request('get', apiMap.role.role, {
      params: { uuid: route.query.uuid }
    })
    if (res.success) {
      roleInfo.value = res.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error('获取角色详情失败')
  }
}

// 获取权限列表
const getPermissionList = async () => {
  try {
    const res = await http.request('get', apiMap.permission.permissionList)
    if (res.success) {
      permissionList.value = res.data.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error('获取权限列表失败')
  }
}

// 编辑
const handleEdit = () => {
  form.value = {
    uuid: roleInfo.value.uuid,
    name: roleInfo.value.name,
    code: roleInfo.value.code,
    description: roleInfo.value.description,
    permissions: roleInfo.value.permissions.map((permission: any) => permission.uuid)
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
        const res = await http.request('put', apiMap.role.role, {
          data: form.value
        })
        if (res.success) {
          ElMessage.success('更新成功')
          isEditing.value = false
          getRoleDetail()
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
  if (!hasPerms('system.role:read')) {
    ElMessage.error('您没有权限查看角色详情')
    router.push('/error/403')
  }
  getRoleDetail()
  if (hasPerms('system.permissionList:read')) {
    getPermissionList()
  }
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.section-title {
  font-size: 16px;
  font-weight: bold;
  margin: 20px 0 10px;
}
</style> 