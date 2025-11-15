<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>{{ t('page.group.detail') }}</span>
          <div>
            <el-button
            type="primary"
            @click="handleEdit"
            v-if="!isEditing && hasPerms('system.group:update')"
            >{{ t('button.edit') }}</el-button>
            <el-button
            @click="$router.back()"
            >{{ t('button.back') }}</el-button>
          </div>
        </div>
      </template>

      <template v-if="isEditing && hasPerms('system.group:update')">
        <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
        <el-form-item :label="t('page.group.name')" prop="name">
          <el-input v-model="form.name" :placeholder="t('page.group.enterName')" />
        </el-form-item>
        <el-form-item :label="t('page.group.parentGroup')">
          <el-select v-model="form.parent" :placeholder="t('page.group.selectParentGroup')" style="width: 100%">
            <el-option :label="t('common.none')" value="undefined" />
            <el-option
              v-for="item in groupList"
              :key="item.uuid"
              :label="item.name"
              :value="item.uuid"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('field.description')" prop="description">
          <el-input v-model="form.description" type="textarea" :placeholder="t('page.group.enterDescription')" />
        </el-form-item>
        <el-form-item :label="t('field.user')">
          <el-select
            v-model="form.users"
            multiple
            filterable
            remote
            :remote-method="getUserList"
            :loading="loading"
            :placeholder="t('page.group.searchUserPlaceholder')"
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
        <el-form-item :label="t('field.role')">
          <el-select
            v-model="form.roles"
            multiple
            filterable
            :placeholder="t('page.group.selectRolePlaceholder')"
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
            v-model="form.permissions"
            multiple
            filterable
            :placeholder="t('page.group.selectPermissionPlaceholder')"
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
          <el-button type="primary" @click="handleSubmit">{{ t('button.save') }}</el-button>
          <el-button @click="handleCancel">{{ t('button.cancel') }}</el-button>
        </el-form-item>
        </el-form>
      </template>

      <template v-if="!isEditing && hasPerms('system.group:read')">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="t('page.group.name')">{{ groupInfo.name }}</el-descriptions-item>
          <el-descriptions-item :label="t('page.group.parentGroup')">{{ parentGroupName }}</el-descriptions-item>
          <el-descriptions-item :label="t('field.description')">{{ groupInfo.description }}</el-descriptions-item>
          <el-descriptions-item :label="t('field.createTime')">{{ groupInfo.created_time }}</el-descriptions-item>
          <el-descriptions-item :label="t('field.updateTime')">{{ groupInfo.updated_time }}</el-descriptions-item>
        </el-descriptions>

        <div class="section-title">{{ t('page.group.userList') }}</div>
        <el-table :data="groupInfo.users" style="width: 100%; margin-bottom: 20px">
          <el-table-column prop="username" :label="t('field.username')" >
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/user/detail?uuid=${row.uuid}`)">{{ row.username }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="nickname" :label="t('field.nickname')" />
          <!-- <el-table-column prop="phone" label="手机号" />
          <el-table-column prop="email" label="邮箱" /> -->
          <el-table-column prop="is_active" :label="t('field.status')">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? t('common.enabled') : t('common.disabled') }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div class="section-title">{{ t('page.group.roleList') }}</div>
        <el-table :data="groupInfo.roles" style="width: 100%; margin-bottom: 20px">
          <el-table-column prop="name" :label="t('field.roleName')" >
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/role/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" :label="t('field.description')" />
        </el-table>

        <div class="section-title">{{ t('page.group.permissionList') }}</div>
        <el-table :data="groupInfo.permissions" style="width: 100%">
          <el-table-column prop="name" :label="t('field.permissionName')" >
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/permission/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" :label="t('field.description')" />
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
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

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
    { required: true, message: t('page.group.enterName'), trigger: 'blur' }
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
    ElMessage.error(`${t('message.getGroupDetailFailed')}。${error.msg || error}`)
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
    ElMessage.error(`${t('message.getGroupListFailed')}。${error.msg || error}`)
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
        ElMessage.error(t('message.searchUserFailed'))
      }
    } catch (error) {
      ElMessage.error(`${t('message.searchUserFailed')}。${error.msg || error}`)
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
          ElMessage.success(t('message.updateSuccess'))
          isEditing.value = false
          getGroupDetail()
        } else {
          ElMessage.error(res.msg)
        }
      } catch (error) {
        ElMessage.error(`${t('message.updateFailed')}。${error.msg || error}`)
      }
    }
  })
}

onMounted(() => {
  if (!hasPerms('system.group:read')) {
    ElMessage.error(t('message.noPermissionToViewGroupDetail'))
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