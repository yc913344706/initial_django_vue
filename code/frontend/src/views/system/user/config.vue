<template>
  <div class="system-page">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span class="title">密码复杂度配置</span>
        </div>
      </template>

      <el-form
        :model="passwordConfigForm"
        :rules="passwordConfigRules"
        ref="passwordConfigFormRef"
        label-width="180px"
        class="config-form"
      >
        <el-form-item label="最小长度" prop="min_length">
          <el-input-number
            v-model="passwordConfigForm.min_length"
            :min="1"
            :max="128"
            placeholder="最小密码长度"
            style="width: 100%"
          />
          <div class="form-help">密码最小长度要求</div>
        </el-form-item>

        <el-form-item label="最大长度" prop="max_length">
          <el-input-number
            v-model="passwordConfigForm.max_length"
            :min="6"
            :max="128"
            placeholder="最大密码长度"
            style="width: 100%"
          />
          <div class="form-help">密码最大长度限制</div>
        </el-form-item>

        <el-form-item label="需要大写字母" prop="require_uppercase">
          <el-switch
            v-model="passwordConfigForm.require_uppercase"
            active-text="是"
            inactive-text="否"
          />
          <div class="form-help">密码是否必须包含大写字母(A-Z)</div>
        </el-form-item>

        <el-form-item label="需要小写字母" prop="require_lowercase">
          <el-switch
            v-model="passwordConfigForm.require_lowercase"
            active-text="是"
            inactive-text="否"
          />
          <div class="form-help">密码是否必须包含小写字母(a-z)</div>
        </el-form-item>

        <el-form-item label="需要数字" prop="require_numbers">
          <el-switch
            v-model="passwordConfigForm.require_numbers"
            active-text="是"
            inactive-text="否"
          />
          <div class="form-help">密码是否必须包含数字(0-9)</div>
        </el-form-item>

        <el-form-item label="需要特殊字符" prop="require_special">
          <el-switch
            v-model="passwordConfigForm.require_special"
            active-text="是"
            inactive-text="否"
          />
          <div class="form-help">密码是否必须包含特殊字符(!@#$%^&*等)</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSavePasswordConfig">保存密码配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 安全配置 -->
    <el-card class="config-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span class="title">安全配置</span>
        </div>
      </template>

      <el-form
        :model="securityConfigForm"
        :rules="securityConfigRules"
        ref="securityConfigFormRef"
        label-width="180px"
        class="config-form"
      >
        <el-form-item label="失败登录次数限制" prop="max_login_attempts">
          <el-input-number
            v-model="securityConfigForm.max_login_attempts"
            :min="1"
            :max="100"
            placeholder="最大失败登录尝试次数"
            style="width: 100%"
          />
          <div class="form-help">用户登录失败达到此次数后将被锁定</div>
        </el-form-item>

        <el-form-item label="登录锁定时间(分钟)" prop="lockout_duration">
          <el-input-number
            v-model="securityConfigForm.lockout_duration"
            :min="1"
            :max="1440"
            placeholder="锁定时间(分钟)"
            style="width: 100%"
          />
          <div class="form-help">账户被锁定的时间长度</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSaveSecurityConfig">保存安全配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { http } from '@/utils/http'
import { apiMap } from '@/config/api'

interface PasswordConfig {
  min_length: number
  max_length: number
  require_uppercase: boolean
  require_lowercase: boolean
  require_numbers: boolean
  require_special: boolean
}

interface SecurityConfig {
  max_login_attempts: number
  lockout_duration: number
}

const passwordConfigForm = ref<PasswordConfig>({
  min_length: 8,
  max_length: 128,
  require_uppercase: true,
  require_lowercase: true,
  require_numbers: true,
  require_special: false
})

const securityConfigForm = ref<SecurityConfig>({
  max_login_attempts: 5,
  lockout_duration: 60
})

const passwordConfigFormRef = ref<FormInstance>()
const securityConfigFormRef = ref<FormInstance>()

// 密码配置验证规则
const passwordConfigRules = ref<FormRules>({
  min_length: [
    { required: true, message: '请输入最小长度', trigger: 'blur' }
  ],
  max_length: [
    { required: true, message: '请输入最大长度', trigger: 'blur' }
  ]
})

// 安全配置验证规则
const securityConfigRules = ref<FormRules>({
  max_login_attempts: [
    { required: true, message: '请输入最大登录尝试次数', trigger: 'blur' }
  ],
  lockout_duration: [
    { required: true, message: '请输入锁定时间', trigger: 'blur' }
  ]
})

// 获取密码配置
const getPasswordConfig = async () => {
  try {
    const res = await http.request('get', apiMap.user.passwordConfig)
    if (res.success) {
      passwordConfigForm.value = {
        ...passwordConfigForm.value,
        ...res.data
      }
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error: any) {
    ElMessage.error(`获取密码配置失败。${error.msg || error}`)
  }
}

// 获取安全配置
const getSecurityConfig = async () => {
  try {
    const res = await http.request('get', apiMap.user.securityConfig)
    if (res.success) {
      securityConfigForm.value = {
        ...securityConfigForm.value,
        ...res.data
      }
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error(`获取安全配置失败。${error.msg || error}`)
  }
}

// 保存密码配置
const handleSavePasswordConfig = async () => {
  if (!passwordConfigFormRef.value) return

  await passwordConfigFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const configToSave = {
          ...passwordConfigForm.value
        }

        const res = await http.request('post', apiMap.user.passwordConfig, { data: configToSave })
        if (res.success) {
          ElMessage.success('密码配置保存成功')
        } else {
          ElMessage.error(res.msg)
        }
      } catch (error) {
        ElMessage.error(`保存密码配置失败。${error.msg || error}`)
      }
    }
  })
}

// 保存安全配置
const handleSaveSecurityConfig = async () => {
  if (!securityConfigFormRef.value) return

  await securityConfigFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const res = await http.request('post', apiMap.user.securityConfig, { data: securityConfigForm.value })
        if (res.success) {
          ElMessage.success('安全配置保存成功')
        } else {
          ElMessage.error(res.msg)
        }
      } catch (error) {
        ElMessage.error(`保存安全配置失败。${error.msg || error}`)
      }
    }
  })
}

onMounted(() => {
  getPasswordConfig()
  getSecurityConfig()
})
</script>

<style scoped>
.config-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 16px;
  font-weight: bold;
}

.config-form {
  max-width: 600px;
}

.form-help {
  color: #999;
  font-size: 12px;
  margin-top: 5px;
}

.dialog-footer button {
  margin-left: 10px;
}
</style>