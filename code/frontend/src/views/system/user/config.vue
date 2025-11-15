<template>
  <div class="system-page">

    <!-- {{ t('page.user.passwordConfig') }} -->
    <el-card class="config-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span class="title">{{ t('page.user.passwordConfig') }}</span>
        </div>
      </template>

      <el-form
        :model="passwordConfigForm"
        :rules="passwordConfigRules"
        ref="passwordConfigFormRef"
        label-width="150px"
        class="config-form"
      >
        <el-form-item :label="t('page.user.passwordMinLength')" prop="min_length">
          <el-input-number
            v-model="passwordConfigForm.min_length"
            :min="1"
            :max="256"
            :placeholder="t('page.user.passwordMinLength')"
          />
          <div class="form-help">{{ t('page.user.passwordMinLengthHelp') }}</div>
        </el-form-item>

        <el-form-item :label="t('page.user.passwordMaxLength')" prop="max_length">
          <el-input-number
            v-model="passwordConfigForm.max_length"
            :min="1"
            :max="256"
            :placeholder="t('page.user.passwordMaxLength')"
          />
          <div class="form-help">{{ t('page.user.passwordMaxLengthHelp') }}</div>
        </el-form-item>

        <el-form-item :label="t('page.user.requireUppercase')">
          <el-switch
            v-model="passwordConfigForm.require_uppercase"
            :active-text="t('common.enabled')"
            :inactive-text="t('common.disabled')"
          />
          <div class="form-help">{{ t('page.user.requireUppercaseHelp') }}</div>
        </el-form-item>

        <el-form-item :label="t('page.user.requireLowercase')">
          <el-switch
            v-model="passwordConfigForm.require_lowercase"
            :active-text="t('common.enabled')"
            :inactive-text="t('common.disabled')"
          />
          <div class="form-help">{{ t('page.user.requireLowercaseHelp') }}</div>
        </el-form-item>

        <el-form-item :label="t('page.user.requireNumbers')">
          <el-switch
            v-model="passwordConfigForm.require_numbers"
            :active-text="t('common.enabled')"
            :inactive-text="t('common.disabled')"
          />
          <div class="form-help">{{ t('page.user.requireNumbersHelp') }}</div>
        </el-form-item>

        <el-form-item :label="t('page.user.requireSpecialChars')">
          <el-switch
            v-model="passwordConfigForm.require_special"
            :active-text="t('common.enabled')"
            :inactive-text="t('common.disabled')"
          />
          <div class="form-help">{{ t('page.user.requireSpecialCharsHelp') }}</div>
        </el-form-item>

        <el-form-item :label="t('page.user.allowedSpecialChars')" prop="allowed_special_chars" v-if="passwordConfigForm.require_special">
          <el-input
            v-model="passwordConfigForm.allowed_special_chars"
            :placeholder="t('page.user.allowedSpecialChars')"
            :rows="3"
            type="textarea"
          />
          <div class="form-help">{{ t('page.user.allowedSpecialCharsHelp') }}</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSavePasswordConfig">{{ t('page.user.savePasswordConfig') }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- {{ t('page.user.securityConfig') }} -->
    <el-card class="config-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span class="title">{{ t('page.user.securityConfig') }}</span>
        </div>
      </template>

      <el-form
        :model="securityConfigForm"
        :rules="securityConfigRules"
        ref="securityConfigFormRef"
        label-width="150px"
        class="config-form"
      >
        <el-form-item :label="t('page.user.maxLoginAttempts')" prop="max_login_attempts">
          <el-input-number
            v-model="securityConfigForm.max_login_attempts"
            :min="1"
            :max="100"
            :placeholder="t('page.user.maxLoginAttemptsPlaceholder')"
          />
          <div class="form-help">{{ t('page.user.maxLoginAttemptsHelp') }}</div>
        </el-form-item>

        <el-form-item :label="t('page.user.lockoutDuration')" prop="lockout_duration">
          <el-input-number
            v-model="securityConfigForm.lockout_duration"
            :min="1"
            :max="1440"
            :placeholder="t('page.user.lockoutDurationPlaceholder')"
          />
          <div class="form-help">{{ t('page.user.lockoutDurationHelp') }}</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSaveSecurityConfig">{{ t('page.user.saveSecurityConfig') }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span class="title">{{ t('page.user.ldapConfig') }}</span>
        </div>
      </template>

      <el-form
        :model="ldapConfigForm"
        :rules="ldapConfigRules"
        ref="ldapConfigFormRef"
        label-width="150px"
        class="config-form"
      >
        <el-form-item :label="t('page.user.enableLdapAuth')" prop="enabled">
          <el-switch
            v-model="ldapConfigForm.enabled"
            :active-text="t('common.enabled')"
            :inactive-text="t('common.disabled')"
          />
        </el-form-item>

        <el-form-item :label="t('page.user.ldapType')" prop="ldap_type">
          <el-select
            v-model="ldapConfigForm.ldap_type"
            :placeholder="t('page.user.ldapTypePlaceholder')"
            style="width: 100%"
            @change="handleLdapTypeChange"
          >
            <el-option :label="t('page.user.activeDirectory')" value="ad" />
            <el-option :label="t('page.user.openldap')" value="openldap" />
          </el-select>
          <div class="form-help">{{ t('page.user.ldapTypeHelp') }}</div>
        </el-form-item>

        <el-form-item :label="t('page.user.serverHost')" prop="server_host">
          <el-input
            v-model="ldapConfigForm.server_host"
            :placeholder="t('page.user.serverHostPlaceholder')"
          />
        </el-form-item>

        <el-form-item :label="t('page.user.serverPort')" prop="server_port">
          <el-input
            v-model="ldapConfigForm.server_port"
            :placeholder="t('page.user.serverPortPlaceholder')"
          />
          <!-- <el-input-number
            v-model="ldapConfigForm.server_port"
            :min="1"
            :max="65535"
            :placeholder="t('page.user.serverPortPlaceholder')"
            style="width: 100%"
          /> -->
        </el-form-item>

        <el-form-item :label="t('page.user.baseDn')" prop="base_dn">
          <el-input
            v-model="ldapConfigForm.base_dn"
            :placeholder="t('page.user.baseDnPlaceholder')"
          />
        </el-form-item>

        <el-form-item :label="t('page.user.adminDn')" prop="admin_dn">
          <el-input
            v-model="ldapConfigForm.admin_dn"
            :placeholder="t('page.user.adminDnPlaceholder')"
          />
        </el-form-item>

        <el-form-item :label="t('page.user.adminPassword')" prop="admin_password">
          <el-input
            v-model="ldapConfigForm.admin_password"
            type="password"
            show-password
            :placeholder="t('page.user.adminPasswordPlaceholder')"
          />
        </el-form-item>

        <el-form-item :label="t('page.user.userSearchFilter')" prop="user_search_filter">
          <el-input
            v-model="ldapConfigForm.user_search_filter"
            :placeholder="t('page.user.userSearchFilterPlaceholder')"
          />
        </el-form-item>

        <el-form-item :label="t('page.user.usernameAttr')" prop="username_attr">
          <el-input
            v-model="ldapConfigForm.username_attr"
            :placeholder="t('page.user.usernameAttrPlaceholder')"
          />
        </el-form-item>

        <el-form-item :label="t('page.user.displayNameAttr')" prop="display_name_attr">
          <el-input
            v-model="ldapConfigForm.display_name_attr"
            :placeholder="t('page.user.displayNameAttrPlaceholder')"
          />
        </el-form-item>

        <el-form-item :label="t('page.user.emailAttr')" prop="email_attr">
          <el-input
            v-model="ldapConfigForm.email_attr"
            :placeholder="t('page.user.emailAttrPlaceholder')"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSaveLdapConfig">{{ t('page.user.saveLdapConfig') }}</el-button>
          <el-button @click="handleTestConnection">{{ t('page.user.testConnection') }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { http } from '@/utils/http'
import { apiMap } from '@/config/api'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

interface LdapConfig {
  enabled: boolean
  server_host: string
  server_port: number
  base_dn: string
  admin_dn: string
  admin_password: string
  user_search_filter: string
  username_attr: string
  display_name_attr: string
  email_attr: string
  ldap_type: string
}

interface SecurityConfig {
  max_login_attempts: number
  lockout_duration: number
}

interface PasswordConfig {
  min_length: number
  max_length: number
  require_uppercase: boolean
  require_lowercase: boolean
  require_numbers: boolean
  require_special: boolean
  allowed_special_chars: string
}

const ldapConfigForm = ref<LdapConfig>({
  enabled: false,
  server_host: '',
  server_port: 389,
  base_dn: '',
  admin_dn: '',
  admin_password: '',
  user_search_filter: '',
  username_attr: '',
  display_name_attr: '',
  email_attr: '',
  ldap_type: 'ad'  // 默认为Active Directory
})

const securityConfigForm = ref<SecurityConfig>({
  max_login_attempts: 5,
  lockout_duration: 60
})

const passwordConfigForm = ref<PasswordConfig>({
  min_length: 8,
  max_length: 128,
  require_uppercase: true,
  require_lowercase: true,
  require_numbers: true,
  require_special: false,
  allowed_special_chars: "!@#$%^&*()_+-=[]{};':\"\\|,.<>/?"  // 默认的特殊字符
})

const ldapConfigFormRef = ref<FormInstance>()
const securityConfigFormRef = ref<FormInstance>()
const passwordConfigFormRef = ref<FormInstance>()

// 密码配置验证规则
const passwordConfigRules = ref<FormRules>({
  min_length: [
    { required: true, message: t('page.user.passwordMinLengthRequired'), trigger: 'blur' }
  ],
  max_length: [
    { required: true, message: t('page.user.passwordMaxLengthRequired'), trigger: 'blur' }
  ],
  allowed_special_chars: [
    { required: true, message: t('page.user.allowedSpecialCharsRequired'), trigger: 'blur' }
  ]
})

// LDAP配置验证规则
const ldapConfigRules = ref<FormRules>({
  server_host: [
    { required: true, message: t('page.user.serverHostRequired'), trigger: 'blur' }
  ],
  base_dn: [
    { required: true, message: t('page.user.baseDnRequired'), trigger: 'blur' }
  ],
  admin_dn: [
    { required: true, message: t('page.user.adminDnRequired'), trigger: 'blur' }
  ]
})

// 安全配置验证规则
const securityConfigRules = ref<FormRules>({
  max_login_attempts: [
    { required: true, message: t('page.user.maxLoginAttemptsRequired'), trigger: 'blur' }
  ],
  lockout_duration: [
    { required: true, message: t('page.user.lockoutDurationRequired'), trigger: 'blur' }
  ]
})

// 获取密码配置
const getPasswordConfig = async () => {
  try {
    const res = await http.request('get', apiMap.user.passwordConfig)
    if (res.success) {
      const configData = res.data

      passwordConfigForm.value = {
        min_length: configData.min_length || 8,
        max_length: configData.max_length || 128,
        require_uppercase: configData.require_uppercase || false,
        require_lowercase: configData.require_lowercase || false,
        require_numbers: configData.require_numbers || false,
        require_special: configData.require_special || false,
        allowed_special_chars: configData.allowed_special_chars || "!@#$%^&*()_+-=[]{};':\"\\|,.<>/?"
      }
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error: any) {
    ElMessage.error(`${t('message.getPasswordConfigFailed')}。${error.msg || error}`)
  }
}

// 获取LDAP配置
const getLdapConfig = async () => {
  try {
    const res = await http.request('get', apiMap.ldap.config)
    if (res.success) {
      const configData = res.data

      ldapConfigForm.value = {
        ...configData
      }
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error: any) {
    ElMessage.error(`${t('message.getLdapConfigFailed')}。${error.msg || error}`)
  }
}

// 处理LDAP类型变化
const handleLdapTypeChange = (value: string) => {
  if (!ldapConfigForm.value.user_search_filter &&
      !ldapConfigForm.value.username_attr &&
      !ldapConfigForm.value.display_name_attr &&
      !ldapConfigForm.value.email_attr) {
    // 只有在用户还没有自定义这些值时才预填充默认值
    if (value === 'ad') {
      // Active Directory 默认值
      ldapConfigForm.value.user_search_filter = '(objectClass=user)'
      ldapConfigForm.value.username_attr = 'sAMAccountName'
      ldapConfigForm.value.display_name_attr = 'displayName'
      ldapConfigForm.value.email_attr = 'mail'
    } else if (value === 'openldap') {
      // OpenLDAP 默认值
      ldapConfigForm.value.user_search_filter = '(objectClass=posixAccount)'
      ldapConfigForm.value.username_attr = 'uid'
      ldapConfigForm.value.display_name_attr = 'cn'
      ldapConfigForm.value.email_attr = 'mail'
    }
  }
}

// 获取安全配置
const getSecurityConfig = async () => {
  try {
    const res = await http.request('get', apiMap.security.config)
    if (res.success) {
      securityConfigForm.value = res.data
    } else {
      ElMessage.error(res.msg)
    }
  } catch (error) {
    ElMessage.error(`${t('message.getSecurityConfigFailed')}。${error.msg || error}`)
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
          ElMessage.success(t('message.passwordConfigSaved'))
        } else {
          ElMessage.error(res.msg)
        }
      } catch (error) {
        ElMessage.error(`${t('message.savePasswordConfigFailed')}。${error.msg || error}`)
      }
    }
  })
}

// 保存LDAP配置
const handleSaveLdapConfig = async () => {
  if (!ldapConfigFormRef.value) return

  await ldapConfigFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const configToSave = {
          ...ldapConfigForm.value
        }

        const res = await http.request('post', apiMap.ldap.config, { data: configToSave })
        if (res.success) {
          ElMessage.success(t('message.ldapConfigSaved'))
        } else {
          ElMessage.error(res.msg)
        }
      } catch (error) {
        ElMessage.error(`${t('message.saveLdapConfigFailed')}。${error.msg || error}`)
      }
    }
  })
}

// 测试LDAP连接
const handleTestConnection = async () => {
  if (!ldapConfigFormRef.value) return

  await ldapConfigFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const configToTest = {
          ...ldapConfigForm.value
        }

        const res = await http.request('post', apiMap.ldap.testConnection, { data: configToTest })
        if (res.success) {
          ElMessage.success(t('message.ldapConnectionTestSuccess'))
        } else {
          ElMessage.error(res.msg || t('message.ldapConnectionTestFailed'))
        }
      } catch (error) {
        ElMessage.error(`${t('message.ldapConnectionTestFailed')}。${error.msg || error}`)
      }
    }
  })
}

// 保存安全配置
const handleSaveSecurityConfig = async () => {
  if (!securityConfigFormRef.value) return

  await securityConfigFormRef.value.validate(async (valid) => {
    if (valid) {
      let res: any
      try {
        res = await http.request('post', apiMap.security.config, { data: securityConfigForm.value })
        console.debug(res)
        if (res.success) {
          ElMessage.success(t('message.securityConfigSaved'))
        } else {
          ElMessage.error(res.msg)
        }
      } catch (error) {
        ElMessage.error(`${t('message.saveSecurityConfigFailed')}。${error.msg || error}`)
      }
    }
  })
}

onMounted(() => {
  getPasswordConfig()
  getLdapConfig()
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