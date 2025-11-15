<template>
  <div class="app-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>{{ t('page.user.detail') }}</span>
          <div>
            <!-- {{ t('page.user.resetPasswordButton') }}（仅管理员可见） -->
            <el-button
              type="warning"
              @click="handleResetPassword"
              v-if="hasPerms('system.user:resetPassword') && (! userInfo.is_ldap)"
              style="margin-right: 10px;"
            >
              {{ t('page.user.resetPassword') }}
            </el-button>

            <!-- {{ t('page.user.changePasswordButton') }}（仅当前用户可见） -->
            <!-- <el-button
              type="primary"
              @click="handleChangePassword"
              v-if="userInfo.username === getCurrentUserUsername()"
              style="margin-right: 10px;"
            >
              {{ t('page.user.changePassword') }}
            </el-button> -->

            <el-button type="primary" @click="handleEdit" v-if="!isEditing && hasPerms('system.user:update')">{{ t('button.edit') }}</el-button>
            <el-button @click="$router.back()">{{ t('button.back') }}</el-button>
          </div>
        </div>
      </template>

      <template v-if="isEditing && hasPerms('system.user:update')">
        <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
        <el-form-item :label="t('field.username')" prop="username">
          <el-input v-model="form.username" :placeholder="t('page.user.enterUsername')" />
        </el-form-item>
        <el-form-item :label="t('field.nickname')" prop="nickname">
          <el-input v-model="form.nickname" :placeholder="t('page.user.enterNickname')" />
        </el-form-item>
        <el-form-item :label="t('field.phone')" prop="phone">
          <el-input v-model="form.phone" :placeholder="t('page.user.enterPhone')" />
        </el-form-item>
        <el-form-item :label="t('field.email')" prop="email">
          <el-input v-model="form.email" :placeholder="t('page.user.enterEmail')" />
        </el-form-item>
        <el-form-item :label="t('field.status')" prop="is_active">
          <el-switch v-model="form.is_active" />
        </el-form-item>
        <el-form-item :label="t('field.role')">
          <el-select
            v-model="form.roles"
            multiple
            filterable
            :placeholder="t('page.user.selectRolePlaceholder')"
            style="width: 100%"
          >
            <el-option
              v-for="item in roleList"
              :key="item.uuid"
              :label="item.name"
              :value="item.uuid"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('field.permission')">
          <el-select
            v-model="form.permissions"
            multiple
            filterable
            :placeholder="t('page.user.selectPermissionPlaceholder')"
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
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">{{ t('button.save') }}</el-button>
          <el-button @click="handleCancel">{{ t('button.cancel') }}</el-button>
        </el-form-item>
      </el-form>
      </template>

      <template v-if="!isEditing && hasPerms('system.user:read')">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="t('field.username')">{{ userInfo.username }}</el-descriptions-item>
          <el-descriptions-item :label="t('field.nickname')">{{ userInfo.nickname }}</el-descriptions-item>
          <el-descriptions-item :label="t('field.phone')">{{ userInfo.phone }}</el-descriptions-item>
          <el-descriptions-item :label="t('field.email')">{{ userInfo.email }}</el-descriptions-item>
          <el-descriptions-item :label="t('field.status')">
            <el-tag :type="userInfo.is_active ? 'success' : 'danger'">
              {{ userInfo.is_active ? t('common.enabled') : t('common.disabled') }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('field.createTime')">{{ userInfo.created_time }}</el-descriptions-item>
          <el-descriptions-item :label="t('field.updateTime')">{{ userInfo.updated_time }}</el-descriptions-item>
        </el-descriptions>

        <div class="section-title">{{ t('page.user.roleList') }}</div>
        <el-table :data="userInfo.roles" style="width: 100%; margin-bottom: 20px">
          <el-table-column prop="name" :label="t('page.user.roleName')">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/role/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" :label="t('field.description')" />
        </el-table>

        <div class="section-title">{{ t('page.user.userGroupList') }}</div>
        <el-table :data="userInfo.groups" style="width: 100%; margin-bottom: 20px">
          <el-table-column prop="name" :label="t('page.user.groupName')">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/group/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" :label="t('field.description')" />
        </el-table>

        <div class="section-title">{{ t('page.user.permissionList') }}</div>
        <el-table :data="userInfo.permissions" style="width: 100%">
          <el-table-column prop="name" :label="t('page.user.permissionName')">
            <template #default="{ row }">
              <el-link type="primary" @click="$router.push(`/system/permission/detail?uuid=${row.uuid}`)">{{ row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column prop="description" :label="t('field.description')" />
        </el-table>

        <div class="section-title">{{ t('page.user.userPermissionJson') }}</div>
        <el-card class="permission-json-card">
          <pre class="permission-json">{{ permissionJson }}</pre>
        </el-card>
      </template>
    </el-card>

    <!-- {{ t('page.user.changePassword') }}对话框 -->
    <el-dialog
      v-model="changePasswordDialogVisible"
      :title="t('page.user.changePassword')"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        :model="changePasswordForm"
        :rules="changePasswordRules"
        ref="changePasswordFormRef"
        label-width="100px"
      >
        <el-form-item :label="t('field.currentPassword')" prop="current_password">
          <el-input
            v-model="changePasswordForm.current_password"
            type="password"
            show-password
            :placeholder="t('page.user.enterCurrentPassword')"
          />
        </el-form-item>
        <el-form-item :label="t('field.newPassword')" prop="new_password">
          <el-input
            v-model="changePasswordForm.new_password"
            type="password"
            show-password
            :placeholder="t('page.user.enterNewPassword')"
          />
        </el-form-item>
        <el-form-item :label="t('field.confirmPassword')" prop="confirm_password">
          <el-input
            v-model="changePasswordForm.confirm_password"
            type="password"
            show-password
            :placeholder="t('page.user.enterConfirmPassword')"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="changePasswordDialogVisible = false">{{ t('button.cancel') }}</el-button>
          <el-button type="primary" @click="confirmChangePassword">{{ t('button.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- {{ t('page.user.showGeneratedPassword') }}对话框 -->
    <el-dialog
      v-model="generatedPasswordDialogVisible"
      :title="t('message.passwordResetSuccess')"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-alert
        :title="t('message.passwordGeneratedNotice')"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      <div style="display: flex; align-items: center;">
        <el-input
          v-model="generatedPassword"
          readonly
          show-password
          :placeholder="t('page.user.generatedPasswordPlaceholder')"
          style="flex: 1; margin-right: 10px;"
        />
        <el-button
          type="primary"
          @click="copyPassword"
          :icon="CopyDocument"
        >
          {{ t('button.copy') }}
        </el-button>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="generatedPasswordDialogVisible = false">{{ t('button.confirm') }}</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { http } from '@/utils/http'
import { apiMap } from '@/config/api'
import { hasPerms } from "@/utils/auth";
import router from '@/router'
import { uuid } from '@pureadmin/utils'
import { CopyDocument } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

// 复制密码到剪贴板
const copyPassword = async () => {
  try {
    await navigator.clipboard.writeText(generatedPassword.value)
    ElMessage.success(t('message.passwordCopiedToClipboard'))
  } catch (err) {
    // 如果浏览器不支持 navigator.clipboard，使用备用方案
    const textArea = document.createElement('textarea')
    textArea.value = generatedPassword.value
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      ElMessage.success(t('message.passwordCopiedToClipboard'))
    } catch (error) {
      ElMessage.error(t('message.copyFailedManual'))
    }
    document.body.removeChild(textArea)
  }
}

const route = useRoute()
const isEditing = ref(false)
const formRef = ref<FormInstance>()
const userInfo = ref({
  uuid: '',
  is_ldap: false,
  username: '',
  nickname: '',
  phone: '',
  email: '',
  is_active: true,
  created_time: '',
  updated_time: '',
  roles: [],
  permissions: [],
  groups: []
})

const form = ref({
  uuid: '',
  username: '',
  nickname: '',
  phone: '',
  email: '',
  is_active: true,
  roles: [] as string[],
  permissions: [] as string[],
  groups: [] as string[]
})

const roleList = ref([])
const permissionList = ref([])
const permissionJson = ref({})

// 密码相关变量
const changePasswordDialogVisible = ref(false)
const generatedPasswordDialogVisible = ref(false)  // 显示生成密码的对话框
const changePasswordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})
// 生成的密码
const generatedPassword = ref('')

const changePasswordRules = {
  current_password: [
    { required: true, message: t('page.user.enterCurrentPassword'), trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: t('page.user.enterNewPassword'), trigger: 'blur' },
    { min: 6, message: t('page.user.newPasswordMinLength'), trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: t('page.user.enterConfirmPassword'), trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== changePasswordForm.value.new_password) {
          callback(new Error(t('page.user.confirmPasswordNotMatch')))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}



const rules = {
  username: [
    { required: true, message: t('page.user.enterUsername'), trigger: 'blur' }
  ],
  nickname: [
    { required: true, message: t('page.user.enterNickname'), trigger: 'blur' }
  ]
}

// 获取用户详情
const getUserDetail = async () => {
  try {
    const res = await http.request('get', apiMap.user.user, {
      params: { uuid: route.query.uuid }
    })
    if (res.success) {
      userInfo.value = res.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error(`${t('message.getUserDetailFailed')}。${error.msg || error}`)
  }
}

// 获取角色列表
const getRoleList = async () => {
  try {
    const res = await http.request('get', apiMap.role.roleList)
    if (res.success) {
      roleList.value = res.data.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error(`${t('message.getRoleListFailed')}。${error.msg || error}`)
  }
}

// 获取权限列表
const getPermissionList = async () => {
  try {
    const res = await http.request('get', apiMap.permission.permissionList)
    if (res.success) {
      permissionList.value = res.data.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error(`${t('message.getPermissionListFailed')}。${error.msg || error}`)
  }
}

// 获取用户权限JSON
const getUserPermissionJson = async () => {
  try {
    const res = await http.request('get', apiMap.permission.userPermissionJson, {
      params: { uuid: route.query.uuid }
    })
    if (res.success) {
      permissionJson.value = res.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error(`${t('message.getUserPermissionJsonFailed')}。${error.msg || error}`)
  }
}

// 编辑
const handleEdit = () => {
  form.value = {
    uuid: userInfo.value.uuid,
    username: userInfo.value.username,
    nickname: userInfo.value.nickname,
    phone: userInfo.value.phone,
    email: userInfo.value.email,
    is_active: userInfo.value.is_active,
    roles: userInfo.value.roles.map((role: any) => role.uuid),
    permissions: userInfo.value.permissions.map((permission: any) => permission.uuid)
  }
  isEditing.value = true
}

// 取消编辑
const handleCancel = () => {
  isEditing.value = false
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const res = await http.request('put', apiMap.user.user, {
          data: form.value
        })
        if (res.success) {
          ElMessage.success(t('message.updateSuccess'))
          isEditing.value = false
          getUserDetail()
        } else {
          ElMessage.error(res.msg)
        }
      } catch (error) {
        ElMessage.error(`${t('message.updateFailed')}。${error.msg || error}`)
      }
    }
  })
}

// 获取当前用户UUID
const getCurrentUserUsername = () => {
  const userStr = localStorage.getItem('user-info');
  if (userStr) {
    const user = JSON.parse(userStr);
    return user.username;
  }
  return '';
}

// 修改密码
const handleChangePassword = () => {
  changePasswordDialogVisible.value = true
  // 重置表单
  changePasswordForm.value = {
    current_password: '',
    new_password: '',
    confirm_password: ''
  }
}

// 生成安全密码
const generateSecurePassword = (length = 12) => {
  const uppercaseChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  const lowercaseChars = 'abcdefghijklmnopqrstuvwxyz'
  const numberChars = '0123456789'
  const specialChars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
  
  const allChars = uppercaseChars + lowercaseChars + numberChars + specialChars
  let password = ''
  
  // 确保密码包含每种类型的字符
  password += uppercaseChars[Math.floor(Math.random() * uppercaseChars.length)]
  password += lowercaseChars[Math.floor(Math.random() * lowercaseChars.length)]
  password += numberChars[Math.floor(Math.random() * numberChars.length)]
  password += specialChars[Math.floor(Math.random() * specialChars.length)]
  
  // 填充剩余长度
  for (let i = password.length; i < length; i++) {
    password += allChars[Math.floor(Math.random() * allChars.length)]
  }
  
  // 打乱密码字符顺序
  return password.split('').sort(() => Math.random() - 0.5).join('')
}

// 重置密码
const handleResetPassword = async () => {
  // 询问用户是否确认重置密码
  try {
    await ElMessageBox.confirm(
      '此操作将为用户生成新密码，用户将无法使用旧密码登录。是否继续？',
      '确认重置密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 生成新密码
    const newPassword = generateSecurePassword(12)
    
    // 调用后端API重置密码
    try {
      const res = await http.request('post', apiMap.user.resetPassword, {
        data: {
          user_uuid: route.query.uuid,
          new_password: newPassword,
          confirm_password: newPassword  // 确认密码与新密码相同
        }
      })
      
      if (res.success) {
        // 显示生成的密码
        generatedPassword.value = newPassword
        generatedPasswordDialogVisible.value = true
        ElMessage.success(res.msg || '密码重置成功')
      } else {
        ElMessage.error(res.msg)
      }
    } catch (error) {
      ElMessage.error(`密码重置失败。${error.msg || error}`)
    }
  } catch {
    // 用户取消操作
    console.log('用户取消重置密码操作')
  }
}

// 确认修改密码
const confirmChangePassword = async () => {
  try {
    const res = await http.request('post', apiMap.user.changePassword, {
      data: changePasswordForm.value
    })
    if (res.success) {
      ElMessage.success(res.msg || t('message.changePasswordSuccess'))
      changePasswordDialogVisible.value = false
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error(`${t('message.changePasswordFailed')}。${error.msg || error}`)
  }
}



onMounted(() => {
  if (!hasPerms('system.user:read')) {
    ElMessage.error(t('message.noPermissionToViewUserDetail'))
    router.push('/error/403')
  }
  getUserDetail()
  getUserPermissionJson()
  if (hasPerms('system.roleList:read')) {
    getRoleList()
  }
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
.section-title {
  font-size: 16px;
  font-weight: bold;
  margin: 20px 0 10px;
}
.permission-json-card {
  margin-top: 10px;
}
.permission-json {
  height: 50vh;
  overflow-y: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 10px;
  margin: 0;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style> 