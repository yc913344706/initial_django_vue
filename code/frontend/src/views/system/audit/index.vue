<template>
  <div class="audit-list">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="操作人" class="form-item">
          <el-input
            v-model="searchForm.operator"
            placeholder="搜索操作人"
            clearable
            class="search-input"
          />
        </el-form-item>

        <el-form-item label="模型名称" class="form-item">
          <el-input
            v-model="searchForm.model_name"
            placeholder="搜索模型名称"
            clearable
            class="search-input"
          />
        </el-form-item>

        <el-form-item label="操作类型" class="form-item">
          <el-select 
            v-model="searchForm.action" 
            placeholder="请选择操作类型" 
            clearable
            class="search-input"
          >
            <el-option label="创建" value="CREATE" />
            <el-option label="更新" value="UPDATE" />
            <el-option label="删除" value="DELETE" />
          </el-select>
        </el-form-item>

        <el-form-item label="IP地址" class="form-item">
          <el-input
            v-model="searchForm.ip_address"
            placeholder="搜索IP地址"
            clearable
            class="search-input"
          />
        </el-form-item>

        <el-form-item label="操作时间" class="form-item">
          <el-date-picker
            v-model="searchForm.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            class="date-range-picker"
          />
        </el-form-item>

        <el-form-item label="关键词" class="form-item">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索操作人/记录ID"
            clearable
            class="search-input"
          />
        </el-form-item>

        <el-form-item class="form-item button-group">
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格区域 -->
    <el-table :data="auditList" v-loading="loading" border>
      <el-table-column prop="operator_username" label="操作人" min-width="100" />
      <el-table-column prop="model_name" label="模型名称" min-width="120" />
      <el-table-column prop="record_id" label="记录ID" min-width="180" />
      <el-table-column prop="action_display" label="操作类型" width="140">
        <template #default="{ row }">
          <el-tag :type="getActionTagType(row.action)">
            {{ row.action_display }}
          </el-tag>
        </template>
      </el-table-column>
      <!-- <el-table-column prop="ip_address" label="IP地址" min-width="120" /> -->
      <el-table-column prop="create_time" label="操作时间" min-width="150" />
      <el-table-column label="操作详情" min-width="120">
        <template #default="{ row }">
          <el-button link type="primary" @click="showDetail(row)">
            查看详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
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

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="操作详情"
      width="600px"
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
  action: '',
  ip_address: '',
  date_range: [],
  keyword: ''
})

// 获取操作类型标签样式
const getActionTagType = (action) => {
  const typeMap = {
    'CREATE': 'success',
    'UPDATE': 'warning',
    'DELETE': 'danger'
  }
  return typeMap[action] || 'info'
}

// 构建查询参数
const buildQueryParams = () => {
  const params = { ...searchForm.value }
  if (params.date_range?.length === 2) {
    params.start_date = params.date_range[0]
    params.end_date = params.date_range[1]
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
    action: '',
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
    const res = await http.request('get', import.meta.env.VITE_BACKEND_URL + apiMap.audit.auditLogs, { 
      params: params
    })
    if (res.success) {
      auditList.value = res.data.data
      total.value = res.data.total
    }
  } catch (error) {
    logger.error('获取审计日志失败:', error)
    ElMessage.error('获取审计日志失败')
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

onMounted(() => {
  fetchAuditLogs()
})
</script>

<style lang="scss" scoped>
.audit-list {
  padding: 20px;
  
  .search-card {
    margin-bottom: 20px;
    
    .search-form {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      padding: 16px;
      
      .form-item {
        margin-bottom: 16px;
        margin-right: 0;
        min-width: 280px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .search-input {
          width: 200px;
        }
        
        .date-range-picker {
          width: 360px;
        }
        
        &.button-group {
          min-width: auto;
          margin-left: auto;
          display: flex;
          align-items: flex-start;
          
          .el-button {
            margin-left: 12px;
            
            &:first-child {
              margin-left: 0;
            }
          }
        }
      }
    }
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }

  :deep(.el-table) {
    margin-top: 20px;
  }

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
}
</style> 