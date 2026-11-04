<script setup lang="ts">
import ModulePlaceholder from '../components/ModulePlaceholder.vue'
</script>
<template>
  <header class="page-heading"><span class="eyebrow">ACCOUNT</span><h1>登录</h1><p>会话与用户隔离的接入入口。</p></header>
  <ModulePlaceholder title="认证模块" description="登录与退出接口已定义，认证逻辑尚未实现。" :items="['接入你已有的用户 ORM 模型', '验证密码、签发与撤销服务端会话', '统一 get_current_user 身份依赖', '登录成功后恢复当前用户数据']" />
</template>
