<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>权限管理</span>
          <el-button type="primary" @click="handleAdd">新增权限</el-button>
        </div>
      </template>

      <el-table :data="permissionList" style="width: 100%">
        <el-table-column prop="name" label="权限名称" />
        <el-table-column prop="code" label="权限代码" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="handleEdit(scope.row)"
              >编辑</el-button
            >
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(scope.row)"
              >删除</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增权限' : '编辑权限'"
      width="50%"
    >
      <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="权限代码" prop="code">
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="权限JSON" prop="permission_json">
          <el-input
            v-model="form.permission_json"
            type="textarea"
            :rows="4"
            placeholder="请输入JSON格式的权限配置"
          />
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
import { ref, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import type { FormInstance } from "element-plus";
import { http } from "@/utils/http";
import { apiMap } from "@/config/api";

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
    ElMessage.error("获取权限列表失败");
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

// 删除权限
const handleDelete = row => {
  ElMessageBox.confirm("确认删除该权限吗？", "提示", {
    type: "warning"
  }).then(async () => {
    try {
      const res = await http.request(
        "delete",
        import.meta.env.VITE_BACKEND_URL +
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

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async valid => {
    if (valid) {
      try {
        if (dialogType.value === "add") {
          const res = await http.request(
            "post",
            import.meta.env.VITE_BACKEND_URL + apiMap.permission.permission,
            { data: form.value }
          );
          if (res.success) {
            ElMessage.success("新增成功");
          } else {
            ElMessage.error(res.msg);
          }
        } else {
          const res = await http.request(
            "put",
            import.meta.env.VITE_BACKEND_URL + apiMap.permission.permission,
            { data: form.value }
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
        ElMessage.error(dialogType.value === "add" ? "新增失败" : "编辑失败");
      }
    }
  });
};

onMounted(() => {
  getPermissionList();
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
