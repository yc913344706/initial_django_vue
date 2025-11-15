<template>
  <div class="system-page" v-if="hasPerms('system.userList:read')">
    <!-- {{ t('page.user.searchSection') }} -->
    <el-card class="search-card">
      <div class="search-form">
        <div class="form-item">
          <span class="label">{{ t('page.user.keyword') }}</span>
          <el-input
            v-model="searchForm.keyword"
            :placeholder="t('page.user.searchUserPlaceholder')"
            clearable
            class="search-input"
            @keyup.enter="handleSearch"
          />
        </div>

        <div class="form-item button-group">
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            {{ t('button.search') }}
          </el-button>
          <el-button @click="resetSearch">{{ t('button.reset') }}</el-button>
          <el-button
            type="danger"
            @click="handleBatchDelete"
            :disabled="!selectedUsers.length"
            v-if="hasPerms('system.userList:delete')"
          >{{ t('button.batchDelete') }}</el-button>
          <el-button
            type="primary"
            @click="handleAdd"
            v-if="hasPerms('system.userList:create')"
          >{{ t('button.create') }}</el-button>
        </div>
      </div>
    </el-card>

    <!-- {{ t('page.user.tableSection') }} -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="userList"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="username" :label="t('field.username')" />
        <el-table-column prop="nickname" :label="t('field.nickname')" />
        <el-table-column prop="is_active" :label="t('field.status')">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? t('common.enabled') : t('common.disabled') }}
              </el-tag>
            </template>
          </el-table-column>
        <el-table-column prop="phone" :label="t('field.phone')" />
        <el-table-column prop="email" :label="t('field.email')" />
        <el-table-column :label="t('table.actions')" width="400">
          <template #default="scope">
            <el-button type="info" size="small" @click="handleViewDetail(scope.row)">{{ t('button.detail') }}</el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(scope.row)"
              v-if="hasPerms('system.user:delete')"
            >{{ t('button.delete') }}</el-button>
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

    <!-- {{ t('page.user.addEditDialog') }} -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? t('dialog.title.create') : t('dialog.title.edit')"
      width="50%"
    >
      <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
        <el-form-item :label="t('field.username')" prop="username">
          <el-input v-model="form.username" :placeholder="t('page.user.enterUsername')" />
        </el-form-item>
        <el-form-item :label="t('field.nickname')" prop="nickname">
          <el-input v-model="form.nickname" :placeholder="t('page.user.enterNickname')" />
        </el-form-item>
        <el-form-item :label="t('field.phone')" prop="phone">
          <el-input v-model="form.phone" :placeholder="t('page.user.enterPhone')" />
        </el-form-item>
        <el-form-item :label="t('field.email')" prop="email">
          <el-input v-model="form.email" :placeholder="t('page.user.enterEmail')" />
        </el-form-item>
        <el-form-item :label="t('field.password')" prop="password" v-if="dialogType === 'add'">
          <el-input v-model="form.password" type="password" :placeholder="t('page.user.enterPassword')" />
        </el-form-item>
        <el-form-item :label="t('field.status')" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">{{ t('button.cancel') }}</el-button>
          <el-button type="primary" @click="handleSubmit">{{ t('button.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- {{ t('page.user.permissionManagement') }}对话框 -->
    <el-dialog
      v-model="authDialogVisible"
      :title="t('page.user.permissionManagement')"
      width="70%"
    >
      <el-form :model="authForm" label-width="120px">
        <el-form-item :label="t('field.role')">
          <el-select
            v-model="authForm.roles"
            multiple
            filterable
            :placeholder="t('page.user.selectRolePlaceholder')"
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
        <el-form-item :label="t('field.permission')">
          <el-select
            v-model="authForm.permissions"
            multiple
            filterable
            :placeholder="t('page.user.selectPermissionPlaceholder')"
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
          <el-button @click="authDialogVisible = false">{{ t('button.cancel') }}</el-button>
          <el-button type="primary" @click="handleSubmitAuth">{{ t('button.confirm') }}</el-button>
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
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

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
    { required: true, message: t('page.user.enterUsername'), trigger: 'blur' }
  ],
  nickname: [
    { required: true, message: t('page.user.enterNickname'), trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('page.user.enterPassword'), trigger: 'blur' }
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
    ElMessage.error(`${t('message.getUserListFailed')}。${error.msg || error}`)
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
    ElMessage.error(`${t('message.getRoleListFailed')}。${error.msg || error}`)
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
    ElMessage.error(`${t('message.getPermissionListFailed')}。${error.msg || error}`)
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
  ElMessageBox.confirm(t('message.deleteConfirm'), t('common.tip'), {
    type: 'warning'
  }).then(async () => {
    try {
      await http.request('delete', apiMap.user.user, {
        data: { uuid: row.uuid }
      })
      ElMessage.success(t('message.deleteSuccess'))
      getUserList()
    } catch (error) {
      ElMessage.error(`${t('message.deleteFailed')}。${error.msg || error}`)
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
            ElMessage.success(t('message.createSuccess'))
          } else {
            ElMessage.error(res.msg)
          }
        } else {
          const res = await http.request('put', apiMap.user.user, { data: { ...form.value, uuid: form.value.uuid } })
          if (res.success) {
            ElMessage.success(t('message.editSuccess'))
          } else {
            ElMessage.error(res.msg)
          }
        }
        dialogVisible.value = false
        getUserList()
      } catch (error) {
        ElMessage.error(`${dialogType.value === 'add' ? t('message.createFailed') : t('message.editFailed')}。${error.msg || error}`)
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
      ElMessage.success(t('message.updateSuccess'))
      authDialogVisible.value = false
      getUserList()
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error(`${t('message.updateFailed')}。${error.msg || error}`)
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
    await ElMessageBox.confirm(t('message.batchDeleteConfirm'), t('common.tip'), {
      type: 'warning'
    })

    const res = await http.request('delete', apiMap.user.userList, {
      data: { uuids: selectedUsers.value }
    })

    if (res.success) {
      ElMessage.success(t('message.deleteSuccess'))
      getUserList()
      selectedUsers.value = []
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`${t('message.deleteFailed')}。${error.msg || error}`)
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
    ElMessage.error(t('message.noPermissionToViewUserList'))
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