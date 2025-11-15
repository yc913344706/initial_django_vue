<script setup lang="ts">
defineOptions({
  name: "Welcome"
});

import { useI18n } from 'vue-i18n';
const { t } = useI18n();

import { getConfig } from "@/config";

const TITLE = getConfig("Title");
</script>

<template>
  <el-card>
    <h1>{{ TITLE }}</h1>

    <div>
      {{ t('page.title.welcome') }} {{ TITLE }}
    </div>
  </el-card>
</template>
