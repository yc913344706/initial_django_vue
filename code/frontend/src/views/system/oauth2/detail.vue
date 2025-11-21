<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>{{ t('page.oauth2.clientDetail') }}</span>
          <div>
            <el-button
              type="primary"
              @click="handleEdit"
              v-if="!isEditing && hasPerms('system.oauth2Client:update')"
            >{{ t('button.edit') }}</el-button>
            <el-button @click="$router.back()">{{ t('button.back') }}</el-button>
          </div>
        </div>
      </template>

      <template v-if="isEditing && hasPerms('system.oauth2Client:update')">
        <el-form :model="form" label-width="150px" :rules="rules" ref="formRef">
          <el-form-item :label="t('field.clientId')" prop="client_id">
            <el-input 
              v-model="form.client_id" 
              :placeholder="t('page.oauth2.enterClientId')"
              :disabled="true" />
          </el-form-item>
          <el-form-item :label="t('field.clientName')" prop="client_name">
            <el-input v-model="form.client_name" :placeholder="t('page.oauth2.enterClientName')" />
          </el-form-item>
          <el-form-item :label="t('field.grantTypes')" prop="grant_types">
            <el-select
              v-model="form.grant_types"
              multiple
              filterable
              :placeholder="t('page.oauth2.selectGrantTypes')"
              style="width: 100%"
              disabled
            >
              <el-option
                v-for="item in grantTypeOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('field.responseTypes')" prop="response_types">
            <el-select
              v-model="form.response_types"
              multiple
              filterable
              :placeholder="t('page.oauth2.selectResponseTypes')"
              style="width: 100%"
              disabled
            >
              <el-option
                v-for="item in responseTypeOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('field.redirectUris')" prop="redirect_uris_text">
            <el-input
              v-model="form.redirect_uris_text"
              type="textarea"
              :rows="3"
              :placeholder="t('page.oauth2.enterRedirectUris')"
            />
          </el-form-item>
          <el-form-item :label="t('field.scope')" prop="scope">
            <el-input v-model="form.scope" :placeholder="t('page.oauth2.enterScope')" />
          </el-form-item>
          <el-form-item :label="t('field.tokenAuthMethod')" prop="token_endpoint_auth_method">
            <el-select
              v-model="form.token_endpoint_auth_method"
              :placeholder="t('page.oauth2.selectTokenAuthMethod')"
              style="width: 100%"
              disabled
            >
              <el-option
                v-for="item in tokenAuthMethodOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSubmit">{{ t('common.save') }}</el-button>
            <el-button @click="handleCancel">{{ t('common.cancel') }}</el-button>
          </el-form-item>
        </el-form>
      </template>

      <template v-if="!isEditing && hasPerms('system.oauth2Client:read')">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="t('field.clientId')">{{ clientInfo.client_id }}</el-descriptions-item>
          <el-descriptions-item :label="t('field.clientName')">{{ clientInfo.client_name }}</el-descriptions-item>
          <el-descriptions-item :label="t('field.grantTypes')">
            <el-tag 
              v-for="grantType in clientInfo.grant_types" 
              :key="grantType" 
              size="small" 
              class="mr-1">
              {{ grantType }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('field.responseTypes')">
            <el-tag 
              v-for="responseType in clientInfo.response_types" 
              :key="responseType" 
              type="info" 
              size="small" 
              class="mr-1">
              {{ responseType }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('field.redirectUris')">
            <div v-for="uri in clientInfo.redirect_uris" :key="uri" class="mb-1">{{ uri }}</div>
          </el-descriptions-item>
          <el-descriptions-item :label="t('field.scope')">{{ clientInfo.scope }}</el-descriptions-item>
          <el-descriptions-item :label="t('field.tokenAuthMethod')">
            {{ tokenAuthMethodOptions.find(opt => opt.value === clientInfo.token_endpoint_auth_method)?.label }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('field.createdAt')">
            {{ new Date().toLocaleString() }} <!-- Hydra doesn't provide creation date in client info -->
          </el-descriptions-item>
        </el-descriptions>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { http } from '@/utils/http'
import { apiMap } from '@/config/api'
import { hasPerms } from "@/utils/auth";
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

interface OAuth2Client {
  client_id: string
  client_name: string
  client_secret?: string
  grant_types: string[]
  response_types: string[]
  redirect_uris: string[]
  scope: string
  token_endpoint_auth_method: string
  redirect_uris_text?: string
}

// 选项配置
const grantTypeOptions = [
  { value: 'authorization_code', label: 'Authorization Code' },
  { value: 'refresh_token', label: 'Refresh Token' },
  { value: 'client_credentials', label: 'Client Credentials' },
  { value: 'implicit', label: 'Implicit' }
]

const responseTypeOptions = [
  { value: 'code', label: 'Code' },
  { value: 'token', label: 'Token' },
  { value: 'id_token', label: 'ID Token' }
]

const tokenAuthMethodOptions = [
  { value: 'client_secret_post', label: 'Client Secret Post' },
  { value: 'client_secret_basic', label: 'Client Secret Basic' },
  { value: 'none', label: 'None (Public Client)' }
]

const clientInfo = ref<OAuth2Client>({
  client_id: '',
  client_name: '',
  grant_types: [],
  response_types: [],
  redirect_uris: [],
  scope: '',
  token_endpoint_auth_method: 'client_secret_post'
})

const form = ref<OAuth2Client>({ ...clientInfo.value, redirect_uris_text: '' })
const isEditing = ref(false)
const formRef = ref<FormInstance>()

const rules = {
  client_name: [
    { required: true, message: t('page.oauth2.enterClientName'), trigger: 'blur' }
  ],
  redirect_uris_text: [
    { required: true, message: t('page.oauth2.enterRedirectUris'), trigger: 'blur' }
  ],
  scope: [
    { required: true, message: t('page.oauth2.enterScope'), trigger: 'blur' }
  ]
}

// 加载客户端详情
const loadClientDetail = async () => {
  const clientId = route.query.client_id as string
  if (!clientId) {
    ElMessage.error(t('message.missingClientId'))
    return
  }

  try {
    const res = await http.request('get', apiMap.oauth2.manageClient, {
      params: { client_id: clientId }
    })

    if (res.success && res.data) {
      const client = res.data
      // 转换 redirect_uris 为文本格式
      const redirect_uris_text = client.redirect_uris ? client.redirect_uris.join('\n') : ''
      clientInfo.value = { ...client, redirect_uris_text }
      form.value = { ...client, redirect_uris_text }
    } else {
      ElMessage.error(res.msg || t('message.getClientDetailFailed'))
    }
  } catch (error: any) {
    ElMessage.error(`${t('message.getClientDetailFailed')}。${error.msg || error}`)
  }
}

// 编辑
const handleEdit = () => {
  isEditing.value = true
  form.value = { ...clientInfo.value }
}

// 保存
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 处理重定向URI格式
        const redirectUrisArray = form.value.redirect_uris_text
          ? form.value.redirect_uris_text.split('\n').map(uri => uri.trim()).filter(uri => uri)
          : [];

        const clientData = {
          ...form.value,
          redirect_uris: redirectUrisArray,
          redirect_uris_text: undefined // 移除临时字段
        }

        const res = await http.request('put', apiMap.oauth2.manageClient, { 
          data: clientData 
        })

        if (res.success) {
          ElMessage.success(t('message.editSuccess'))
          isEditing.value = false
          clientInfo.value = { ...form.value }
        } else {
          ElMessage.error(res.msg || t('message.editFailed'))
        }
      } catch (error: any) {
        ElMessage.error(`${t('message.editFailed')}。${error.msg || error}`)
      }
    }
  })
}

// 取消编辑
const handleCancel = () => {
  isEditing.value = false
  form.value = { ...clientInfo.value }
}

onMounted(() => {
  if (!hasPerms('system.oauth2Client:read')) {
    ElMessage.error(t('message.noPermissionToViewOauth2Client'))
    // In actual implementation, you might want to redirect to error page
  } else {
    loadClientDetail()
  }
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mr-1 {
  margin-right: 4px;
}

.mb-1 {
  margin-bottom: 4px;
}
</style>