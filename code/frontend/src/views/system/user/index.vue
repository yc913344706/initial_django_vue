<template>
  <div class="system-page" v-if="hasPerms('system.userList:read')">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <div class="search-form">
        <div class="form-item">
          <span class="label">关键词</span>
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索用户名/昵称/手机号/邮箱"
            clearable
            class="search-input"
            @keyup.enter="handleSearch"
          />
        </div>

        <div class="form-item button-group">
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
          <el-button 
            type="danger" 
            @click="handleBatchDelete" 
            :disabled="!selectedUsers.length"
            v-if="hasPerms('system.userList:delete')"
          >批量删除</el-button>
          <el-button 
            type="primary" 
            @click="handleAdd"
            v-if="hasPerms('system.userList:create')"
          >新增</el-button>
        </div>
      </div>
    </el-card>

    <!-- 表格区域 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="userList"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="nickname" label="昵称" />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column label="操作" width="400">
          <template #default="scope">
            <el-button type="info" size="small" @click="handleViewDetail(scope.row)">查看详情</el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(scope.row)" 
              v-if="hasPerms('system.user:delete')"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增用户' : '编辑用户'"
      width="50%"
    >
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
        <el-form-item label="密码" prop="password" v-if="dialogType === 'add'">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 权限管理对话框 -->
    <el-dialog
      v-model="authDialogVisible"
      title="权限管理"
      width="70%"
    >
      <el-form :model="authForm" label-width="120px">
        <el-form-item label="角色">
          <el-select
            v-model="authForm.roles"
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
            v-model="authForm.permissions"
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
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="authDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitAuth">确定</el-button>
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
import { hasPerms } from "@/utils/auth";
import router from '@/router'
import { Search } from '@element-plus/icons-vue'
import '@/style/system.scss'

interface UserForm {
  uuid?: string
  username: string
  nickname: string
  phone: string
  email: string
  password?: string
  is_active: boolean
}

interface AuthForm {
  uuid: string
  roles: string[]
  permissions: string[]
}

const userList = ref([])
const roleList = ref([])
const permissionList = ref([])
const dialogVisible = ref(false)
const authDialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const formRef = ref<FormInstance>()
const form = ref<UserForm>({
  username: '',
  nickname: '',
  phone: '',
  email: '',
  password: '',
  is_active: true
})
const authForm = ref<AuthForm>({
  uuid: '',
  roles: [],
  permissions: []
})
const selectedUsers = ref<string[]>([])

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const loading = ref(false)

// 分页相关
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 搜索相关
const searchForm = ref({
  keyword: ''
})

// 获取用户列表
const getUserList = async () => {
  try {
    loading.value = true
    const params = {
      page: page.value,
      page_size: pageSize.value,
      search: searchForm.value.keyword
    }
    const res = await http.request('get', apiMap.user.userList, { params: params })
    if (res.success) {
      userList.value = res.data.data
      total.value = res.data.total
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
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

// 新增用户
const handleAdd = () => {
  dialogType.value = 'add'
  form.value = {
    username: '',
    nickname: '',
    phone: '',
    email: '',
    password: '',
    is_active: true
  }
  dialogVisible.value = true
}

// 查看详情
const handleViewDetail = (row: UserForm) => {
  router.push({
    path: '/system/user/detail',
    query: { uuid: row.uuid }
  })
}

// 删除用户
const handleDelete = (row: UserForm) => {
  ElMessageBox.confirm('确定删除该用户吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await http.request('delete', apiMap.user.user, {
        data: { uuid: row.uuid }
      })
      ElMessage.success('删除成功')
      getUserList()
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
          const res = await http.request('post', apiMap.user.user, { data: form.value })
          if (res.success) {
            ElMessage.success('新增成功')
          } else {
            ElMessage.error(res.msg)
          }
        } else {
          const res = await http.request('put', apiMap.user.user, { data: { ...form.value, uuid: form.value.uuid } })
          if (res.success) {
            ElMessage.success('编辑成功')
          } else {
            ElMessage.error(res.msg)
          }
        }
        dialogVisible.value = false
        getUserList()
      } catch (error) {
        ElMessage.error(dialogType.value === 'add' ? '新增失败' : '编辑失败')
      }
    }
  })
}

// 提交权限表单
const handleSubmitAuth = async () => {
  try {
    const res = await http.request('put', apiMap.user.user, {
      data: {
        uuid: authForm.value.uuid,
        roles: authForm.value.roles,
        permissions: authForm.value.permissions
      }
    })
    if (res.success) {
      ElMessage.success('更新成功')
      authDialogVisible.value = false
      getUserList()
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

// 表格选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedUsers.value = selection.map(item => item.uuid)
}

// 批量删除
const handleBatchDelete = async () => {
  if (!selectedUsers.value.length) return
  
  try {
    await ElMessageBox.confirm('确定要删除选中的用户吗?', '提示', {
      type: 'warning'
    })
    
    const res = await http.request('delete', apiMap.user.userList, {
      data: { uuids: selectedUsers.value }
    })
    
    if (res.success) {
      ElMessage.success('删除成功')
      getUserList()
      selectedUsers.value = []
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 处理搜索
const handleSearch = () => {
  page.value = 1
  getUserList()
}

// 处理页码改变
const handleCurrentChange = (val: number) => {
  page.value = val
  getUserList()
}

// 处理每页条数改变
const handleSizeChange = (val: number) => {
  pageSize.value = val
  page.value = 1
  getUserList()
}

// 重置搜索
const resetSearch = () => {
  searchForm.value.keyword = ''
  page.value = 1
  getUserList()
}

onMounted(() => {
  if (!hasPerms('system.userList:read')) {
    ElMessage.error('您没有权限查看用户列表')
    router.push('/error/403')
  }
  getUserList()
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

.search-box {
  margin-left: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style> 