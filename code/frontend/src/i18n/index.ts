import { createI18n } from 'vue-i18n';
import zhCN from './locales/zh-CN.json';
import enUS from './locales/en-US.json';

// 定义支持的语言
const messages = {
  'zh-CN': zhCN,
  'en-US': enUS
};

// 创建 i18n 实例
const i18n = createI18n({
  legacy: false, // 使用 Composition API 模式
  locale: localStorage.getItem('lang') || 'en-US', // 从 localStorage 获取语言设置，默认中文
  fallbackLocale: 'en-US', // 回退语言
  messages
});

// 导出 i18n 实例
export default i18n;

// 导出全局 t 函数
export const globalT = (key: string) => {
  return i18n.global.t(key);
};