<template>
  <div class="system-page" v-if="hasPerms('system.groupList:read')">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <div class="search-form">
        <div class="form-item">
          <span class="label">{{ t('page.group.keyword') }}</span>
          <el-input
            v-model="searchForm.keyword"
            :placeholder="t('page.group.searchPlaceholder')"
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
            :disabled="!selectedGroups.length"
            v-if="hasPerms('system.groupList:delete')"
          >{{ t('button.batchDelete') }}</el-button>
          <el-button
            type="primary"
            @click="handleAdd"
            v-if="hasPerms('system.groupList:create')"
          >{{ t('button.create') }}</el-button>
        </div>
      </div>
    </el-card>

    <!-- 表格区域 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="userGroupList"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" :label="t('page.group.name')" />
        <el-table-column prop="description" :label="t('field.description')" />
        <el-table-column :label="t('table.actions')" width="500">
          <template #default="scope">
            <el-button type="info" size="small" @click="handleViewDetail(scope.row)">{{ t('button.detail') }}</el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(scope.row)"
              v-if="hasPerms('system.group:delete')"
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

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? t('dialog.title.create') + t('common.group') : t('dialog.title.edit') + t('common.group')"
      width="50%"
    >
      <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
        <el-form-item :label="t('page.group.name')" prop="name">
          <el-input v-model="form.name" :placeholder="t('page.group.enterName')" />
        </el-form-item>
        <el-form-item :label="t('page.group.parentGroup')" prop="parent">
          <el-select v-model="form.parent" :placeholder="t('page.group.selectParentGroup')" clearable style="width: 100%">
            <el-option
              v-for="item in userGroupList"
              :key="item.uuid"
              :label="item.name"
              :value="item.uuid"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('field.description')" prop="description">
          <el-input v-model="form.description" type="textarea" :placeholder="t('page.group.enterDescription')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">{{ t('button.cancel') }}</el-button>
          <el-button type="primary" @click="handleSubmit">{{ t('button.confirm') }}</el-button>
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
import { useRouter } from 'vue-router'
import { hasPerms } from "@/utils/auth";
import { Search } from '@element-plus/icons-vue'
import '@/style/system.scss'
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

interface UserGroupForm {
  uuid?: string
  name: string
  parent?: string
  description: string
}

interface UserForm {
  userGroup: string
  users: string[]
}

interface AuthForm {
  uuid: string
  roles: string[]
  permissions: string[]
}

const userGroupList = ref([])
const userList = ref([])
const roleList = ref([])
const permissionList = ref([])
const dialogVisible = ref(false)
const userDialogVisible = ref(false)
const authDialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const formRef = ref<FormInstance>()
const form = ref<UserGroupForm>({
  name: '',
  parent: undefined,
  description: ''
})
const userForm = ref<UserForm>({
  userGroup: '',
  users: []
})
const authForm = ref<AuthForm>({
  uuid: '',
  roles: [],
  permissions: []
})
const selectedGroups = ref<string[]>([])

// 分页相关
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 搜索相关
const searchForm = ref({
  keyword: ''
})

const rules = {
  name: [
    { required: true, message: t('page.group.enterName'), trigger: 'blur' }
  ]
}

const loading = ref(false)
// 获取用户组列表
const getUserGroupList = async () => {
  try {
    loading.value = true
    const params = {
      page: page.value,
      page_size: pageSize.value,
      search: searchForm.value.keyword
    }
    const res = await http.request('get', apiMap.group.groupList, { params: params })
    if (res.success) {
      userGroupList.value = res.data.data
      total.value = res.data.total
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error(`${t('message.getGroupListFailed')}。${error.msg || error}`)
  } finally {
    loading.value = false
  }
}

// 获取用户列表
const getUserList = async () => {
  try {
    const res = await http.request('get', apiMap.user.userList)
    if (res.success) {
      userList.value = res.data.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error(`${t('message.getUserListFailed')}。${error.msg || error}`)
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

// 新增用户组
const handleAdd = () => {
  dialogType.value = 'add'
  form.value = {
    name: '',
    parent: undefined,
    description: ''
  }
  dialogVisible.value = true
}

// 查看详情
const router = useRouter()
const handleViewDetail = (row: UserGroupForm) => {
  router.push({
    path: '/system/group/detail',
    query: { uuid: row.uuid }
  })
}

// 删除用户组
const handleDelete = (row: UserGroupForm) => {
  ElMessageBox.confirm(t('message.deleteConfirm'), t('common.confirm'), {
    type: 'warning'
  }).then(async () => {
    try {
      await http.request('delete', apiMap.group.group, {
        data: { uuid: row.uuid }
      })
      ElMessage.success(t('message.operationSuccess'))
      getUserGroupList()
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
          const res = await http.request('post', apiMap.group.group, { data: form.value })
          if (res.success) {
            ElMessage.success(t('message.createSuccess'))
          } else {
            ElMessage.error(res.msg)
          }
        } else {
          const res = await http.request('put', apiMap.group.group, {
            data: {
              ...form.value,
              uuid: form.value.uuid
            }
          })
          if (res.success) {
            ElMessage.success(t('message.editSuccess'))
          } else {
            ElMessage.error(res.msg)
          }
        }
        dialogVisible.value = false
        getUserGroupList()
      } catch (error) {
        ElMessage.error(dialogType.value === 'add' ? `${t('message.createFailed')}.${error.msg || error}` : `${t('message.editFailed')}.${error.msg || error}`)
      }
    }
  })
}

// 表格选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedGroups.value = selection.map(item => item.uuid)
}

// 批量删除
const handleBatchDelete = async () => {
  if (!selectedGroups.value.length) return

  try {
    await ElMessageBox.confirm(t('message.batchDeleteConfirm'), t('common.confirm'), {
      type: 'warning'
    })

    const res = await http.request('delete', apiMap.group.groupList, {
      data: { uuids: selectedGroups.value }
    })

    if (res.success) {
      ElMessage.success(t('message.operationSuccess'))
      getUserGroupList()
      selectedGroups.value = []
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
  getUserGroupList()
}

// 处理页码改变
const handleCurrentChange = (val: number) => {
  page.value = val
  getUserGroupList()
}

// 处理每页条数改变
const handleSizeChange = (val: number) => {
  pageSize.value = val
  page.value = 1
  getUserGroupList()
}

// 重置搜索
const resetSearch = () => {
  searchForm.value.keyword = ''
  page.value = 1
  getUserGroupList()
}

onMounted(() => {
  if (!hasPerms('system.groupList:read')) {
    ElMessage.error(t('message.noPermissionToAccessPage'))
    router.push('/error/403')
  }
  getUserGroupList()

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

.search-box {
  margin: 0 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style> 