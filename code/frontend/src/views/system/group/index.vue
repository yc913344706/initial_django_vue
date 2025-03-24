<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>角色组</span>
          <el-button type="primary" @click="handleAdd">新增</el-button>
        </div>
      </template>

      <el-table :data="userGroupList" style="width: 100%">
        <el-table-column prop="name" label="角色组" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" width="300">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="success" size="small" @click="handleManageUsers(scope.row)">管理用户</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增' : '编辑'"
      width="50%"
    >
      <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
        <el-form-item label="角色组" prop="name">
          <el-input v-model="form.name" :placeholder="角色组" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :placeholder="描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 管理用户对话框 -->
    <el-dialog
      v-model="userDialogVisible"
      title="管理用户"
      width="70%"
    >
      <el-form :model="userForm" label-width="120px">
        <el-form-item label="用户">
          <el-select
            v-model="userForm.users"
            multiple
            filterable
            placeholder="用户"
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
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="userDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitUsers">确定</el-button>
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

interface UserGroupForm {
  uuid?: string
  name: string
  description: string
}

interface UserForm {
  userGroup: string
  users: string[]
}

const userGroupList = ref([])
const userList = ref([])
const dialogVisible = ref(false)
const userDialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const formRef = ref<FormInstance>()
const form = ref<UserGroupForm>({
  name: '',
  description: ''
})
const userForm = ref<UserForm>({
  userGroup: '',
  users: []
})

const rules = {
  name: [
    { required: true, message: '角色组', trigger: 'blur' }
  ]
}

// 获取用户组列表
const getUserGroupList = async () => {
  try {
    const res = await http.request('get', import.meta.env.VITE_BACKEND_URL + apiMap.group.groupList)
    if (res.success) {
      userGroupList.value = res.data.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error('获取用户组列表失败')
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

// 新增用户组
const handleAdd = () => {
  dialogType.value = 'add'
  form.value = {
    name: '',
    description: ''
  }
  dialogVisible.value = true
}

// 编辑用户组
const handleEdit = (row: UserGroupForm) => {
  dialogType.value = 'edit'
  form.value = { ...row }
  dialogVisible.value = true
}

// 管理用户
const handleManageUsers = async (row: UserGroupForm) => {
  userForm.value.userGroup = row.uuid
  await getUserGroupUsers(row.uuid)
  userDialogVisible.value = true
}

// 删除用户组
const handleDelete = (row: UserGroupForm) => {
  ElMessageBox.confirm('确定删除该用户组吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await http.request('delete', import.meta.env.VITE_BACKEND_URL + apiMap.group.group, {
        data: { uuid: row.uuid }
      })
      ElMessage.success('删除成功')
      getUserGroupList()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (dialogType.value === 'add') {
          const res = await http.request('post', import.meta.env.VITE_BACKEND_URL + apiMap.group.group, form.value)
          if (res.success) {
            ElMessage.success('新增成功')
          } else {
            ElMessage.error(res.msg)
          }
        } else {
          const res = await http.request('put', import.meta.env.VITE_BACKEND_URL + apiMap.group.group, { ...form.value, uuid: form.value.uuid })
          if (res.success) {
            ElMessage.success('编辑成功')
          } else {
            ElMessage.error(res.msg)
          }
        }
        dialogVisible.value = false
        getUserGroupList()
      } catch (error) {
        ElMessage.error(dialogType.value === 'add' ? '新增失败' : '编辑失败')
      }
    }
  })
}

// 提交用户表单
const handleSubmitUsers = async () => {
  try {
    // 删除原有用户关联
    await http.request('delete', import.meta.env.VITE_BACKEND_URL + apiMap.group.groupUser, {
      data: { user_group: userForm.value.userGroup }
    })

    // 添加新的用户关联
    for (const userUuid of userForm.value.users) {
      await http.request('post', import.meta.env.VITE_BACKEND_URL + apiMap.group.groupUser, {
        user_group: userForm.value.userGroup,
        user: userUuid
      })
    }

    ElMessage.success('更新成功')
    userDialogVisible.value = false
    getUserGroupList()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

onMounted(() => {
  getUserGroupList()
  getUserList()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 