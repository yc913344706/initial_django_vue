<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>{{ $t('page.permission.detail') }}</span>
          <div>
            <el-button
            type="primary"
            @click="handleEdit"
            v-if="!isEditing && hasPerms('system.permission:update')"
            >
              {{ $t('common.edit') }}
            </el-button>
            <el-button
            @click="$router.back()"
            >{{ $t('common.back') }}</el-button>
          </div>
        </div>
      </template>

      <template v-if="isEditing && hasPerms('system.permission:update')">
        <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
          <el-form-item :label="$t('page.permission.name')" prop="name">
            <el-input v-model="form.name" :placeholder="$t('page.permission.enterName')" />
          </el-form-item>
        <el-form-item :label="$t('page.permission.code')" prop="code">
          <el-input v-model="form.code" :placeholder="$t('page.permission.enterCode')" />
        </el-form-item>
        <el-form-item :label="$t('page.permission.description')" prop="description">
          <el-input v-model="form.description" type="textarea" :placeholder="$t('page.permission.enterDescription')" />
        </el-form-item>
        <el-form-item :label="$t('page.permission.json')" prop="permission_json">
          <el-input
            v-model="form.permission_json"
            type="textarea"
            :rows="10"
            :placeholder="$t('page.permission.enterJson')"
            @input="handleJsonInput"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">{{ $t('common.save') }}</el-button>
            <el-button @click="handleCancel">{{ $t('common.cancel') }}</el-button>
          </el-form-item>
        </el-form>
      </template>

      <template v-if="!isEditing && hasPerms('system.permission:read')">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="$t('page.permission.name')">{{ permissionInfo.name }}</el-descriptions-item>
          <el-descriptions-item :label="$t('page.permission.code')">{{ permissionInfo.code }}</el-descriptions-item>
          <el-descriptions-item :label="$t('page.permission.type')">
            <el-tag :type="permissionInfo.is_system ? 'danger' : 'success'">
              {{ permissionInfo.is_system ? $t('page.permission.systemPermission') : $t('page.permission.normalPermission') }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('page.permission.description')">{{ permissionInfo.description }}</el-descriptions-item>
          <el-descriptions-item :label="$t('page.user.createTime')">{{ permissionInfo.created_time }}</el-descriptions-item>
          <el-descriptions-item :label="$t('page.user.updateTime')">{{ permissionInfo.updated_time }}</el-descriptions-item>
        </el-descriptions>

        <div class="section-title">{{ $t('page.permission.json') }}</div>
        <pre class="json-viewer">{{ JSON.stringify(permissionInfo.permission_json, null, 2) }}</pre>

        <div class="section-title">{{ $t('page.role.name') }} {{ $t('common.list') }}</div>
        <el-table :data="permissionInfo.roles" style="width: 100%; margin-bottom: 20px">
          <el-table-column prop="name" :label="$t('page.role.name')">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/role/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" :label="$t('page.role.description')" />
        </el-table>

        <div class="section-title">{{ $t('page.role.user') }} {{ $t('common.list') }}</div>
        <el-table :data="permissionInfo.users" style="width: 100%; margin-bottom: 20px">
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
        <el-table :data="permissionInfo.groups" style="width: 100%">
          <el-table-column prop="name" :label="$t('page.group.name')">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/group/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" :label="$t('page.group.description')" />
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
import router from '@/router'

const { t } = useI18n();
const route = useRoute()
const routerInstance = useRouter()
const isEditing = ref(false)
const formRef = ref<FormInstance>()
const permissionInfo = ref({
  uuid: '',
  name: '',
  code: '',
  description: '',
  permission_json: {},
  created_time: '',
  updated_time: '',
  roles: [],
  users: [],
  groups: []
})

const form = ref({
  uuid: '',
  name: '',
  code: '',
  description: '',
  permission_json: ''
})

const rules = {
  name: [
    { required: true, message: t('page.permission.enterName'), trigger: 'blur' }
  ],
  code: [
    { required: true, message: t('page.permission.enterCode'), trigger: 'blur' }
  ],
  permission_json: [
    { required: true, message: t('page.permission.enterJson'), trigger: 'blur' },
    { validator: validateJson, trigger: 'blur' }
  ]
}

// JSON验证
function validateJson(rule: any, value: string, callback: any) {
  if (!value) {
    callback(new Error(t('page.permission.enterJson')))
  } else {
    try {
      JSON.parse(value)
      callback()
    } catch (error) {
      callback(new Error(t('page.permission.jsonFormatError')))
    }
  }
}

// 获取权限详情
const getPermissionDetail = async () => {
  try {
    const res = await http.request('get', apiMap.permission.permission, {
      params: { uuid: route.query.uuid }
    })
    if (res.success) {
      permissionInfo.value = res.data
      form.value.permission_json = JSON.stringify(res.data.permission_json, null, 2)
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
    uuid: permissionInfo.value.uuid,
    name: permissionInfo.value.name,
    code: permissionInfo.value.code,
    description: permissionInfo.value.description,
    permission_json: JSON.stringify(permissionInfo.value.permission_json, null, 2)
  }
  isEditing.value = true
}

// 取消编辑
const handleCancel = () => {
  isEditing.value = false
}

// JSON输入处理
const handleJsonInput = (value: string) => {
  try {
    JSON.parse(value)
  } catch (error) {
    // 输入时不做验证,只在提交时验证
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const submitData = {
          ...form.value,
          permission_json: JSON.parse(form.value.permission_json)
        }
        const res = await http.request('put', apiMap.permission.permission, {
          data: submitData
        })
        if (res.success) {
          ElMessage.success(t('message.updateSuccess'))
          isEditing.value = false
          getPermissionDetail()
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
  if (!hasPerms('system.permission:read')) {
    ElMessage.error(t('message.noPermissionToAccessPage'))
    routerInstance.push('/error/403')
  }
  getPermissionDetail()
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
.json-viewer {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style> 