<template>
  <a-layout class="app-layout">
    
    <div class="header-container">
      <div class="system-header">
        <div class="logo-area">
          <div class="logo-icon">C++</div>
          <span class="system-title">C++作业批改系统</span>
        </div>
        </div>
      
      <div class="nav-container">
        <a-menu 
          mode="horizontal" 
          :selected-keys="selectedKeys"
          @menu-item-click="handleMenuClick"
          class="custom-menu"
        >
          <a-menu-item key="/grader">文字识别</a-menu-item>
          <a-menu-item key="/tasks">任务管理</a-menu-item>
        </a-menu>
      </div>
    </div>

    <a-layout-content class="content-wrapper">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <keep-alive>
            <component :is="Component" />
          </keep-alive>
        </transition>
      </router-view>
    </a-layout-content>

  </a-layout>
</template>

<script setup>
import { useRouter,useRoute } from 'vue-router'
import { computed } from 'vue'
const router = useRouter()
const route = useRoute()
const handleMenuClick = (key) => {
  router.push(key)
}
const selectedKeys = computed(() => {
  // 如果当前路径以 /tasks 开头，就高亮任务管理
  if (route.path.startsWith('/tasks')) {
    return ['/tasks']
  }
  // 否则默认高亮文字识别
  return ['/grader']
})

</script>

<style scoped>
/* 局部样式 */
.app-layout {
  height: 100vh;
  width: 100vw;
  background-color: #f2f3f5; 
  display: flex;
  flex-direction: column;
  overflow: hidden; 
}

/* === 头部设计 === */
.header-container {
  background: #fff;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
  z-index: 100;
  flex-shrink: 0;
}

.system-header {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 40px;
  border-bottom: 1px solid #f2f3f5;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #165dff 0%, #722ed1 100%);
  border-radius: 8px;
  color: #fff;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(22, 93, 255, 0.3);
}

.system-title {
  font-size: 20px;
  font-weight: 600;
  color: #1d2129;
  letter-spacing: 0.5px;
}

.nav-container {
  padding: 0 40px;
  background: #fff;
}

:deep(.arco-menu-horizontal .arco-menu-inner) { padding: 0; }
:deep(.arco-menu-light .arco-menu-item.arco-menu-selected) { color: #165dff; font-weight: 600; }
:deep(.arco-menu-light .arco-menu-item:hover) { background-color: transparent; color: #165dff; }

/* === 内容区 === */
.content-wrapper {
  flex: 1;
  padding: 0; 
  overflow: hidden; /* 禁止内部滚动 */
  position: relative;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

<style>
/* 隐藏 Chrome/Safari/Edge 的滚动条 */
::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
}

/* 隐藏 Firefox/IE 的滚动条 */
html, body, #app {
  scrollbar-width: none !important; /* Firefox */
  -ms-overflow-style: none !important; /* IE 10+ */
  overflow: hidden !important; /* 确保 body 也不滚动 */
}
</style>