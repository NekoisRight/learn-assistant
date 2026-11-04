<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const showHeader = computed(() => route.path !== '/login')

onMounted(() => {
  if (auth.token && !auth.user) {
    void auth.loadMe()
  }
})

function logout() {
  auth.logout()
  void router.push('/login')
}
</script>

<template>
  <el-container class="app-shell">
    <el-header v-if="showHeader" class="app-header">
      <div class="brand" @click="router.push('/articles')">Learn Assistant</div>
      <nav class="nav">
        <router-link to="/articles">文章</router-link>
        <router-link to="/vocabs">生词本</router-link>
        <router-link to="/mistakes">错题本</router-link>
      </nav>
      <div class="spacer" />
      <span v-if="auth.user" class="username">{{ auth.user.username }}</span>
      <el-button v-if="auth.user" text size="small" @click="logout">退出</el-button>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>