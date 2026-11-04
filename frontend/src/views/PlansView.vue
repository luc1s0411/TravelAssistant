<script setup lang="ts">
import ModulePlaceholder from '../components/ModulePlaceholder.vue'
</script>
<template>
  <header class="page-heading"><span class="eyebrow">YOUR JOURNEYS</span><h1>我的规划</h1><p>在这里回看每一段已经确认的旅程。</p></header>
  <ModulePlaceholder title="个人规划列表" description="列表接口待接入，当前未读取或创建任何个人规划。" :items="['登录身份下的分页列表', '打开计划详情与当前版本', '重命名和删除接口需后续补充契约']" />
</template>
