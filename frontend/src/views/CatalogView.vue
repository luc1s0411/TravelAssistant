<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ModulePlaceholder from '../components/ModulePlaceholder.vue'
import type { Category } from '../api/types'
const route = useRoute()
const labels: Record<Category, string> = { lodging: '住宿', dining: '美食', attraction: '景点' }
const title = computed(() => labels[route.params.category as Category])
</script>
<template>
  <RouterLink to="/" class="back-link">← 返回旅行助手</RouterLink>
  <header class="page-heading"><span class="eyebrow">EXPLORE</span><h1>{{ title }}选择</h1><p>{{ route.query.draft_id ? '已携带草稿编号，等待业务接口接入。' : '尚无当前草稿；页面仅展示模块入口。' }}</p></header>
  <ModulePlaceholder :title="title + '候选窗口'" description="筛选、候选卡片与加入规划功能待实现。" :items="['根据草稿的预算、日期和偏好筛选', '显示来源、价格性质及未知字段', '主动加入或移除，校验草稿 revision', '支持空结果、无权限与超时状态']" />
</template>
