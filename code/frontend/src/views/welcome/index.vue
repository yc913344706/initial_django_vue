<script setup lang="ts">
defineOptions({
  name: "Welcome"
});

import { getConfig } from "@/config";

const TITLE = getConfig("Title");
</script>

<template>
  <el-card>
    <h1>{{ TITLE }}</h1>

    <div>
      欢迎来到{{ TITLE }}
    </div>
  </el-card>
</template>
