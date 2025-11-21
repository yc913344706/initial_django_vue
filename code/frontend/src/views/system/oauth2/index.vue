<template>
  <div class="system-page" v-if="hasPerms('system.oauth2ClientList:read')">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <div class="search-form">
        <div class="form-item">
          <span class="label">{{ t('page.oauth2.clientId') }}</span>
          <el-input
            v-model="searchForm.client_id"
            :placeholder="t('page.oauth2.searchClientId')"
            clearable
            class="search-input"
            @keyup.enter="handleSearch"
          />
        </div>

        <div class="form-item">
          <span class="label">{{ t('page.oauth2.clientName') }}</span>
          <el-input
            v-model="searchForm.client_name"
            :placeholder="t('page.oauth2.searchClientName')"
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
            :disabled="!selectedClients.length"
            v-if="hasPerms('system.oauth2ClientList:delete')"
          >{{ t('button.batchDelete') }}</el-button>
          <el-button
            type="primary"
            @click="handleAdd"
            v-if="hasPerms('system.oauth2ClientList:create')"
          >{{ t('button.create') }}</el-button>
        </div>
      </div>
    </el-card>

    <!-- 表格区域 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="clientList"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="client_id" :label="t('field.clientId')" />
        <el-table-column prop="client_name" :label="t('field.clientName')" />
        <el-table-column prop="grant_types" :label="t('field.grantTypes')">
          <template #default="{ row }">
            <el-tag 
              v-for="grantType in row.grant_types" 
              :key="grantType" 
              size="small" 
              class="mr-1">
              {{ grantType }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="response_types" :label="t('field.responseTypes')">
          <template #default="{ row }">
            <el-tag 
              v-for="responseType in row.response_types" 
              :key="responseType" 
              type="info" 
              size="small" 
              class="mr-1">
              {{ responseType }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="scope" :label="t('field.scope')" show-overflow-tooltip />
        <el-table-column :label="t('table.actions')" width="300">
          <template #default="scope">
            <el-button type="info" size="small" @click="handleViewDetail(scope.row)">{{ t('button.detail') }}</el-button>
            <el-button
              type="primary"
              size="small"
              @click="handleEdit(scope.row)"
              v-if="hasPerms('system.oauth2Client:update')"
            >{{ t('button.edit') }}</el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(scope.row)"
              v-if="hasPerms('system.oauth2Client:delete')"
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

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? t('dialog.title.create') : t('dialog.title.edit')"
      width="60%"
    >
      <el-form :model="form" label-width="150px" :rules="rules" ref="formRef">
        <el-form-item :label="t('field.clientName')" prop="client_name">
          <el-input v-model="form.client_name" :placeholder="t('page.oauth2.enterClientName')" />
        </el-form-item>
        <!-- 客户端ID由系统生成，仅在编辑时显示 -->
        <el-form-item :label="t('field.clientId')" v-if="dialogType === 'edit'">
          <el-input v-model="form.client_id" disabled />
        </el-form-item>
        <!-- 仅在创建时显示客户端密钥 -->
        <el-form-item :label="t('field.clientSecret')" v-if="showClientSecret">
          <el-input v-model="form.client_secret" type="password" readonly show-password>
            <template #append>
              <el-button @click="copyToClipboard(form.client_secret)">
                {{ t('button.copy') }}
              </el-button>
            </template>
          </el-input>
          <div class="form-help">{{ t('page.oauth2.clientSecretHelp') }}</div>
        </el-form-item>
        <el-form-item :label="t('field.grantTypes')" prop="grant_types">
          <el-select
            v-model="form.grant_types"
            multiple
            filterable
            :placeholder="t('page.oauth2.selectGrantTypes')"
            style="width: 100%"
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
          >
            <el-option
              v-for="item in responseTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('field.redirectUris')" prop="redirect_uris">
          <el-input
            v-model="form.redirect_uris_text"
            type="textarea"
            :rows="3"
            :placeholder="t('page.oauth2.enterRedirectUris')"
          />
          <div class="form-help">{{ t('page.oauth2.redirectUrisHelp') }}</div>
        </el-form-item>
        <el-form-item :label="t('field.scope')" prop="scope">
          <el-input v-model="form.scope" :placeholder="t('page.oauth2.enterScope')" />
          <div class="form-help">{{ t('page.oauth2.scopeHelp') }}</div>
        </el-form-item>
        <el-form-item :label="t('field.tokenAuthMethod')" prop="token_endpoint_auth_method">
          <el-select
            v-model="form.token_endpoint_auth_method"
            :placeholder="t('page.oauth2.selectTokenAuthMethod')"
            style="width: 100%"
          >
            <el-option
              v-for="item in tokenAuthMethodOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
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
import { hasPerms } from "@/utils/auth";
import { Search } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import '@/style/system.scss'

const { t } = useI18n()

interface OAuth2Client {
  client_id: string
  client_name: string
  client_secret?: string
  grant_types: string[]
  response_types: string[]
  redirect_uris: string[]
  scope: string
  token_endpoint_auth_method: string
  redirect_uris_text?: string // 用于表单输入的换行分隔字符串
}

interface SearchForm {
  client_id: string
  client_name: string
}

const clientList = ref<OAuth2Client[]>([])
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const showClientSecret = ref(false) // 控制客户端密钥的显示
const formRef = ref<FormInstance>()
const form = ref<OAuth2Client>({
  client_id: '',
  client_name: '',
  client_secret: '',
  grant_types: [],
  response_types: [],
  redirect_uris: [],
  scope: 'openid profile email',
  token_endpoint_auth_method: 'client_secret_post',
  redirect_uris_text: ''
})

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

const rules = {
  client_name: [
    { required: true, message: t('page.oauth2.enterClientName'), trigger: 'blur' }
  ],
  grant_types: [
    { required: true, message: t('page.oauth2.selectGrantTypes'), trigger: 'change' }
  ],
  response_types: [
    { required: true, message: t('page.oauth2.selectResponseTypes'), trigger: 'change' }
  ],
  redirect_uris_text: [
    { required: true, message: t('page.oauth2.enterRedirectUris'), trigger: 'blur' }
  ],
  scope: [
    { required: true, message: t('page.oauth2.enterScope'), trigger: 'blur' }
  ]
}

const loading = ref(false)

// 分页相关
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 搜索相关
const searchForm = ref<SearchForm>({
  client_id: '',
  client_name: ''
})

// 选中项
const selectedClients = ref<string[]>([])

// 获取客户端列表
const getClientList = async () => {
  try {
    loading.value = true
    // Hydra Admin API doesn't have pagination, we'll get all and filter locally
    const res = await http.request('get', apiMap.oauth2.manageClient, {})
    if (res.success) {
      // Apply search filters
      const filteredList = res.data?.filter(client => {
        return (
          (!searchForm.value.client_id || client.client_id.includes(searchForm.value.client_id)) &&
          (!searchForm.value.client_name || client.client_name?.includes(searchForm.value.client_name))
        )
      }) || []
      
      // Apply pagination
      const start = (page.value - 1) * pageSize.value
      const end = start + pageSize.value
      clientList.value = filteredList.slice(start, end)
      total.value = filteredList.length
    } else {
      ElMessage.error(res.msg || t('message.getClientListFailed'))
    }
  } catch (error: any) {
    ElMessage.error(`${t('message.getClientListFailed')}。${error.msg || error}`)
  } finally {
    loading.value = false
  }
}

// 查看详情
const handleViewDetail = (row: OAuth2Client) => {
  // 跳转到详情页，暂时用编辑功能代替
  handleEdit(row)
  // 在实际实现中，可以有独立的详情页面
}

// 删除客户端
const handleDelete = async (row: OAuth2Client) => {
  try {
    await ElMessageBox.confirm(
      t('message.deleteConfirm').replace('{name}', row.client_id),
      t('common.tip'),
      { type: 'warning' }
    )

    const res = await http.request('delete', apiMap.oauth2.manageClient, {
      data: { client_id: row.client_id }
    })

    if (res.success) {
      ElMessage.success(t('message.deleteSuccess'))
      getClientList() // 刷新列表
    } else {
      ElMessage.error(res.msg || t('message.deleteFailed'))
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`${t('message.deleteFailed')}。${error.msg || error}`)
    }
  }
}

// 表格选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedClients.value = selection.map(item => item.client_id)
}

// 批量删除
const handleBatchDelete = async () => {
  if (!selectedClients.value.length) return

  try {
    await ElMessageBox.confirm(
      t('message.batchDeleteConfirm').replace('{count}', selectedClients.value.length.toString()),
      t('common.tip'),
      { type: 'warning' }
    )

    for (const clientId of selectedClients.value) {
      await http.request('delete', apiMap.oauth2.manageClient, {
        data: { client_id: clientId }
      })
    }

    ElMessage.success(t('message.deleteSuccess'))
    selectedClients.value = []
    getClientList() // 刷新列表
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`${t('message.deleteFailed')}。${error.msg || error}`)
    }
  }
}

// 处理搜索
const handleSearch = () => {
  page.value = 1
  getClientList()
}

// 处理页码改变
const handleCurrentChange = (val: number) => {
  page.value = val
  getClientList()
}

// 处理每页条数改变
const handleSizeChange = (val: number) => {
  pageSize.value = val
  page.value = 1
  getClientList()
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    client_id: '',
    client_name: ''
  }
  page.value = 1
  getClientList()
}

// 复制到剪贴板
const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success(t('message.passwordCopiedToClipboard'));
  } catch (err) {
    ElMessage.error(t('message.copyFailedManual'));
    // 如果API失败，提示用户手动复制
    console.error('Failed to copy: ', err);
  }
}

// 新增客户端
const handleAdd = () => {
  dialogType.value = 'add'
  form.value = {
    client_id: '',
    client_name: '',
    client_secret: '', // 实际值将在API响应中设置
    grant_types: [],
    response_types: [],
    redirect_uris: [],
    scope: 'openid profile email',
    token_endpoint_auth_method: 'client_secret_post',
    redirect_uris_text: ''
  }
  showClientSecret.value = false // 初始隐藏密钥
  dialogVisible.value = true
}

// 编辑客户端
const handleEdit = (row: OAuth2Client) => {
  dialogType.value = 'edit'
  // 转换 redirect_uris 为文本格式
  const redirect_uris_text = row.redirect_uris ? row.redirect_uris.join('\n') : ''
  form.value = { ...row, redirect_uris_text }
  dialogVisible.value = true
}

// 提交表单
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
          redirect_uris_text: undefined, // 移除临时字段
          // 让服务端自动生成client_id
          client_id: undefined  // 移除前端指定的ID，让服务端自动生成
        }

        let res;
        if (dialogType.value === 'add') {
          res = await http.request('post', apiMap.oauth2.manageClient, { data: clientData })
        } else {
          res = await http.request('put', apiMap.oauth2.manageClient, { data: clientData })
        }

        if (res.success) {
          if (dialogType.value === 'add' && res.data?.client_secret) {
            // 创建成功，显示生成的密钥
            form.value.client_secret = res.data.client_secret;
            showClientSecret.value = true;
            // 显示信息提醒用户保存密钥
            ElMessage.info(t('message.clientSecretGeneratedNotice') || '请立即保存客户端密钥，之后将无法再次查看');
          }

          ElMessage.success(
            dialogType.value === 'add'
              ? t('message.createSuccess')
              : t('message.editSuccess')
          )

          if (dialogType.value !== 'add') {
            // 编辑时直接关闭对话框
            dialogVisible.value = false
            getClientList() // 刷新列表
          }
          // 如果是创建，让用户先保存密钥再关闭
        } else {
          ElMessage.error(res.msg ||
            (dialogType.value === 'add' ? t('message.createFailed') : t('message.editFailed'))
          )
        }
      } catch (error: any) {
        ElMessage.error(
          `${dialogType.value === 'add' ? t('message.createFailed') : t('message.editFailed')}。${error.msg || error}`
        )
      }
    }
  })
}

onMounted(() => {
  if (!hasPerms('system.oauth2ClientList:read')) {
    ElMessage.error(t('message.noPermissionToViewOauth2ClientList'))
    // In actual implementation, you might want to redirect to error page
  } else {
    getClientList()
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

.mr-1 {
  margin-right: 4px;
}

.form-help {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>