<template>
  <div class="app-shell">
    <header class="topbar">
      <RouterLink to="/" class="brand"><span class="brand-icon" aria-hidden="true">↗</span><span>旅行助手<small>TRAVEL COMPANION</small></span></RouterLink>
      <nav aria-label="主导航"><RouterLink to="/">助手</RouterLink><RouterLink to="/confirm">确认</RouterLink><RouterLink to="/plans">我的规划</RouterLink><RouterLink to="/login">登录</RouterLink></nav>
    </header>
    <div class="scaffold-banner" role="note"><span class="status-dot" aria-hidden="true"></span>工程骨架 · 页面与接口待实现，当前不会保存或生成旅行规划</div>
    <main><RouterView /></main>
    <footer><span>旅行助手 H5</span><span>Vue 3 · FastAPI · MySQL 8.4</span></footer>
  </div>
</template>
