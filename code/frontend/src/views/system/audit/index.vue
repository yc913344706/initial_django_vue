<template>
  <div class="system-page" v-if="hasPerms('system.auditList:read')">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <div class="search-form">
        <div class="form-item">
          <span class="label">{{ $t('page.audit.operator') }}</span>
          <el-input
            v-model="searchForm.operator"
            :placeholder="$t('page.audit.searchOperator')"
            clearable
            class="search-input"
            @keyup.enter="handleSearch"
          />
        </div>

        <div class="form-item">
          <span class="label">{{ $t('page.audit.model') }}</span>
          <el-input
            v-model="searchForm.model_name"
            :placeholder="$t('page.audit.searchModelName')"
            clearable
            class="search-input"
            @keyup.enter="handleSearch"
          />
        </div>

        <div class="form-item">
          <span class="label">{{ $t('page.audit.action') }}</span>
          <el-select
            v-model="searchForm.action"
            :placeholder="$t('page.audit.selectActionType')"
            clearable
            multiple
            collapse-tags
            class="search-input"
            @keyup.enter="handleSearch"
          >
            <el-option
              v-for="config in auditConfig.action_configs"
              :key="config.value"
              :label="config.display"
              :value="config.value"
            />
          </el-select>
        </div>

        <div class="form-item">
          <span class="label">{{ $t('page.audit.ip') }}</span>
          <el-input
            v-model="searchForm.ip_address"
            :placeholder="$t('page.audit.searchIp')"
            clearable
            class="search-input"
            @keyup.enter="handleSearch"
          />
        </div>

        <div class="form-item">
          <span class="label">{{ $t('page.audit.time') }}</span>
          <el-date-picker
            v-model="searchForm.date_range"
            type="daterange"
            range-separator="-"
            start-placeholder="$t('page.audit.startDate')"
            end-placeholder="$t('page.audit.endDate')"
            value-format="YYYY-MM-DD"
            class="date-range-picker"
            @keyup.enter="handleSearch"
          />
        </div>

        <div class="form-item">
          <span class="label">{{ $t('page.audit.keyword') }}</span>
          <el-input
            v-model="searchForm.keyword"
            :placeholder="$t('page.audit.searchKeyword')"
            clearable
            class="search-input"
            @keyup.enter="handleSearch"
          />
        </div>

        <div class="form-item button-group">
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            {{ $t('common.search') }}
          </el-button>
          <el-button @click="resetSearch">{{ $t('common.reset') }}</el-button>
        </div>
      </div>
    </el-card>

    <!-- 表格区域 -->
    <el-card class="table-card">
      <el-table :data="auditList" v-loading="loading" border>
        <el-table-column prop="operator_username" :label="$t('page.audit.operator')" min-width="100" />
        <el-table-column prop="model_name" :label="$t('page.audit.model')" min-width="120" />
        <el-table-column prop="record_id" :label="$t('page.audit.recordId')" min-width="180" />
        <el-table-column prop="action_display" :label="$t('page.audit.action')" width="140">
          <template #default="{ row }">
            <el-tag :type="getActionTagType(row.action)">
              {{ row.action_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" :label="$t('page.audit.time')" min-width="150" />
        <el-table-column :label="$t('page.audit.content')" min-width="120">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)">
              {{ $t('common.detail') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="$t('page.audit.detail')"
      width="600px"
      class="detail-dialog"
    >
      <pre class="detail-content">{{ currentDetail }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { http } from '@/utils/http'
import { apiMap } from '@/config/api'
import logger from '@/utils/logger'
import { hasPerms } from "@/utils/auth";
import router from '@/router'
import { useI18n } from 'vue-i18n'
import '@/style/system.scss'

const { t } = useI18n()
const loading = ref(false)
const auditList = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const detailDialogVisible = ref(false)
const currentDetail = ref('')

const searchForm = ref({
  operator: '',
  model_name: '',
  action: [],  // 改为数组以支持多选
  ip_address: '',
  date_range: [],
  keyword: ''
})

// 审计配置数据
const auditConfig = ref({
  action_configs: []
})

// 获取审计配置
const fetchAuditConfig = async () => {
  try {
    const res = await http.request('get', apiMap.audit.config)
    if (res.success) {
      auditConfig.value = res.data
    } else {
      logger.error('获取审计配置失败:', res.msg)
      ElMessage.error(`${t('message.getPermissionListFailed')}: ${res.msg}`)
    }
  } catch (error) {
    logger.error('获取审计配置失败:', error)
    ElMessage.error(`${t('message.getPermissionListFailed')}: ${error.msg || error}`)
  }
}

// 获取操作类型标签样式
const getActionTagType = (action) => {
  const config = auditConfig.value.action_configs.find(item => item.value === action)
  if (config) {
    return config.tag_type
  }
  return 'info' // 默认样式
}

// 构建查询参数
const buildQueryParams = () => {
  const params = { ...searchForm.value }
  if (params.date_range?.length === 2) {
    params.start_date = params.date_range[0]
    params.end_date = params.date_range[1]
  }
  // 如果action是数组，将其转换为逗号分隔的字符串
  if (Array.isArray(params.action) && params.action.length > 0) {
    params.action = params.action.join(',')
  } else if (params.action === null || params.action === '') {
    // 如果是空值，删除该参数
    delete params.action
  }
  delete params.date_range
  return params
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  fetchAuditLogs()
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    operator: '',
    model_name: '',
    action: [],
    ip_address: '',
    date_range: [],
    keyword: ''
  }
  handleSearch()
}

// 获取审计日志列表
const fetchAuditLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...buildQueryParams()
    }
    const res = await http.request('get', apiMap.audit.auditLogs, {
      params: params
    })
    if (res.success) {
      auditList.value = res.data.data
      total.value = res.data.total
    }
  } catch (error) {
    logger.error('获取审计日志失败:', error)
    ElMessage.error(`${t('message.getPermissionListFailed')}。${error.msg || error}`)
  } finally {
    loading.value = false
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchAuditLogs()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchAuditLogs()
}

// 显示详情
const showDetail = (row) => {
  currentDetail.value = JSON.stringify(row.detail, null, 2)
  detailDialogVisible.value = true
}

onMounted(async () => {
  if (!hasPerms('system.auditList:read')) {
    ElMessage.error(t('message.noPermissionToAccessPage'))
    router.push('/error/403')
  }
  // 先获取配置，再获取审计日志
  await fetchAuditConfig()
  fetchAuditLogs()
})
</script>

<style lang="scss" scoped>
:deep(.el-tag) {
  min-width: 80px;
  text-align: center;
}

.detail-content {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: monospace;
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
}
</style> 