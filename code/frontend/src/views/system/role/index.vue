<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>角色管理</span>
          <el-button type="primary" @click="handleAdd">新增角色</el-button>
        </div>
      </template>

      <el-table :data="roleList" style="width: 100%">
        <el-table-column prop="name" label="角色名称" />
        <el-table-column prop="code" label="角色代码" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增角色' : '编辑角色'"
      width="50%"
    >
      <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="角色代码" prop="code">
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="权限列表" prop="permissions">
          <el-select
            v-model="form.permissions"
            multiple
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
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
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

// 获取角色列表
const getRoleList = async () => {
  try {
    const res = await http.request(
      "get",
      import.meta.env.VITE_BACKEND_URL + apiMap.role.roleList
    );
    if (res.success) {
      roleList.value = res.data.data;
    } else {
      ElMessage.error(res.msg);
    }
  } catch (error) {
    ElMessage.error("获取角色列表失败");
  }
}

// 获取权限列表
const getPermissionList = async () => {
  try {
    const res = await http.request(
      "get",
      import.meta.env.VITE_BACKEND_URL + apiMap.permission.permissionList
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

// 编辑角色
const handleEdit = (row) => {
  dialogType.value = 'edit'
  form.value = {
    ...row,
    permissions: row.permissions.map(p => p.uuid)
  }
  dialogVisible.value = true
}

// 删除角色
const handleDelete = (row) => {
  ElMessageBox.confirm('确认删除该角色吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      const res = await http.request(
        "delete",
        import.meta.env.VITE_BACKEND_URL + apiMap.role.role,
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
            import.meta.env.VITE_BACKEND_URL + apiMap.role.role,
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
            import.meta.env.VITE_BACKEND_URL + apiMap.role.role,
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

onMounted(() => {
  getRoleList()
  getPermissionList()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 