<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>授权管理</span>
          <el-button type="primary" @click="handleAdd">新增授权</el-button>
        </div>
      </template>

      <el-table :data="grantList" style="width: 100%">
        <el-table-column prop="user.username" :label="用户" />
        <el-table-column prop="userGroup.name" :label="用户组" />
        <el-table-column prop="role.name" :label="角色" />
        <el-table-column prop="permission.name" :label="权限" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增授权' : '编辑授权'"
      width="50%"
    >
      <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
        <!-- 授权对象类型选择 -->
        <el-form-item label="授权对象类型" prop="grantType">
          <el-radio-group v-model="form.grantType">
            <el-radio label="user">用户</el-radio>
            <el-radio label="userGroup">用户组</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 根据授权对象类型显示不同的选择器 -->
        <el-form-item 
          v-if="form.grantType === 'user'" 
          label="用户" 
          prop="user"
        >
          <el-select v-model="form.user" :placeholder="请选择用户" style="width: 100%" multiple>
            <el-option
              v-for="item in userList"
              :key="item.uuid"
              :label="item.username"
              :value="item.uuid"
            />
          </el-select>
        </el-form-item>

        <el-form-item 
          v-if="form.grantType === 'userGroup'" 
          label="用户组" 
          prop="userGroup"
        >
          <el-select v-model="form.userGroup" :placeholder="请选择用户组" style="width: 100%" multiple>
            <el-option
              v-for="item in userGroupList"
              :key="item.uuid"
              :label="item.name"
              :value="item.uuid"
            />
          </el-select>
        </el-form-item>

        <!-- 授权类型选择 -->
        <el-form-item label="授权类型" prop="authType">
          <el-radio-group v-model="form.authType">
            <el-radio label="role">角色</el-radio>
            <el-radio label="permission">权限</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 根据授权类型显示不同的选择器 -->
        <el-form-item 
          v-if="form.authType === 'role'" 
          label="角色" 
          prop="role"
        >
          <el-select v-model="form.role" :placeholder="请选择角色" style="width: 100%" multiple>
            <el-option
              v-for="item in roleList"
              :key="item.uuid"
              :label="item.name"
              :value="item.uuid"
            />
          </el-select>
        </el-form-item>

        <el-form-item 
          v-if="form.authType === 'permission'" 
          label="权限" 
          prop="permission"
        >
          <el-select v-model="form.permission" :placeholder="请选择权限" style="width: 100%" multiple>
            <el-option
              v-for="item in permissionList"
              :key="item.uuid"
              :label="item.name"
              :value="item.uuid"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { http } from '@/utils/http'
import { apiMap } from '@/config/api'

interface GrantForm {
  uuid?: string
  grantType: 'user' | 'userGroup'
  user?: string[]
  userGroup?: string[]
  authType: 'role' | 'permission'
  role?: string[]
  permission?: string[]
}

const grantList = ref([])
const userList = ref([])
const userGroupList = ref([])
const roleList = ref([])
const permissionList = ref([])
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const formRef = ref<FormInstance>()
const form = ref<GrantForm>({
  grantType: 'user',
  user: [],
  userGroup: [],
  authType: 'role',
  role: [],
  permission: []
})

const rules = {
  grantType: [
    { required: true, message: '请选择授权对象', trigger: 'change' }
  ],
  user: [
    { required: true, message: '请选择用户', trigger: 'change' }
  ],
  userGroup: [
    { required: true, message: '请选择用户组', trigger: 'change' }
  ],
  authType: [
    { required: true, message: '请选择授权类型', trigger: 'change' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  permission: [
    { required: true, message: '请选择权限', trigger: 'change' }
  ]
}

// 获取授权列表
const getGrantList = async () => {
  try {
    const res = await http.request('get', import.meta.env.VITE_BACKEND_URL + apiMap.grant.grantList)
    if (res.success) {
      grantList.value = res.data.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error('获取授权列表失败')
  }
}

// 获取用户列表
const getUserList = async () => {
  try {
    const res = await http.request('get', import.meta.env.VITE_BACKEND_URL + apiMap.user.userList)
    if (res.success) {
      userList.value = res.data.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  }
}

// 获取用户组列表
const getUserGroupList = async () => {
  try {
    const res = await http.request('get', import.meta.env.VITE_BACKEND_URL + apiMap.userGroup.userGroupList)
    if (res.success) {
      userGroupList.value = res.data.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error('获取用户组列表失败')
  }
}

// 获取角色列表
const getRoleList = async () => {
  try {
    const res = await http.request('get', import.meta.env.VITE_BACKEND_URL + apiMap.role.roleList)
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
    const res = await http.request('get', import.meta.env.VITE_BACKEND_URL + apiMap.permission.permissionList)
    if (res.success) {
      permissionList.value = res.data.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error('获取权限列表失败')
  }
}

// 新增授权
const handleAdd = () => {
  dialogType.value = 'add'
  form.value = {
    grantType: 'user',
    user: [],
    userGroup: [],
    authType: 'role',
    role: [],
    permission: []
  }
  dialogVisible.value = true
}

// 编辑授权
const handleEdit = (row: GrantForm) => {
  dialogType.value = 'edit'
  form.value = {
    uuid: row.uuid,
    grantType: row.user ? 'user' : 'userGroup',
    user: Array.isArray(row.user) ? row.user : [row.user],
    userGroup: Array.isArray(row.userGroup) ? row.userGroup : [row.userGroup],
    authType: row.role ? 'role' : 'permission',
    role: Array.isArray(row.role) ? row.role : [row.role],
    permission: Array.isArray(row.permission) ? row.permission : [row.permission]
  }
  dialogVisible.value = true
}

// 删除授权
const handleDelete = (row: GrantForm) => {
  ElMessageBox.confirm('确定删除该授权吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await http.request('delete', import.meta.env.VITE_BACKEND_URL + apiMap.grant.grant, {
        data: { uuid: row.uuid }
      })
      ElMessage.success('删除授权成功')
      getGrantList()
    } catch (error) {
      ElMessage.error('删除授权失败')
    }
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const submitData = {
          user: form.value.grantType === 'user' ? form.value.user : null,
          userGroup: form.value.grantType === 'userGroup' ? form.value.userGroup : null,
          role: form.value.authType === 'role' ? form.value.role : null,
          permission: form.value.authType === 'permission' ? form.value.permission : null
        }

        if (dialogType.value === 'add') {
          const res = await http.request('post', import.meta.env.VITE_BACKEND_URL + apiMap.grant.grant, submitData)
          if (res.success) {
            ElMessage.success('新增授权成功')
          } else {
            ElMessage.error(res.msg)
          }
        } else {
          const res = await http.request('put', import.meta.env.VITE_BACKEND_URL + apiMap.grant.grant, { ...submitData, uuid: form.value.uuid })
          if (res.success) {
            ElMessage.success('编辑授权成功')
          } else {
            ElMessage.error(res.msg)
          }
        }
        dialogVisible.value = false
        getGrantList()
      } catch (error) {
        ElMessage.error(dialogType.value === 'add' ? '新增授权失败' : '编辑授权失败')
      }
    }
  })
}

onMounted(() => {
  getGrantList()
  getUserList()
  getUserGroupList()
  getRoleList()
  getPermissionList()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 