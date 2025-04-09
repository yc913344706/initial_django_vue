<template>
  <div class="system-page" v-if="hasPerms('system.permissionList:read')">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <div class="search-form">
        <div class="form-item">
          <span class="label">关键词</span>
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索权限名称/权限代码"
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
            :disabled="!selectedPermissions.length"
            v-if="hasPerms('system.permissionList:delete')"
          >批量删除</el-button>
          <el-button 
            type="primary" 
            @click="handleAdd"
            v-if="hasPerms('system.permissionList:create')"
          >新增</el-button>
        </div>
      </div>
    </el-card>

    <!-- 表格区域 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="permissionList"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="权限名称" />
        <el-table-column prop="code" label="权限代码" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="info" size="small" @click="handleViewDetail(scope.row)">查看详情</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)"
              v-if="hasPerms('system.permission:delete')"
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
      :title="dialogType === 'add' ? '新增权限' : '编辑权限'"
      width="50%"
    >
      <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入权限名称" />
        </el-form-item>
        <el-form-item label="权限代码" prop="code">
          <el-input v-model="form.code" placeholder="请输入权限代码" />
        </el-form-item>
        <el-form-item label="权限JSON" prop="permission_json">
          <el-input
            v-model="form.permission_json"
            type="textarea"
            :rows="10"
            placeholder="请输入权限JSON"
            @input="handleJsonInput"
          />
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
import { ref, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import type { FormInstance } from "element-plus";
import { http } from "@/utils/http";
import { apiMap } from "@/config/api";
import { hasPerms } from "@/utils/auth";
import router from '@/router'
import logger from '@/utils/logger'
import { Search } from '@element-plus/icons-vue'
import '@/style/system.scss'

const permissionList = ref([]);
const dialogVisible = ref(false);
const dialogType = ref("add");
const formRef = ref<FormInstance>();
const form = ref({
  name: "",
  code: "",
  permission_json: "",
  description: ""
});

const rules = {
  name: [{ required: true, message: "请输入权限名称", trigger: "blur" }],
  code: [{ required: true, message: "请输入权限代码", trigger: "blur" }],
  permission_json: [
    { required: true, message: "请输入权限JSON", trigger: "blur" }
  ]
};

const selectedPermissions = ref<string[]>([])
const loading = ref(false)

// 分页相关
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 搜索相关
const searchForm = ref({
  keyword: ''
})

// 获取权限列表
const getPermissionList = async () => {
  try {
    loading.value = true
    const params = {
      page: page.value,
      page_size: pageSize.value,
      search: searchForm.value.keyword
    }
    const res = await http.request(
      "get",
      apiMap.permission.permissionList,
      { params: params }
    );
    if (res.success) {
      permissionList.value = res.data.data;
      total.value = res.data.total;
    } else {
      ElMessage.error(res.msg);
    }
  } catch (error) {
    ElMessage.error("获取权限列表失败");
  } finally {
    loading.value = false
  }
};

// 新增权限
const handleAdd = () => {
  dialogType.value = "add";
  form.value = {
    name: "",
    code: "",
    permission_json: "",
    description: ""
  };
  dialogVisible.value = true;
};

// 编辑权限
const handleEdit = row => {
  dialogType.value = "edit";
  form.value = { ...row };
  dialogVisible.value = true;
};

// 查看详情
const handleViewDetail = row => {
  router.push({
    path: '/system/permission/detail',
    query: { uuid: row.uuid }
  })
}

// 删除权限
const handleDelete = row => {
  ElMessageBox.confirm("确认删除该权限吗？", "提示", {
    type: "warning"
  }).then(async () => {
    try {
      const res = await http.request(
        "delete",
        apiMap.permission.permission,
        { data: { uuid: row.uuid } }
      );
      if (res.success) {
        ElMessage.success("删除成功");
        getPermissionList();
      } else {
        ElMessage.error(res.msg);
      }
    } catch (error) {
      ElMessage.error("删除失败");
    }
  });
};

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
  if (!formRef.value) return;

  await formRef.value.validate(async valid => {
    if (valid) {
      try {
        const submitData = {
          ...form.value,
          permission_json: JSON.parse(form.value.permission_json)
        }
        if (dialogType.value === "add") {
          const res = await http.request(
            "post",
            apiMap.permission.permission,
            { data: submitData }
          );
          if (res.success) {
            ElMessage.success("新增成功");
          } else {
            ElMessage.error(res.msg);
          }
        } else {
          const res = await http.request(
            "put",
            apiMap.permission.permission,
            { data: submitData }
          );
          if (res.success) {
            ElMessage.success("编辑成功");
          } else {
            ElMessage.error(res.msg);
          }
        }
        dialogVisible.value = false;
        getPermissionList();
      } catch (error) {
        logger.error(error)
        ElMessage.error(dialogType.value === "add" ? "新增失败" : "编辑失败");
      }
    }
  });
};

// 表格选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedPermissions.value = selection.map(item => item.uuid)
}

// 批量删除
const handleBatchDelete = async () => {
  if (!selectedPermissions.value.length) return
  
  try {
    await ElMessageBox.confirm('确定要删除选中的权限吗?', '提示', {
      type: 'warning'
    })
    
    const res = await http.request('delete', apiMap.permission.permissionList, {
      data: { uuids: selectedPermissions.value }
    })
    
    if (res.success) {
      ElMessage.success('删除成功')
      getPermissionList()
      selectedPermissions.value = []
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
  getPermissionList()
}

// 处理页码改变
const handleCurrentChange = (val: number) => {
  page.value = val
  getPermissionList()
}

// 处理每页条数改变
const handleSizeChange = (val: number) => {
  pageSize.value = val
  page.value = 1
  getPermissionList()
}

// 重置搜索
const resetSearch = () => {
  searchForm.value.keyword = ''
  page.value = 1
  getPermissionList()
}

onMounted(() => {
  if (!hasPerms('system.permissionList:read')) {
    ElMessage.error('您没有权限查看权限列表')
    router.push('/error/403')
  }
  getPermissionList();
});
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
