<script setup lang="ts">
defineProps<{ title: string; description: string; items?: string[] }>()
</script>
<template>
  <section class="panel placeholder">
    <span class="status-label">待实现</span><h2>{{ title }}</h2><p>{{ description }}</p>
    <ul v-if="items?.length" class="task-list"><li v-for="item in items" :key="item">{{ item }}</li></ul>
    <slot />
  </section>
</template>
