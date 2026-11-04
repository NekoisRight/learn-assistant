<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const mode = ref<'login' | 'register'>('login')
const loading = ref(false)

const loginForm = reactive({ username: '', password: '' })
const registerForm = reactive({ username: '', email: '', password: '' })

async function afterLogin() {
  await auth.loadMe()
  ElMessage.success('登录成功')
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/articles'
  await router.replace(redirect)
}

async function submitLogin() {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await authApi.login(loginForm)
    auth.setToken(res.access_token)
    await afterLogin()
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    loading.value = false
  }
}

async function submitRegister() {
  if (registerForm.username.length < 3 || !registerForm.email || registerForm.password.length < 6) {
    ElMessage.warning('用户名至少 3 位，密码至少 6 位，邮箱需填写')
    return
  }
  loading.value = true
  try {
    await authApi.register(registerForm)
    const res = await authApi.login({
      username: registerForm.username,
      password: registerForm.password,
    })
    auth.setToken(res.access_token)
    await afterLogin()
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-hero">
      <h1>Learn Assistant</h1>
      <p>读一篇文章，进入一个场景，在真实对话中把英语用起来。</p>
      <ul>
        <li>AI 生成沉浸式角色扮演场景</li>
        <li>结束学习自动生成反馈报告</li>
        <li>生词与错题沉淀，随时复习</li>
      </ul>
    </div>

    <el-card class="login-card" shadow="always">
      <div class="login-tabs">
        <button
          class="tab-btn"
          :class="{ active: mode === 'login' }"
          @click="mode = 'login'"
        >
          登录
        </button>
        <button
          class="tab-btn"
          :class="{ active: mode === 'register' }"
          @click="mode = 'register'"
        >
          注册
        </button>
      </div>

      <el-form v-if="mode === 'login'" label-position="top" @submit.prevent="submitLogin">
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="loginForm.password"
            type="password"
            show-password
            placeholder="请输入密码"
            @keyup.enter="submitLogin"
          />
        </el-form-item>
        <el-button type="primary" class="submit-btn" :loading="loading" @click="submitLogin">
          登录
        </el-button>
      </el-form>

      <el-form v-else label-position="top" @submit.prevent="submitRegister">
        <el-form-item label="用户名">
          <el-input v-model="registerForm.username" placeholder="至少 3 位" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="registerForm.email" placeholder="you@example.com" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="registerForm.password"
            type="password"
            show-password
            placeholder="至少 6 位"
            @keyup.enter="submitRegister"
          />
        </el-form-item>
        <el-button type="primary" class="submit-btn" :loading="loading" @click="submitRegister">
          注册并登录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.login-page {
  min-height: calc(100vh - 64px);
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, 420px);
  gap: 48px;
  align-items: center;
  max-width: 1080px;
  margin: 0 auto;
  padding: 48px 24px;
}

.login-hero h1 {
  font-size: 48px;
  margin: 0 0 16px;
  color: #111827;
  letter-spacing: -1px;
}

.login-hero p {
  color: #4b5563;
  font-size: 18px;
  line-height: 1.7;
  max-width: 460px;
}

.login-hero ul {
  margin: 28px 0 0;
  padding-left: 20px;
  color: #6b7280;
  line-height: 2;
}

.login-card {
  border-radius: 16px;
}

.login-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  background: #f3f4f6;
  border-radius: 10px;
  padding: 4px;
}

.tab-btn {
  flex: 1;
  border: 0;
  background: transparent;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 15px;
  color: #6b7280;
}

.tab-btn.active {
  background: #fff;
  color: #111827;
  font-weight: 600;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.submit-btn {
  width: 100%;
  margin-top: 8px;
}

@media (max-width: 860px) {
  .login-page {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  .login-hero h1 {
    font-size: 36px;
  }
}
</style>