<script setup lang="ts">
defineOptions({
  name: "Welcome"
});

import { getConfig } from "@/config";

const TITLE = getConfig("Title");
</script>

<template>
  <h1>{{ TITLE }}</h1>
</template>
