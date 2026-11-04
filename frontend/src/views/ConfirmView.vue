<script setup lang="ts">
import ModulePlaceholder from '../components/ModulePlaceholder.vue'
</script>
<template>
  <header class="page-heading"><span class="eyebrow">CONFIRM</span><h1>规划确认</h1><p>确认本次使用的需求与选择。</p></header>
  <ModulePlaceholder title="确认资料并生成" description="确认和生成接口已定义，当前不会保存快照或生成行程。" :items="['勾选本次项目，设置日期、数量和必选性', '显式接受留空分类，说明未知价格', '确认对应精确草稿版本', '使用同一个幂等键安全重试生成请求']" />
</template>
