<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { reportApi } from '@/api/report'
import { sessionApi, type Message, type SessionDetail } from '@/api/session'

const route = useRoute()
const router = useRouter()
const sessionId = Number(route.params.sessionId)

const session = ref<SessionDetail | null>(null)
const messages = ref<Message[]>([])
const loading = ref(false)
const sending = ref(false)
const generating = ref(false)
const input = ref('')
const chatBox = ref<HTMLElement | null>(null)

async function scrollToBottom() {
  await nextTick()
  chatBox.value?.scrollTo({ top: chatBox.value.scrollHeight, behavior: 'smooth' })
}

async function load() {
  loading.value = true
  try {
    const [sessionRes, messageRes] = await Promise.all([
      sessionApi.detail(sessionId),
      sessionApi.messages(sessionId),
    ])
    session.value = sessionRes
    messages.value = messageRes
    await scrollToBottom()
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    loading.value = false
  }
}

async function send() {
  const content = input.value.trim()
  if (!content || sending.value || generating.value) return

  sending.value = true
  try {
    const res = await sessionApi.send(sessionId, content)
    messages.value.push(res.user_message, res.ai_message)
    input.value = ''
    await scrollToBottom()
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    sending.value = false
  }
}

async function finish() {
  if (generating.value) return
  generating.value = true
  ElMessage.info('正在生成学习报告，约需 10–20 秒…')
  try {
    await reportApi.generate(sessionId)
    try {
      await sessionApi.end(sessionId)
    } catch {
      // 会话状态失败不影响报告查看
    }
    ElMessage.success('报告已生成')
    await router.push(`/reports/${sessionId}`)
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    generating.value = false
  }
}

function formatTime(value: string) {
  return new Date(value).toLocaleTimeString()
}

onMounted(load)
</script>

<template>
  <div v-loading="loading" class="session-page">
    <div class="session-head">
      <div>
        <el-button text size="small" @click="router.push(`/articles/${session?.article_id ?? ''}`)">
          ← 返回文章
        </el-button>
        <h2>{{ session?.scene?.title ?? '对话练习' }}</h2>
        <p class="muted">{{ session?.scene?.goal }}</p>
      </div>
      <el-button type="success" :loading="generating" @click="finish">结束学习</el-button>
    </div>

    <div class="session-body">
      <el-card class="chat-card" shadow="never">
        <div ref="chatBox" class="chat-box">
          <el-empty
            v-if="messages.length === 0"
            description="发第一句话，开始角色扮演吧"
          />
          <div
            v-for="message in messages"
            :key="message.id"
            class="message-row"
            :class="message.role === 'user' ? 'from-user' : 'from-ai'"
          >
            <div class="avatar">{{ message.role === 'user' ? '我' : 'AI' }}</div>
            <div class="bubble-wrap">
              <div class="bubble">{{ message.content }}</div>
              <div class="time">{{ formatTime(message.created_at) }}</div>
            </div>
          </div>
        </div>

        <div class="composer">
          <el-input
            v-model="input"
            type="textarea"
            :rows="3"
            resize="none"
            placeholder="用英文回复（Enter 发送，Shift + Enter 换行）"
            :disabled="sending || generating"
            @keydown.enter.exact.prevent="send"
          />
          <el-button
            type="primary"
            class="send-btn"
            :loading="sending"
            :disabled="!input.trim() || generating"
            @click="send"
          >
            发送
          </el-button>
        </div>
      </el-card>

      <aside v-if="session?.scene" class="scene-side">
        <el-card shadow="never">
          <h4>你的身份</h4>
          <p>{{ session.scene.user_role }}</p>

          <h4>任务链</h4>
          <ol class="task-list">
            <li v-for="step in session.scene.task_chain" :key="step.stage">
              <strong>{{ step.stage }}</strong>
              <div>{{ step.task }}</div>
              <div class="muted">{{ step.user_action }}</div>
            </li>
          </ol>

          <h4>AI 角色</h4>
          <div v-for="role in session.scene.ai_roles" :key="role.name" class="role">
            <strong>{{ role.name }}</strong>
            <div class="muted">{{ role.stance }}</div>
          </div>
        </el-card>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.session-page {
  max-width: 1180px;
  margin: 0 auto;
}

.session-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.session-head h2 {
  margin: 4px 0 6px;
}

.session-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 16px;
  align-items: start;
}

.chat-card {
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 220px);
  min-height: 480px;
}

.chat-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0;
}

.chat-box {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #fafafa;
}

.message-row {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
}

.from-user {
  flex-direction: row-reverse;
}

.avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #e5e7eb;
  color: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  flex-shrink: 0;
}

.from-user .avatar {
  background: #2563eb;
  color: #fff;
}

.bubble-wrap {
  max-width: 72%;
}

.from-user .bubble-wrap {
  text-align: right;
}

.bubble {
  text-align: left;
  white-space: pre-wrap;
  line-height: 1.7;
  padding: 10px 14px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid #e5e7eb;
  color: #1f2937;
}

.from-user .bubble {
  background: #2563eb;
  border-color: #2563eb;
  color: #fff;
}

.time {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 4px;
}

.composer {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  background: #fff;
}

.send-btn {
  align-self: flex-end;
  height: 40px;
}

.scene-side h4 {
  margin: 16px 0 6px;
  color: #111827;
}

.scene-side h4:first-child {
  margin-top: 0;
}

.scene-side p {
  margin: 0;
  color: #4b5563;
  line-height: 1.6;
}

.task-list {
  padding-left: 18px;
  margin: 0;
  color: #374151;
  line-height: 1.6;
}

.task-list li {
  margin-bottom: 10px;
}

.role {
  margin-bottom: 10px;
  color: #374151;
}

@media (max-width: 900px) {
  .session-body {
    grid-template-columns: 1fr;
  }
  .scene-side {
    display: none;
  }
  .chat-card {
    height: calc(100vh - 240px);
  }
}
</style>