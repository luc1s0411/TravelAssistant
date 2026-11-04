<script setup lang="ts">
import type { PlanItem } from '../api/types'
defineProps<{ items: PlanItem[] }>()
</script>
<template>
  <section class="panel"><h2>行程时间线</h2>
    <p v-if="!items.length" class="muted">暂无行程。时间线组件已预留，等待接入已保存的计划。</p>
    <ol v-else class="task-list"><li v-for="item in items" :key="item.plan_item_id">{{ item.date }} · {{ item.start_time ?? '时间待确认' }} · {{ item.name }}</li></ol>
  </section>
</template>
