<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>{{ $t('page.role.detail') }}</span>
          <div>
            <el-button type="primary" @click="handleEdit" v-if="!isEditing && hasPerms('system.role:update')">{{ $t('common.edit') }}</el-button>
            <el-button @click="$router.back()"
            >{{ $t('common.back') }}</el-button>
          </div>
        </div>
      </template>

      <template v-if="isEditing && hasPerms('system.role:update')">
        <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
          <el-form-item :label="$t('page.role.name')" prop="name">
            <el-input v-model="form.name" :placeholder="$t('page.role.enterName')" />
          </el-form-item>
          <el-form-item :label="$t('page.role.code')" prop="code">
            <el-input v-model="form.code" :placeholder="$t('page.role.enterCode')" />
          </el-form-item>
          <el-form-item :label="$t('page.role.description')" prop="description">
            <el-input v-model="form.description" type="textarea" :placeholder="$t('page.role.enterDescription')" />
          </el-form-item>
          <el-form-item :label="$t('page.role.permission')">
            <el-select
              v-model="form.permissions"
              multiple
              filterable
              :placeholder="$t('page.user.selectPermissionPlaceholder')"
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
            <el-button type="primary" @click="handleSubmit">{{ $t('common.save') }}</el-button>
            <el-button @click="handleCancel">{{ $t('common.cancel') }}</el-button>
          </el-form-item>
        </el-form>
      </template>

      <template v-if="!isEditing && hasPerms('system.role:read')">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="$t('page.role.name')">{{ roleInfo.name }}</el-descriptions-item>
          <el-descriptions-item :label="$t('page.role.code')">{{ roleInfo.code }}</el-descriptions-item>
          <el-descriptions-item :label="$t('page.role.description')">{{ roleInfo.description }}</el-descriptions-item>
          <el-descriptions-item :label="$t('page.user.createTime')">{{ roleInfo.created_time }}</el-descriptions-item>
          <el-descriptions-item :label="$t('page.user.updateTime')">{{ roleInfo.updated_time }}</el-descriptions-item>
        </el-descriptions>

        <div class="section-title">{{ $t('page.role.permission') }}</div>
        <el-table :data="roleInfo.permissions" style="width: 100%; margin-bottom: 20px">
          <el-table-column prop="name" :label="$t('page.permission.name')">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/permission/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" :label="$t('page.role.description')" />
        </el-table>

        <div class="section-title">{{ $t('page.role.user') }} {{ $t('common.list') }}</div>
        <el-table :data="roleInfo.users" style="width: 100%; margin-bottom: 20px">
          <el-table-column prop="username" :label="$t('page.user.username')">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/user/detail?uuid=${row.uuid}`)">{{ row.username }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="nickname" :label="$t('page.user.nickname')" />
          <el-table-column prop="is_active" :label="$t('page.user.status')">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? $t('common.enabled') : $t('common.disabled') }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div class="section-title">{{ $t('page.group.name') }} {{ $t('common.list') }}</div>
        <el-table :data="roleInfo.groups" style="width: 100%">
          <el-table-column prop="name" :label="$t('page.group.name')">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/group/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" :label="$t('page.role.description')" />
        </el-table>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { http } from '@/utils/http'
import { apiMap } from '@/config/api'
import { hasPerms } from "@/utils/auth";
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const route = useRoute()
const router = useRouter()
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
    { required: true, message: t('page.role.enterName'), trigger: 'blur' }
  ],
  code: [
    { required: true, message: t('page.role.enterCode'), trigger: 'blur' }
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
          ElMessage.success(t('message.updateSuccess'))
          isEditing.value = false
          getRoleDetail()
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
  if (!hasPerms('system.role:read')) {
    ElMessage.error(t('message.noPermissionToAccessPage'))
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