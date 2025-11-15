<script setup lang="ts">
import {
  ref,
  unref,
  watch,
  reactive,
  computed,
  nextTick,
  onUnmounted,
  onBeforeMount
} from "vue";
import { emitter } from "@/utils/mitt";
import LayPanel from "../lay-panel/index.vue";
import { useNav } from "@/layout/hooks/useNav";
import { useAppStoreHook } from "@/store/modules/app";
import { useMultiTagsStoreHook } from "@/store/modules/multiTags";
import Segmented, { type OptionsType } from "@/components/ReSegmented";
import { useDataThemeChange } from "@/layout/hooks/useDataThemeChange";
import { useDark, useGlobal, debounce, isNumber } from "@pureadmin/utils";
import { useI18n } from 'vue-i18n';

import Check from "@iconify-icons/ep/check";
import LeftArrow from "@iconify-icons/ri/arrow-left-s-line";
import RightArrow from "@iconify-icons/ri/arrow-right-s-line";
import DayIcon from "@/assets/svg/day.svg?component";
import DarkIcon from "@/assets/svg/dark.svg?component";
import SystemIcon from "@/assets/svg/system.svg?component";

const { t, locale } = useI18n();

const { device } = useNav();
const { isDark } = useDark();
const { $storage } = useGlobal<GlobalPropertiesApi>();

const mixRef = ref();
const verticalRef = ref();
const horizontalRef = ref();

const {
  dataTheme,
  overallStyle,
  layoutTheme,
  themeColors,
  toggleClass,
  dataThemeChange,
  setLayoutThemeColor
} = useDataThemeChange();

/* body添加layout属性，作用于src/style/sidebar.scss */
if (unref(layoutTheme)) {
  const layout = unref(layoutTheme).layout;
  const theme = unref(layoutTheme).theme;
  document.documentElement.setAttribute("data-theme", theme);
  setLayoutModel(layout);
}

/** 默认灵动模式 */
const markValue = ref($storage.configure?.showModel ?? "smart");

const logoVal = ref($storage.configure?.showLogo ?? true);

const settings = reactive({
  greyVal: $storage.configure.grey,
  weakVal: $storage.configure.weak,
  tabsVal: $storage.configure.hideTabs,
  showLogo: $storage.configure.showLogo,
  showModel: $storage.configure.showModel,
  hideFooter: $storage.configure.hideFooter,
  multiTagsCache: $storage.configure.multiTagsCache,
  stretch: $storage.configure.stretch
});

const getThemeColorStyle = computed(() => {
  return color => {
    return { background: color };
  };
});

/** 当网页整体为暗色风格时不显示亮白色主题配色切换选项 */
const showThemeColors = computed(() => {
  return themeColor => {
    return themeColor === "light" && isDark.value ? false : true;
  };
});

function storageConfigureChange<T>(key: string, val: T): void {
  const storageConfigure = $storage.configure;
  storageConfigure[key] = val;
  $storage.configure = storageConfigure;
}

/** 灰色模式设置 */
const greyChange = (value): void => {
  const htmlEl = document.querySelector("html");
  toggleClass(settings.greyVal, "html-grey", htmlEl);
  storageConfigureChange("grey", value);
};

/** 色弱模式设置 */
const weekChange = (value): void => {
  const htmlEl = document.querySelector("html");
  toggleClass(settings.weakVal, "html-weakness", htmlEl);
  storageConfigureChange("weak", value);
};

/** 隐藏标签页设置 */
const tagsChange = () => {
  const showVal = settings.tabsVal;
  storageConfigureChange("hideTabs", showVal);
  emitter.emit("tagViewsChange", showVal as unknown as string);
};

/** 隐藏页脚设置 */
const hideFooterChange = () => {
  const hideFooter = settings.hideFooter;
  storageConfigureChange("hideFooter", hideFooter);
};

/** 标签页持久化设置 */
const multiTagsCacheChange = () => {
  const multiTagsCache = settings.multiTagsCache;
  storageConfigureChange("multiTagsCache", multiTagsCache);
  useMultiTagsStoreHook().multiTagsCacheChange(multiTagsCache);
};

function onChange({ option }) {
  const { value } = option;
  markValue.value = value;
  storageConfigureChange("showModel", value);
  emitter.emit("tagViewsShowModel", value);
}

/** 侧边栏Logo */
function logoChange() {
  unref(logoVal)
    ? storageConfigureChange("showLogo", true)
    : storageConfigureChange("showLogo", false);
  emitter.emit("logoChange", unref(logoVal));
}

function setFalse(Doms): any {
  Doms.forEach(v => {
    toggleClass(false, "is-select", unref(v));
  });
}

/** 页宽 */
const stretchTypeOptions = computed<Array<OptionsType>>(() => {
  return [
    {
      label: t('setting.fixedWidth'),
      tip: t('setting.fixedWidthTip'),
      value: "fixed"
    },
    {
      label: t('setting.customWidth'),
      tip: t('setting.customWidthTip'),
      value: "custom"
    }
  ];
});

const setStretch = value => {
  settings.stretch = value;
  storageConfigureChange("stretch", value);
};

const stretchTypeChange = ({ option }) => {
  const { value } = option;
  value === "custom" ? setStretch(1440) : setStretch(false);
};

/** 主题色 激活选择项 */
const getThemeColor = computed(() => {
  return current => {
    if (
      current === layoutTheme.value.theme &&
      layoutTheme.value.theme !== "light"
    ) {
      return "#fff";
    } else if (
      current === layoutTheme.value.theme &&
      layoutTheme.value.theme === "light"
    ) {
      return "#1d2b45";
    } else {
      return "transparent";
    }
  };
});

const pClass = computed(() => {
  return ["mb-[12px]", "font-medium", "text-sm", "dark:text-white"];
});

const themeOptions = computed<Array<OptionsType>>(() => {
  return [
    {
      label: t('setting.dayTheme'),
      icon: DayIcon,
      theme: "light",
      tip: t('setting.dayThemeTip'),
      iconAttrs: { fill: isDark.value ? "#fff" : "#000" }
    },
    {
      label: t('setting.darkTheme'),
      icon: DarkIcon,
      theme: "dark",
      tip: t('setting.darkThemeTip'),
      iconAttrs: { fill: isDark.value ? "#fff" : "#000" }
    },
    {
      label: t('setting.systemTheme'),
      icon: SystemIcon,
      theme: "system",
      tip: t('setting.systemThemeTip'),
      iconAttrs: { fill: isDark.value ? "#fff" : "#000" }
    }
  ];
});

const markOptions = computed<Array<OptionsType>>(() => {
  return [
    {
      label: t('setting.smartTag'),
      tip: t('setting.smartTagTip'),
      value: "smart"
    },
    {
      label: t('setting.cardTag'),
      tip: t('setting.cardTagTip'),
      value: "card"
    },
    {
      label: t('setting.chromeTag'),
      tip: t('setting.chromeTagTip'),
      value: "chrome"
    }
  ];
});

/** 设置导航模式 */
function setLayoutModel(layout: string) {
  layoutTheme.value.layout = layout;
  window.document.body.setAttribute("layout", layout);
  $storage.layout = {
    layout,
    theme: layoutTheme.value.theme,
    darkMode: $storage.layout?.darkMode,
    sidebarStatus: $storage.layout?.sidebarStatus,
    epThemeColor: $storage.layout?.epThemeColor,
    themeColor: $storage.layout?.themeColor,
    overallStyle: $storage.layout?.overallStyle
  };
  useAppStoreHook().setLayout(layout);
}

watch($storage, ({ layout }) => {
  switch (layout["layout"]) {
    case "vertical":
      toggleClass(true, "is-select", unref(verticalRef));
      debounce(setFalse([horizontalRef]), 50);
      debounce(setFalse([mixRef]), 50);
      break;
    case "horizontal":
      toggleClass(true, "is-select", unref(horizontalRef));
      debounce(setFalse([verticalRef]), 50);
      debounce(setFalse([mixRef]), 50);
      break;
    case "mix":
      toggleClass(true, "is-select", unref(mixRef));
      debounce(setFalse([verticalRef]), 50);
      debounce(setFalse([horizontalRef]), 50);
      break;
  }
});

const mediaQueryList = window.matchMedia("(prefers-color-scheme: dark)");

/** 根据操作系统主题设置平台整体风格 */
function updateTheme() {
  if (overallStyle.value !== "system") return;
  if (mediaQueryList.matches) {
    dataTheme.value = true;
  } else {
    dataTheme.value = false;
  }
  dataThemeChange(overallStyle.value);
}

function removeMatchMedia() {
  mediaQueryList.removeEventListener("change", updateTheme);
}

/** 监听操作系统主题改变 */
function watchSystemThemeChange() {
  updateTheme();
  removeMatchMedia();
  mediaQueryList.addEventListener("change", updateTheme);
}

// 语言切换功能
const languageOptions = [
  { value: 'zh-CN', label: '简体中文' },
  { value: 'en-US', label: 'English' }
];

const handleLanguageChange = (lang: string) => {
  locale.value = lang;
  localStorage.setItem('lang', lang);
};

onBeforeMount(() => {
  /* 初始化系统配置 */
  nextTick(() => {
    watchSystemThemeChange();
    settings.greyVal &&
      document.querySelector("html")?.classList.add("html-grey");
    settings.weakVal &&
      document.querySelector("html")?.classList.add("html-weakness");
    settings.tabsVal && tagsChange();
    settings.hideFooter && hideFooterChange();
  });
});

onUnmounted(() => removeMatchMedia);
</script>

<template>
  <LayPanel>
    <div class="p-5">
      <p :class="pClass">{{ t('setting.overallStyle') }}</p>
      <Segmented
        resize
        class="select-none"
        :modelValue="overallStyle === 'system' ? 2 : dataTheme ? 1 : 0"
        :options="themeOptions"
        @change="
          theme => {
            theme.index === 1 && theme.index !== 2
              ? (dataTheme = true)
              : (dataTheme = false);
            overallStyle = theme.option.theme;
            dataThemeChange(theme.option.theme);
            theme.index === 2 && watchSystemThemeChange();
          }
        "
      />

      <p :class="['mt-5', pClass]">{{ t('setting.themeColor') }}</p>
      <ul class="theme-color">
        <li
          v-for="(item, index) in themeColors"
          v-show="showThemeColors(item.themeColor)"
          :key="index"
          :style="getThemeColorStyle(item.color)"
          @click="setLayoutThemeColor(item.themeColor)"
        >
          <el-icon
            style="margin: 0.1em 0.1em 0 0"
            :size="17"
            :color="getThemeColor(item.themeColor)"
          >
            <IconifyIconOffline :icon="Check" />
          </el-icon>
        </li>
      </ul>

      <p :class="['mt-5', pClass]">{{ t('setting.navMode') }}</p>
      <ul class="pure-theme">
        <li
          ref="verticalRef"
          v-tippy="{
            content: t('setting.navModeVerticalTip'),
            zIndex: 41000
          }"
          :class="layoutTheme.layout === 'vertical' ? 'is-select' : ''"
          @click="setLayoutModel('vertical')"
        >
          <div />
          <div />
        </li>
        <li
          v-if="device !== 'mobile'"
          ref="horizontalRef"
          v-tippy="{
            content: t('setting.navModeHorizontalTip'),
            zIndex: 41000
          }"
          :class="layoutTheme.layout === 'horizontal' ? 'is-select' : ''"
          @click="setLayoutModel('horizontal')"
        >
          <div />
          <div />
        </li>
        <li
          v-if="device !== 'mobile'"
          ref="mixRef"
          v-tippy="{
            content: t('setting.navModeMixTip'),
            zIndex: 41000
          }"
          :class="layoutTheme.layout === 'mix' ? 'is-select' : ''"
          @click="setLayoutModel('mix')"
        >
          <div />
          <div />
        </li>
      </ul>

      <span v-if="useAppStoreHook().getViewportWidth > 1280">
        <p :class="['mt-5', pClass]">{{ t('setting.pageWidth') }}</p>
        <Segmented
          resize
          class="mb-2 select-none"
          :modelValue="isNumber(settings.stretch) ? 1 : 0"
          :options="stretchTypeOptions"
          @change="stretchTypeChange"
        />
        <el-input-number
          v-if="isNumber(settings.stretch)"
          v-model="settings.stretch as number"
          :min="1280"
          :max="1600"
          controls-position="right"
          @change="value => setStretch(value)"
        />
        <button
          v-else
          v-ripple="{ class: 'text-gray-300' }"
          class="bg-transparent flex-c w-full h-20 rounded-md border border-[var(--pure-border-color)]"
          @click="setStretch(!settings.stretch)"
        >
          <div
            class="flex-bc transition-all duration-300"
            :class="[settings.stretch ? 'w-[24%]' : 'w-[50%]']"
            style="color: var(--el-color-primary)"
          >
            <IconifyIconOffline
              :icon="settings.stretch ? RightArrow : LeftArrow"
              height="20"
            />
            <div
              class="flex-grow border-b border-dashed"
              style="border-color: var(--el-color-primary)"
            />
            <IconifyIconOffline
              :icon="settings.stretch ? LeftArrow : RightArrow"
              height="20"
            />
          </div>
        </button>
      </span>

      <p :class="['mt-4', pClass]">{{ t('setting.tabStyle') }}</p>
      <Segmented
        resize
        class="select-none"
        :modelValue="markValue === 'smart' ? 0 : markValue === 'card' ? 1 : 2"
        :options="markOptions"
        @change="onChange"
      />

      <p class="mt-5 font-medium text-sm dark:text-white">{{ t('setting.interfaceDisplay') }}</p>
      <ul class="setting">
        <li>
          <span class="dark:text-white">{{ t('setting.languageSwitch') }}</span>
          <el-select
            v-model="locale"
            :placeholder="$t('common.selectLanguage')"
            @change="handleLanguageChange"
            style="width: 100px;"
            :teleported="false"
          >
            <el-option
              v-for="item in languageOptions"
              :key="item.value"
              :label="t('setting.language.' + item.value)"
              :value="item.value"
            />
          </el-select>
        </li>
        <li>
          <span class="dark:text-white">{{ t('setting.greyMode') }}</span>
          <el-switch
            v-model="settings.greyVal"
            inline-prompt
            :active-text="t('setting.on')"
            :inactive-text="t('setting.off')"
            @change="greyChange"
          />
        </li>
        <li>
          <span class="dark:text-white">{{ t('setting.weakMode') }}</span>
          <el-switch
            v-model="settings.weakVal"
            inline-prompt
            :active-text="t('setting.on')"
            :inactive-text="t('setting.off')"
            @change="weekChange"
          />
        </li>
        <li>
          <span class="dark:text-white">{{ t('setting.hideTabs') }}</span>
          <el-switch
            v-model="settings.tabsVal"
            inline-prompt
            :active-text="t('setting.on')"
            :inactive-text="t('setting.off')"
            @change="tagsChange"
          />
        </li>
        <li>
          <span class="dark:text-white">{{ t('setting.hideFooter') }}</span>
          <el-switch
            v-model="settings.hideFooter"
            inline-prompt
            :active-text="t('setting.on')"
            :inactive-text="t('setting.off')"
            @change="hideFooterChange"
          />
        </li>
        <li>
          <span class="dark:text-white">{{ t('setting.logo') }}</span>
          <el-switch
            v-model="logoVal"
            inline-prompt
            :active-value="true"
            :inactive-value="false"
            :active-text="t('setting.on')"
            :inactive-text="t('setting.off')"
            @change="logoChange"
          />
        </li>
        <li>
          <span class="dark:text-white">{{ t('setting.tabPersistence') }}</span>
          <el-switch
            v-model="settings.multiTagsCache"
            inline-prompt
            :active-text="t('setting.on')"
            :inactive-text="t('setting.off')"
            @change="multiTagsCacheChange"
          />
        </li>
      </ul>
    </div>
  </LayPanel>
</template>

<style lang="scss" scoped>
:deep(.el-divider__text) {
  font-size: 16px;
  font-weight: 700;
}

:deep(.el-switch__core) {
  --el-switch-off-color: var(--pure-switch-off-color);

  min-width: 36px;
  height: 18px;
}

:deep(.el-switch__core .el-switch__action) {
  height: 14px;
}

.theme-color {
  height: 20px;

  li {
    float: left;
    height: 20px;
    margin-right: 8px;
    cursor: pointer;
    border-radius: 4px;

    &:nth-child(1) {
      border: 1px solid #ddd;
    }
  }
}

.pure-theme {
  display: flex;
  gap: 12px;

  li {
    position: relative;
    width: 46px;
    height: 36px;
    overflow: hidden;
    cursor: pointer;
    background: #f0f2f5;
    border-radius: 4px;
    box-shadow: 0 1px 2.5px 0 rgb(0 0 0 / 18%);

    &:nth-child(1) {
      div {
        &:nth-child(1) {
          width: 30%;
          height: 100%;
          background: #1b2a47;
        }

        &:nth-child(2) {
          position: absolute;
          top: 0;
          right: 0;
          width: 70%;
          height: 30%;
          background: #fff;
          box-shadow: 0 0 1px #888;
        }
      }
    }

    &:nth-child(2) {
      div {
        &:nth-child(1) {
          width: 100%;
          height: 30%;
          background: #1b2a47;
          box-shadow: 0 0 1px #888;
        }
      }
    }

    &:nth-child(3) {
      div {
        &:nth-child(1) {
          width: 100%;
          height: 30%;
          background: #1b2a47;
          box-shadow: 0 0 1px #888;
        }

        &:nth-child(2) {
          position: absolute;
          bottom: 0;
          left: 0;
          width: 30%;
          height: 70%;
          background: #fff;
          box-shadow: 0 0 1px #888;
        }
      }
    }
  }
}

.is-select {
  border: 2px solid var(--el-color-primary);
}

.setting {
  li {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 3px 0;
    font-size: 14px;
  }
}
.el-select-dropdown {
  z-index: 999999;  /* 提升 select 下拉框层级 */
}
</style>