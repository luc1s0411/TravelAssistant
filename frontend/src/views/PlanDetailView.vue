<script setup lang="ts">
import PlanMap from '../components/PlanMap.vue'
import PlanTimeline from '../components/PlanTimeline.vue'
import ModulePlaceholder from '../components/ModulePlaceholder.vue'
</script>
<template>
  <RouterLink to="/plans" class="back-link">← 返回我的规划</RouterLink>
  <header class="page-heading"><span class="eyebrow">ITINERARY</span><h1>规划详情</h1><p>日程、地图、预算与版本查询的页面入口。</p></header>
  <div class="workspace-grid"><PlanTimeline :items="[]" /><PlanMap /></div>
  <ModulePlaceholder class="detail-note" title="查询与修改" description="待接入计划查询、修改预览与用户确认。" :items="['查询只读，修改先预览', '确认前校验 expected_version', '保留未受影响的日期与历史成功版本']" />
</template>
