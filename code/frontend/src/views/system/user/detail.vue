<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>用户详情</span>
          <div>
            <el-button type="primary" @click="handleEdit" v-if="!isEditing && hasPerms('system.user:update')">编辑</el-button>
            <el-button @click="$router.back()"
            >返回</el-button>
          </div>
        </div>
      </template>

      <template v-if="isEditing && hasPerms('system.user:update')">
        <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select
            v-model="form.roles"
            multiple
            filterable
            placeholder="请选择角色"
            style="width: 100%"
          >
            <el-option
              v-for="item in roleList"
              :key="item.uuid"
              :label="item.name"
              :value="item.uuid"
            />
          </el-select>
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

      <template v-if="!isEditing && hasPerms('system.user:read')">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
          <el-descriptions-item label="昵称">{{ userInfo.nickname }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ userInfo.phone }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ userInfo.email }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="userInfo.is_active ? 'success' : 'danger'">
              {{ userInfo.is_active ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ userInfo.created_time }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ userInfo.updated_time }}</el-descriptions-item>
        </el-descriptions>

        <div class="section-title">角色列表</div>
        <el-table :data="userInfo.roles" style="width: 100%; margin-bottom: 20px">
          <el-table-column prop="name" label="角色名称">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/role/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" />
        </el-table>

        <div class="section-title">加入的用户组列表</div>
        <el-table :data="userInfo.groups" style="width: 100%; margin-bottom: 20px">
          <el-table-column prop="name" label="用户组名称">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/group/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" />
        </el-table>

        <div class="section-title">权限列表</div>
        <el-table :data="userInfo.permissions" style="width: 100%">
          <el-table-column prop="name" label="权限名称">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/permission/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" />
        </el-table>

        <div class="section-title">用户权限JSON</div>
        <el-card class="permission-json-card">
          <pre class="permission-json">{{ permissionJson }}</pre>
        </el-card>
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
const userInfo = ref({
  username: '',
  nickname: '',
  phone: '',
  email: '',
  is_active: true,
  created_time: '',
  updated_time: '',
  roles: [],
  permissions: [],
  groups: []
})

const form = ref({
  uuid: '',
  username: '',
  nickname: '',
  phone: '',
  email: '',
  is_active: true,
  roles: [] as string[],
  permissions: [] as string[],
  groups: [] as string[]
})

const roleList = ref([])
const permissionList = ref([])
const permissionJson = ref({})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' }
  ]
}

// 获取用户详情
const getUserDetail = async () => {
  try {
    const res = await http.request('get', apiMap.user.user, {
      params: { uuid: route.query.uuid }
    })
    if (res.success) {
      userInfo.value = res.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error('获取用户详情失败')
  }
}

// 获取角色列表
const getRoleList = async () => {
  try {
    const res = await http.request('get', apiMap.role.roleList)
    if (res.success) {
      roleList.value = res.data.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error('获取角色列表失败')
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

// 获取用户权限JSON
const getUserPermissionJson = async () => {
  try {
    const res = await http.request('get', apiMap.permission.userPermissionJson, {
      params: { uuid: route.query.uuid }
    })
    if (res.success) {
      permissionJson.value = res.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error('获取用户权限JSON失败')
  }
}

// 编辑
const handleEdit = () => {
  form.value = {
    uuid: userInfo.value.uuid,
    username: userInfo.value.username,
    nickname: userInfo.value.nickname,
    phone: userInfo.value.phone,
    email: userInfo.value.email,
    is_active: userInfo.value.is_active,
    roles: userInfo.value.roles.map((role: any) => role.uuid),
    permissions: userInfo.value.permissions.map((permission: any) => permission.uuid)
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
        const res = await http.request('put', apiMap.user.user, {
          data: form.value
        })
        if (res.success) {
          ElMessage.success('更新成功')
          isEditing.value = false
          getUserDetail()
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
  if (!hasPerms('system.user:read')) {
    ElMessage.error('您没有权限查看用户详情')
    router.push('/error/403')
  }
  getUserDetail()
  getUserPermissionJson()
  if (hasPerms('system.roleList:read')) {
    getRoleList()
  }
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
.permission-json-card {
  margin-top: 10px;
}
.permission-json {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 10px;
  margin: 0;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style> 