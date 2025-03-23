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
        <el-table-column prop="user.username" label="用户名" />
        <el-table-column prop="role.name" label="角色" />
        <el-table-column prop="permission.name" label="权限" />
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
        <el-form-item label="用户" prop="user">
          <el-select v-model="form.user" placeholder="请选择用户" style="width: 100%">
            <el-option
              v-for="item in userList"
              :key="item.uuid"
              :label="item.username"
              :value="item.uuid"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" style="width: 100%">
            <el-option
              v-for="item in roleList"
              :key="item.uuid"
              :label="item.name"
              :value="item.uuid"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="权限" prop="permission">
          <el-select v-model="form.permission" placeholder="请选择权限" style="width: 100%">
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

const grantList = ref([])
const userList = ref([])
const roleList = ref([])
const permissionList = ref([])
const dialogVisible = ref(false)
const dialogType = ref('add')
const formRef = ref<FormInstance>()
const form = ref({
  user: '',
  role: '',
  permission: ''
})

const rules = {
  user: [
    { required: true, message: '请选择用户', trigger: 'change' }
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
    const res = await http.get('/api/perm/grants/')
    grantList.value = res.data
  } catch (error) {
    ElMessage.error('获取授权列表失败')
  }
}

// 获取用户列表
const getUserList = async () => {
  try {
    const res = await http.get('/api/user/users/')
    userList.value = res.data
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  }
}

// 获取角色列表
const getRoleList = async () => {
  try {
    const res = await http.get('/api/perm/roles/')
    roleList.value = res.data
  } catch (error) {
    ElMessage.error('获取角色列表失败')
  }
}

// 获取权限列表
const getPermissionList = async () => {
  try {
    const res = await http.get('/api/perm/permissions/')
    permissionList.value = res.data
  } catch (error) {
    ElMessage.error('获取权限列表失败')
  }
}

// 新增授权
const handleAdd = () => {
  dialogType.value = 'add'
  form.value = {
    user: '',
    role: '',
    permission: ''
  }
  dialogVisible.value = true
}

// 编辑授权
const handleEdit = (row) => {
  dialogType.value = 'edit'
  form.value = {
    uuid: row.uuid,
    user: row.user.uuid,
    role: row.role.uuid,
    permission: row.permission.uuid
  }
  dialogVisible.value = true
}

// 删除授权
const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该授权吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await http.delete('/api/perm/grant/', { data: { uuid: row.uuid } })
      ElMessage.success('删除成功')
      getGrantList()
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
          await http.post('/api/perm/grant/', form.value)
          ElMessage.success('新增成功')
        } else {
          await http.put('/api/perm/grant/', form.value)
          ElMessage.success('编辑成功')
        }
        dialogVisible.value = false
        getGrantList()
      } catch (error) {
        ElMessage.error(dialogType.value === 'add' ? '新增失败' : '编辑失败')
      }
    }
  })
}

onMounted(() => {
  getGrantList()
  getUserList()
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