<template>
  <div class="system-page" v-if="hasPerms('system.permissionList:read')">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <div class="search-form">
        <div class="form-item">
          <span class="label">{{ t('page.permission.keyword') }}</span>
          <el-input
            v-model="searchForm.keyword"
            :placeholder="t('page.permission.searchPlaceholder')"
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
            :disabled="!selectedPermissions.length"
            v-if="hasPerms('system.permissionList:delete')"
          >{{ t('button.batchDelete') }}</el-button>
          <el-button
            type="primary"
            @click="handleAdd"
            v-if="hasPerms('system.permissionList:create')"
          >{{ t('button.create') }}</el-button>
        </div>
      </div>
    </el-card>

    <!-- 表格区域 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="permissionList"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" min-width="55" />
        <el-table-column prop="name" :label="t('page.permission.name')" min-width="180" fixed/>
        <el-table-column prop="code" :label="t('page.permission.code')" min-width="120" />
        <el-table-column prop="description" :label="t('field.description')" min-width="240" />
        <el-table-column prop="is_system" :label="t('page.permission.type')" min-width="120">
          <template #default="scope">
            <el-tag :type="scope.row.is_system ? 'danger' : 'success'">
              {{ scope.row.is_system ? t('page.permission.systemPermission') : t('page.permission.normalPermission') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('table.actions')" width="250">
          <template #default="scope">
            <el-button type="info" size="small" @click="handleViewDetail(scope.row)">{{ t('button.detail') }}</el-button>
            <!-- <el-button
              type="primary"
              size="small"
              @click="handleEdit(scope.row)"
              v-if="hasPerms('system.permission:update')"
            >
              {{ t('button.edit') }}
            </el-button> -->
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(scope.row)"
              :disabled="scope.row.is_system"
              v-if="hasPerms('system.permission:delete')"
            >
              {{ t('button.delete') }}
            </el-button>
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
      :title="dialogType === 'add' ? t('dialog.title.create') + t('common.permission') : t('dialog.title.edit') + t('common.permission')"
      width="50%"
    >
      <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
        <el-form-item :label="t('page.permission.name')" prop="name">
          <el-input v-model="form.name" :placeholder="t('page.permission.enterName')" />
        </el-form-item>
        <el-form-item :label="t('page.permission.code')" prop="code">
          <el-input v-model="form.code" :placeholder="t('page.permission.enterCode')" />
        </el-form-item>
        <el-form-item :label="t('page.permission.json')" prop="permission_json">
          <el-input
            v-model="form.permission_json"
            type="textarea"
            :rows="10"
            :placeholder="t('page.permission.enterJson')"
            @input="handleJsonInput"
          />
        </el-form-item>
        <el-form-item :label="t('field.description')" prop="description">
          <el-input v-model="form.description" type="textarea" :placeholder="t('page.permission.enterDescription')" />
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
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

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
  name: [{ required: true, message: t('page.permission.enterName'), trigger: "blur" }],
  code: [{ required: true, message: t('page.permission.enterCode'), trigger: "blur" }],
  permission_json: [
    { required: true, message: t('page.permission.enterJson'), trigger: "blur" }
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
    ElMessage.error(`${t('message.getPermissionListFailed')}。${error.msg || error}`);
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
  // 检查是否为系统权限
  if (row.is_system) {
    ElMessage.warning(t('message.systemPermissionCannotDelete'));
    return;
  }

  ElMessageBox.confirm(t('message.deleteConfirm'), t('common.confirm'), {
    type: "warning"
  }).then(async () => {
    try {
      const res = await http.request(
        "delete",
        apiMap.permission.permission,
        { data: { uuid: row.uuid } }
      );
      if (res.success) {
        ElMessage.success(t('message.operationSuccess'));
        getPermissionList();
      } else {
        ElMessage.error(res.msg);
      }
    } catch (error) {
      ElMessage.error(`${t('message.deleteFailed')}。${error.msg || error}`);
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
            ElMessage.success(t('message.createSuccess'));
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
            ElMessage.success(t('message.editSuccess'));
          } else {
            ElMessage.error(res.msg);
          }
        }
        dialogVisible.value = false;
        getPermissionList();
      } catch (error) {
        logger.error(error)
        ElMessage.error(dialogType.value === "add" ? `${t('message.createFailed')}。${error.msg || error}` : `${t('message.editFailed')}。${error.msg || error}`);
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

  // 检查选中的权限中是否包含系统权限
  const selectedPermissionObjects = permissionList.value.filter(item =>
    selectedPermissions.value.includes(item.uuid)
  );

  const systemPermissions = selectedPermissionObjects.filter(item => item.is_system);
  if (systemPermissions.length > 0) {
    ElMessage.warning(`${t('message.systemPermissionCannotDelete')}：${systemPermissions.map(p => p.name).join(', ')}`);
    return;
  }

  try {
    await ElMessageBox.confirm(t('message.batchDeleteConfirm'), t('common.confirm'), {
      type: 'warning'
    })

    const res = await http.request('delete', apiMap.permission.permissionList, {
      data: { uuids: selectedPermissions.value }
    })

    if (res.success) {
      ElMessage.success(t('message.operationSuccess'))
      getPermissionList()
      selectedPermissions.value = []
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
