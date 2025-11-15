<template>
  <el-dropdown @command="handleCommand">
    <span class="el-dropdown-link">
      <svg-icon icon-class="language" />
      <span>{{ currentLangText }}</span>
    </span>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="zh-CN" :disabled="currentLang === 'zh-CN'">
          中文
        </el-dropdown-item>
        <el-dropdown-item command="en-US" :disabled="currentLang === 'en-US'">
          English
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { locale } = useI18n();

const currentLang = computed(() => locale.value);
const currentLangText = computed(() => {
  return currentLang.value === 'zh-CN' ? '中文' : 'English';
});

const handleCommand = (lang: string) => {
  if (lang !== currentLang.value) {
    locale.value = lang;
    localStorage.setItem('lang', lang);
  }
};
</script>

<style scoped>
.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>