<template>
  <el-config-provider :locale="zhCn">
    <div id="app-container">
      <!-- 顶部导航栏 -->
      <el-header class="app-header">
        <div class="header-left">
          <img src="/favicon.svg" alt="logo" class="logo" />
          <span class="title">松材线虫病CT检测系统</span>
        </div>
        <div class="header-right">
          <el-tag type="success" size="small">🌲 智能诊断平台</el-tag>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-container class="main-container">
        <!-- 侧边菜单 -->
        <el-aside width="220px" class="sidebar">
          <el-menu
            :default-active="activeMenu"
            router
            background-color="#1a2940"
            text-color="#c9d8ec"
            active-text-color="#4fc3f7"
          >
            <el-menu-item index="/">
              <el-icon><Monitor /></el-icon>
              <span>系统概览</span>
            </el-menu-item>
            <el-menu-item index="/detect">
              <el-icon><Upload /></el-icon>
              <span>影像检测</span>
            </el-menu-item>
            <el-menu-item index="/history">
              <el-icon><List /></el-icon>
              <span>检测历史</span>
            </el-menu-item>
            <el-menu-item index="/about">
              <el-icon><InfoFilled /></el-icon>
              <span>关于系统</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- 路由视图 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  background: #f0f4f8;
}

#app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #1a2940 0%, #0d3b6e 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px !important;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  width: 36px;
  height: 36px;
}

.title {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 1px;
}

.main-container {
  flex: 1;
  overflow: hidden;
}

.sidebar {
  background: #1a2940 !important;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.2);
  overflow-y: auto;
}

.sidebar .el-menu {
  border-right: none;
  padding-top: 16px;
}

.main-content {
  background: #f0f4f8;
  overflow-y: auto;
  padding: 24px;
}
</style>
