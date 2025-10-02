<script setup lang="ts">
import Motion from "./utils/motion";
import { useRouter } from "vue-router";
import { message } from "@/utils/message";
import { loginRules } from "./utils/rule";
import { useNav } from "@/layout/hooks/useNav";
import type { FormInstance } from "element-plus";
import { useLayout } from "@/layout/hooks/useLayout";
import { useUserStoreHook } from "@/store/modules/user";
import { initRouter, getTopMenu } from "@/router/utils";
import { bg, avatar, illustration } from "./utils/static";
import { useRenderIcon } from "@/components/ReIcon/src/hooks";
import { ref, reactive, toRaw, onMounted, onBeforeUnmount } from "vue";
import { useDataThemeChange } from "@/layout/hooks/useDataThemeChange";
import { DataInfo } from "@/utils/auth";

import dayIcon from "@/assets/svg/day.svg?component";
import darkIcon from "@/assets/svg/dark.svg?component";
import Lock from "@iconify-icons/ri/lock-fill";
import User from "@iconify-icons/ri/user-3-fill";
import logger from "@/utils/logger";
import Cookies from "js-cookie";
import { setToken } from "@/utils/auth";

defineOptions({
  name: "Login"
});
const router = useRouter();
const loading = ref(false);
const ruleFormRef = ref<FormInstance>();

const { initStorage } = useLayout();
initStorage();

const { dataTheme, overallStyle, dataThemeChange } = useDataThemeChange();
dataThemeChange(overallStyle.value);
const { title } = useNav();

const ruleForm = reactive({
  username: "admin",
  password: "Admin@123"
});

const onLogin = async (formEl: FormInstance | undefined) => {
  logger.debug('开始登录')
  if (!formEl) return;
  await formEl.validate((valid, fields) => {
    if (valid) {
      logger.debug('表单验证通过')
      loading.value = true;
      useUserStoreHook()
        .loginByUsername({ username: ruleForm.username, password: ruleForm.password })
        .then(res => {
          logger.debug('登录成功: loginByUsername')
          if (res.success) {
            logger.debug('登录成功: loginByUsername: res.success')
            // 获取后端路由
            return initRouter().then(() => {
              logger.debug('路由初始化完成')
              const topMenu = getTopMenu(true);
              logger.debug('获取到的topMenu:', topMenu)
              if (topMenu?.path) {
                logger.debug('准备跳转到菜单页面:', topMenu.path)
                // 检查路由是否存在
                if (router.hasRoute(topMenu.path)) {
                  router.push(topMenu.path)
                    .then(() => {
                      logger.debug('跳转成功' + topMenu.path)
                      message("登录成功", { type: "success" });
                    })
                    .catch(err => {
                      logger.error('路由跳转失败:', err)
                      // message("路由跳转失败: " + err.message, { type: "error" });
                      // 如果跳转失败，尝试跳转到首页
                      router.push("/").then(() => {
                        logger.debug('跳转到首页成功')
                        message("登录成功", { type: "success" });
                      }).catch(e => {
                        logger.error('跳转到首页也失败:', e)
                        message("登录失败，跳转到首页失败", { type: "error" });
                      });
                    });
                } else {
                  logger.error('路由不存在:', topMenu.path)
                  // message("目标路由不存在，将跳转到首页", { type: "warning" });
                  router.push("/").then(() => {
                    logger.debug('跳转到首页成功')
                    message("登录成功", { type: "success" });
                  }).catch(e => {
                    logger.error('跳转到首页失败:', e)
                    message("登录失败，跳转到首页失败", { type: "error" });
                  });
                }
              } else {
                logger.debug('没有可用的菜单，准备跳转到首页')
                router.push("/")
                  .then(() => {
                    logger.debug('跳转到首页成功')
                    message("登录成功", { type: "success" });
                  })
                  .catch(err => {
                    logger.error('跳转到首页失败:', err)
                    message("登录失败，跳转到首页失败", { type: "error" });
                  });
              }
            }).catch(err => {
              logger.error('路由初始化失败:', err)
              message("登录失败，路由初始化失败", { type: "error" });
            });
          } else {
            logger.error('登录失败，返回结果:', res)
            message("登录失败", { type: "error" });
          }
        }).catch(error => {
          logger.error('登录过程发生错误:', error)
          let _error_msg = "登录失败."
          if (error.msg) {
            _error_msg += error.msg
          } else if (error.message) {
            _error_msg += error.message
          }
          message(_error_msg, { type: "error" });
        })
        .finally(() => {
          loading.value = false;
          logger.debug('登录流程结束，loading状态:', loading.value)
        });
    }
  });
};

/** 使用公共函数，避免`removeEventListener`失效 */
function onkeypress({ code }: KeyboardEvent) {
  if (["Enter", "NumpadEnter"].includes(code)) {
    onLogin(ruleFormRef.value);
  }
}

onMounted(async () => {
  // 判断是否已经登录
  logger.debug('判断是否已经登录')
  const accessToken = Cookies.get(import.meta.env.VITE_ACCESS_TOKEN_NAME);
  const refreshToken = Cookies.get(import.meta.env.VITE_REFRESH_TOKEN_NAME);
  // 如果有access_token, 跳转到上一个页面，如果没有上一个页面，则跳转到首页

  let _already_login = false;
  if (accessToken) {
    logger.debug('有access_token, 跳转到上一个页面')
    _already_login = true;
  } else if (refreshToken) {
    logger.debug('没有access_token, 有refresh_token, 调用刷新token接口')
    // 如果有 refresh_token，则调用刷新token接口
    const res = await useUserStoreHook().handRefreshToken({ 
      refreshToken: refreshToken 
    });
    if (res.success) {
      logger.debug('刷新token成功')
      setToken(res.data);
      _already_login = true;
    } else {
      logger.debug('刷新token失败，需要保持登录页面' + res)
    }
  } else {
    logger.debug('没有access_token, 没有refresh_token, 需要保持登录页面')
  }

  if (_already_login) {
    logger.debug('已登录，跳转到上一个页面')

    const topMenu = getTopMenu(true);
    if (topMenu?.path) {
      logger.debug('准备跳转到菜单页面:', topMenu.path)
      // 检查路由是否存在
      if (router.hasRoute(topMenu.path)) {
        router.push(topMenu.path)
          .then(() => {
            logger.debug('跳转成功')
          })
          .catch(err => {
            logger.error('路由跳转失败:', err)
            // 如果跳转失败，尝试跳转到首页
            router.push("/").catch(e => {
              logger.error('跳转到首页也失败:', e)
            });
          });
      } else {
        logger.error('路由不存在:', topMenu.path)
        // 如果路由不存在，跳转到首页
        router.push("/").catch(e => {
          logger.error('跳转到首页失败:', e)
        });
      }
      return;
    } else {
      // 如果没有可用的菜单，跳转到首页
      logger.debug('没有可用的菜单，跳转到首页')
      router.push("/")
        .then(() => {
          logger.debug('跳转到首页成功')
        })
        .catch(err => {
          logger.error('跳转到首页失败:', err)
        });
      return;
    }
  }
  logger.debug('最终，保持登录页面...')

  // 如果有 refresh_token，则调用刷新token接口
  
  window.document.addEventListener("keypress", onkeypress);
});

onBeforeUnmount(() => {
  window.document.removeEventListener("keypress", onkeypress);
});
</script>

<template>
  <div class="select-none">
    <img :src="bg" class="wave" />
    <div class="flex-c absolute right-5 top-3">
      <!-- 主题 -->
      <el-switch
        v-model="dataTheme"
        inline-prompt
        :active-icon="dayIcon"
        :inactive-icon="darkIcon"
        @change="dataThemeChange"
      />
    </div>
    <div class="login-container">
      <div class="img">
        <component :is="toRaw(illustration)" />
      </div>
      <div class="login-box">
        <div class="login-form">
          <avatar class="avatar" />
          <Motion>
            <h2 class="outline-none">{{ title }}</h2>
          </Motion>

          <el-form
            ref="ruleFormRef"
            :model="ruleForm"
            :rules="loginRules"
            size="large"
          >
            <Motion :delay="100">
              <el-form-item
                :rules="[
                  {
                    required: true,
                    message: '请输入账号',
                    trigger: 'blur'
                  }
                ]"
                prop="username"
              >
                <el-input
                  v-model="ruleForm.username"
                  clearable
                  placeholder="账号"
                  :prefix-icon="useRenderIcon(User)"
                />
              </el-form-item>
            </Motion>

            <Motion :delay="150">
              <el-form-item prop="password">
                <el-input
                  v-model="ruleForm.password"
                  clearable
                  show-password
                  placeholder="密码"
                  :prefix-icon="useRenderIcon(Lock)"
                />
              </el-form-item>
            </Motion>

            <Motion :delay="250">
              <el-button
                class="w-full mt-4"
                size="default"
                type="primary"
                :loading="loading"
                @click="onLogin(ruleFormRef)"
              >
                登录
              </el-button>
            </Motion>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url("@/style/login.css");
</style>

<style lang="scss" scoped>
:deep(.el-input-group__append, .el-input-group__prepend) {
  padding: 0;
}
</style>
