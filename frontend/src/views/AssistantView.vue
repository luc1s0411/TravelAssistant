<script setup lang="ts">
import { computed } from 'vue'
import { ElInput, ElButton } from 'element-plus'
import 'element-plus/es/components/input/style/css'
import 'element-plus/es/components/button/style/css'
import { useDraftStore } from '../stores/draft'
import ModulePlaceholder from '../components/ModulePlaceholder.vue'
const draft = useDraftStore()
const query = computed(() => draft.current ? { draft_id: draft.current.draft_id } : {})
const windows = [
  { category: 'lodging', number: '01', title: '住宿', note: '每间每晚 · 入住与离店' },
  { category: 'dining', number: '02', title: '美食', note: '每人每天 · 口味与饮食限制' },
  { category: 'attraction', number: '03', title: '景点', note: '每人本次 · 兴趣与可用时间' },
]
</script>
<template>
  <header class="page-heading"><span class="eyebrow">TRAVEL ASSISTANT</span><h1>让下一段旅程，<br />从这里开始。</h1><p>告诉助手你的想法，再慢慢挑选喜欢的地方。</p></header>
  <div class="workspace-grid">
    <section class="panel conversation">
      <div class="section-heading"><h2>旅行助手</h2><span class="status-label">功能占位</span></div>
      <div class="empty-conversation"><span aria-hidden="true">✳</span><h3>先聊聊，你想去哪里？</h3><p>此处将收集目的地、出行日期、人数与分类预算。</p></div>
      <label for="trip-message" class="sr-only">出行需求</label>
      <ElInput id="trip-message" disabled placeholder="对话功能待实现，当前不会发送或保存需求" />
      <ElButton type="primary" disabled class="send-button">发送需求</ElButton>
    </section>
    <ModulePlaceholder title="本次出行" description="尚未创建草稿。" :items="['目的地与日期', '人数与房间数', '分类预算与偏好', '已选项目与确认版本']" />
  </div>
  <div class="section-heading selection-heading"><h2>三个选择窗口</h2><span class="muted">共享同一份规划草稿</span></div>
  <div class="category-grid">
    <RouterLink v-for="window in windows" :key="window.category" :to="{ name: 'catalog', params: { category: window.category }, query }" class="category-card">
      <span class="category-number">{{ window.number }}</span><h3>{{ window.title }} <span aria-hidden="true">↗</span></h3><p>{{ window.note }}</p>
    </RouterLink>
  </div>
</template>
