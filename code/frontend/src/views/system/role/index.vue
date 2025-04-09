<template>
  <div class="system-page" v-if="hasPerms('system.roleList:read')">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <div class="search-form">
        <div class="form-item">
          <span class="label">关键词</span>
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索角色名称/角色代码"
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
            :disabled="!selectedRoles.length"
            v-if="hasPerms('system.roleList:delete')"
          >批量删除</el-button>
          <el-button 
            type="primary" 
            @click="handleAdd"
            v-if="hasPerms('system.roleList:create')"
          >新增</el-button>
        </div>
      </div>
    </el-card>

    <!-- 表格区域 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="roleList"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="角色名称" />
        <el-table-column prop="code" label="角色代码" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" width="300">
          <template #default="scope">
            <el-button type="info" size="small" @click="handleViewDetail(scope.row)">查看详情</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)"
            v-if="hasPerms('system.role:delete')"
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
      :title="dialogType === 'add' ? '新增角色' : '编辑角色'"
      width="50%"
    >
      <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色代码" prop="code">
          <el-input v-model="form.code" placeholder="请输入角色代码" />
        </el-form-item>
        <el-form-item label="权限" prop="permissions">
          <el-select
            v-model="form.permissions"
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
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
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

const roleList = ref([])
const permissionList = ref([])
const dialogVisible = ref(false)
const dialogType = ref('add')
const formRef = ref<FormInstance>()
const form = ref({
  name: '',
  code: '',
  permissions: [],
  description: ''
})
const selectedRoles = ref<string[]>([])

const rules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入角色代码', trigger: 'blur' }
  ],
  permissions: [
    { required: true, message: '请选择权限', trigger: 'change' }
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

// 获取角色列表
const getRoleList = async () => {
  try {
    loading.value = true
    const params = {
      page: page.value,
      page_size: pageSize.value,
      search: searchForm.value.keyword
    }
    const res = await http.request(
      "get",
      apiMap.role.roleList,
      { params: params }
    );
    if (res.success) {
      roleList.value = res.data.data;
      total.value = res.data.total;
    } else {
      ElMessage.error(res.msg);
    }
  } catch (error) {
    ElMessage.error("获取角色列表失败");
  } finally {
    loading.value = false
  }
}

// 获取权限列表
const getPermissionList = async () => {
  try {
    const res = await http.request(
      "get",
      apiMap.permission.permissionList
    );
    if (res.success) {
      permissionList.value = res.data.data;
    } else {
      ElMessage.error(res.msg);
    }
  } catch (error) {
    ElMessage.error('获取权限列表失败')
  }
}

// 新增角色
const handleAdd = () => {
  dialogType.value = 'add'
  form.value = {
    name: '',
    code: '',
    permissions: [],
    description: ''
  }
  dialogVisible.value = true
}

// 查看详情
const handleViewDetail = (row) => {
  router.push({
    path: '/system/role/detail',
    query: { uuid: row.uuid }
  })
}

// 删除角色
const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该角色吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      const res = await http.request(
        "delete",
        apiMap.role.role,
        { data: { uuid: row.uuid } }
      );
      if (res.success) {
        ElMessage.success("删除成功");
        getRoleList();
      } else {
        ElMessage.error(res.msg);
      }
    } catch (error) {
      ElMessage.error("删除失败");
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
          const res = await http.request(
            "post",
            apiMap.role.role,
            { data: form.value }
          );
          if (res.success) {
            ElMessage.success('新增成功')
          } else {
            ElMessage.error(res.msg);
          }
          dialogVisible.value = false
          getRoleList()
        } else {
          const res = await http.request(
            "put",
            apiMap.role.role,
            { data: form.value }
          );
          if (res.success) {
            ElMessage.success('编辑成功')
          } else {
            ElMessage.error(res.msg);
          }
          dialogVisible.value = false
          getRoleList()
        }
      } catch (error) {
        ElMessage.error(dialogType.value === 'add' ? '新增失败' : '编辑失败')
      }
    }
  })
}

// 表格选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedRoles.value = selection.map(item => item.uuid)
}

// 批量删除
const handleBatchDelete = async () => {
  if (!selectedRoles.value.length) return
  
  try {
    await ElMessageBox.confirm('确定要删除选中的角色吗?', '提示', {
      type: 'warning'
    })
    
    const res = await http.request('delete', apiMap.role.roleList, {
      data: { uuids: selectedRoles.value }
    })
    
    if (res.success) {
      ElMessage.success('删除成功')
      getRoleList()
      selectedRoles.value = []
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
  getRoleList()
}

// 处理页码改变
const handleCurrentChange = (val: number) => {
  page.value = val
  getRoleList()
}

// 处理每页条数改变
const handleSizeChange = (val: number) => {
  pageSize.value = val
  page.value = 1
  getRoleList()
}

// 重置搜索
const resetSearch = () => {
  searchForm.value.keyword = ''
  page.value = 1
  getRoleList()
}

onMounted(() => {
  if (!hasPerms('system.roleList:read')) {
    ElMessage.error('您没有权限查看角色列表')
    router.push('/error/403')
  }
  getRoleList()
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