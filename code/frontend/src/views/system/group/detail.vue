<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>用户组详情</span>
          <div>
            <el-button 
            type="primary" 
            @click="handleEdit" 
            v-if="!isEditing && hasPerms('system.group:update')"
            >编辑</el-button>
            <el-button 
            @click="$router.back()"
            >返回</el-button>
          </div>
        </div>
      </template>

      <template v-if="isEditing && hasPerms('system.group:update')">
        <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
        <el-form-item label="用户组名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入用户组名称" />
        </el-form-item>
        <el-form-item label="父级用户组">
          <el-select v-model="form.parent" placeholder="请选择父级用户组" style="width: 100%">
            <el-option label="无" value="undefined" />
            <el-option
              v-for="item in groupList"
              :key="item.uuid"
              :label="item.name"
              :value="item.uuid"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="用户">
          <el-select
            v-model="form.users"
            multiple
            filterable
            remote
            :remote-method="getUserList"
            :loading="loading"
            placeholder="请输入用户名搜索"
            style="width: 100%"
          >
            <el-option
              v-for="item in userList"
              :key="item.uuid"
              :label="item.username"
              :value="item.uuid"
            />
          </el-select>
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

      <template v-if="!isEditing && hasPerms('system.group:read')">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户组名称">{{ groupInfo.name }}</el-descriptions-item>
          <el-descriptions-item label="父级用户组">{{ parentGroupName }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ groupInfo.description }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ groupInfo.created_time }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ groupInfo.updated_time }}</el-descriptions-item>
        </el-descriptions>

        <div class="section-title">用户列表</div>
        <el-table :data="groupInfo.users" style="width: 100%; margin-bottom: 20px">
          <el-table-column prop="username" label="用户名" >
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/user/detail?uuid=${row.uuid}`)">{{ row.username }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="nickname" label="昵称" />
          <!-- <el-table-column prop="phone" label="手机号" />
          <el-table-column prop="email" label="邮箱" /> -->
          <el-table-column prop="is_active" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div class="section-title">角色列表</div>
        <el-table :data="groupInfo.roles" style="width: 100%; margin-bottom: 20px">
          <el-table-column prop="name" label="角色名称" >
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/role/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" />
        </el-table>

        <div class="section-title">权限列表</div>
        <el-table :data="groupInfo.permissions" style="width: 100%">
          <el-table-column prop="name" label="权限名称" >
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/permission/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" />
        </el-table>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
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
const groupInfo = ref({
  uuid: '',
  name: '',
  parent: undefined,
  description: '',
  created_time: '',
  updated_time: '',
  users: [],
  roles: [],
  permissions: []
})

const form = ref({
  uuid: '',
  name: '',
  parent: undefined,
  description: '',
  users: [] as string[],
  roles: [] as string[],
  permissions: [] as string[]
})

const groupList = ref([])
const userList = ref([])
const roleList = ref([])
const permissionList = ref([])
const loading = ref(false)

const parentGroupName = computed(() => {
  if (!groupInfo.value.parent) return '无'
  const parent = groupList.value.find((g: any) => g.uuid === groupInfo.value.parent)
  return parent ? parent.name : '未知'
})

const rules = {
  name: [
    { required: true, message: '请输入用户组名称', trigger: 'blur' }
  ]
}

// 获取用户组详情
const getGroupDetail = async () => {
  try {
    const res = await http.request('get', apiMap.group.group, {
      params: { uuid: route.query.uuid }
    })
    if (res.success) {
      groupInfo.value = res.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error('获取用户组详情失败')
  }
}

// 获取用户组列表
const getGroupList = async () => {
  try {
    const res = await http.request('get', apiMap.group.groupList)
    if (res.success) {
      groupList.value = res.data.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error('获取用户组列表失败')
  }
}

// 获取用户列表
const getUserList = async (query: string) => {
  if (query) {
    loading.value = true
    try {
      const response = await http.request('get', apiMap.user.userList, {
        params: { search: query }
      })
      if (response.success) {
        userList.value = response.data.data
      } else {
        ElMessage.error('搜索用户失败')
      }
    } catch (error) {
      ElMessage.error('搜索用户失败')
    } finally {
      loading.value = false
    }
  } else {
    userList.value = []
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


// 编辑
const handleEdit = () => {
  form.value = {
    uuid: groupInfo.value.uuid,
    name: groupInfo.value.name,
    parent: groupInfo.value.parent,
    description: groupInfo.value.description,
    users: groupInfo.value.users.map((user: any) => user.uuid),
    roles: groupInfo.value.roles.map((role: any) => role.uuid),
    permissions: groupInfo.value.permissions.map((permission: any) => permission.uuid)
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
        const res = await http.request('put', apiMap.group.group, {
          data: form.value
        })
        if (res.success) {
          ElMessage.success('更新成功')
          isEditing.value = false
          getGroupDetail()
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
  if (!hasPerms('system.group:read')) {
    ElMessage.error('您没有权限查看用户组详情')
    router.push('/error/403')
  }
  getGroupDetail()

  if (hasPerms('system.groupList:read')) {
    getGroupList()
  }
  if (hasPerms('system.userList:read')) {
    getUserList()
  }
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
</style> 