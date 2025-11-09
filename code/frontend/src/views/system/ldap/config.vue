<template>
  <div class="system-page">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span class="title">LDAP配置</span>
        </div>
      </template>

      <el-form
        :model="ldapConfigForm"
        :rules="ldapConfigRules"
        ref="ldapConfigFormRef"
        label-width="150px"
        class="config-form"
      >
        <el-form-item label="启用LDAP认证" prop="enabled">
          <el-switch
            v-model="ldapConfigForm.enabled"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>

        <el-form-item label="LDAP类型" prop="ldap_type">
          <el-select
            v-model="ldapConfigForm.ldap_type"
            placeholder="选择LDAP类型"
            style="width: 100%"
            @change="handleLdapTypeChange"
          >
            <el-option label="Active Directory" value="ad" />
            <el-option label="OpenLDAP" value="openldap" />
          </el-select>
          <div class="form-help">选择您使用的LDAP服务器类型</div>
        </el-form-item>

        <el-form-item label="服务器主机" prop="server_host">
          <el-input
            v-model="ldapConfigForm.server_host"
            placeholder="例如: ldap.example.com"
          />
        </el-form-item>

        <el-form-item label="服务器端口" prop="server_port">
          <el-input
            v-model="ldapConfigForm.server_port"
            placeholder="端口号"
          />
          <!-- <el-input-number
            v-model="ldapConfigForm.server_port"
            :min="1"
            :max="65535"
            placeholder="端口号"
            style="width: 100%"
          /> -->
        </el-form-item>

        <el-form-item label="基础DN" prop="base_dn">
          <el-input
            v-model="ldapConfigForm.base_dn"
            placeholder="例如: dc=example,dc=com"
          />
        </el-form-item>

        <el-form-item label="管理员DN" prop="admin_dn">
          <el-input
            v-model="ldapConfigForm.admin_dn"
            placeholder="例如: cn=admin,dc=example,dc=com"
          />
        </el-form-item>

        <el-form-item label="管理员密码" prop="admin_password">
          <el-input
            v-model="ldapConfigForm.admin_password"
            type="password"
            show-password
            placeholder="管理员密码"
          />
        </el-form-item>

        <el-form-item label="用户搜索过滤器" prop="user_search_filter">
          <el-input
            v-model="ldapConfigForm.user_search_filter"
            placeholder="例如: (objectClass=user)"
          />
        </el-form-item>

        <el-form-item label="用户名属性" prop="username_attr">
          <el-input
            v-model="ldapConfigForm.username_attr"
            placeholder="例如: sAMAccountName"
          />
        </el-form-item>

        <el-form-item label="显示名属性" prop="display_name_attr">
          <el-input
            v-model="ldapConfigForm.display_name_attr"
            placeholder="例如: displayName"
          />
        </el-form-item>

        <el-form-item label="邮箱属性" prop="email_attr">
          <el-input
            v-model="ldapConfigForm.email_attr"
            placeholder="例如: mail"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSaveLdapConfig">保存配置</el-button>
          <el-button @click="handleTestConnection">测试连接</el-button>
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
        label-width="150px"
        class="config-form"
      >
        <el-form-item label="失败登录次数限制" prop="max_login_attempts">
          <el-input-number
            v-model="securityConfigForm.max_login_attempts"
            :min="1"
            :max="100"
            placeholder="最大失败登录尝试次数"
          />
          <div class="form-help">用户登录失败达到此次数后将被锁定</div>
        </el-form-item>

        <el-form-item label="登录锁定时间(分钟)" prop="lockout_duration">
          <el-input-number
            v-model="securityConfigForm.lockout_duration"
            :min="1"
            :max="1440"
            placeholder="锁定时间(分钟)"
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
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { http } from '@/utils/http'
import { apiMap } from '@/config/api'

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

const ldapConfigFormRef = ref<FormInstance>()
const securityConfigFormRef = ref<FormInstance>()

// LDAP配置验证规则
const ldapConfigRules = ref<FormRules>({
  server_host: [
    { required: true, message: '请输入服务器地址', trigger: 'blur' }
  ],
  base_dn: [
    { required: true, message: '请输入基础DN', trigger: 'blur' }
  ],
  admin_dn: [
    { required: true, message: '请输入管理员DN', trigger: 'blur' }
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
    ElMessage.error(`获取LDAP配置失败。${error.msg || error}`)
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
    ElMessage.error(`获取安全配置失败。${error.msg || error}`)
  }
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
          ElMessage.success('LDAP配置保存成功')
        } else {
          ElMessage.error(res.msg)
        }
      } catch (error) {
        ElMessage.error(`保存LDAP配置失败。${error.msg || error}`)
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
          ElMessage.success('LDAP连接测试成功')
        } else {
          ElMessage.error(res.msg || 'LDAP连接测试失败')
        }
      } catch (error) {
        ElMessage.error(`LDAP连接测试失败。${error.msg || error}`)
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