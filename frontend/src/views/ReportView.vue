<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { reportApi, type Report } from '@/api/report'

const route = useRoute()
const router = useRouter()
const sessionId = Number(route.params.sessionId)

const report = ref<Report | null>(null)
const loading = ref(false)
const generating = ref(false)

async function loadReport() {
  loading.value = true
  try {
    report.value = await reportApi.detail(sessionId)
  } catch {
    report.value = null
  } finally {
    loading.value = false
  }
}

async function generateReport() {
  generating.value = true
  try {
    report.value = await reportApi.generate(sessionId)
    ElMessage.success('报告已生成')
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    generating.value = false
  }
}

function goVocabs() {
  router.push('/vocabs')
}

function goMistakes() {
  router.push('/mistakes')
}

function backToChat() {
  router.push(`/sessions/${sessionId}`)
}

onMounted(loadReport)
</script>

<template>
  <div v-loading="loading" class="page report-page">
    <div class="report-head">
      <div>
        <el-button text size="small" @click="backToChat">← 返回对话</el-button>
        <h2>学习报告</h2>
        <p class="muted">基于本次场景对话自动生成，重点看语法、词汇、表达与任务完成度。</p>
      </div>
      <div class="head-actions">
        <el-button @click="goVocabs">生词本</el-button>
        <el-button @click="goMistakes">错题本</el-button>
        <el-button @click="backToChat">返回对话</el-button>
      </div>
    </div>

    <el-empty v-if="!loading && !report" description="还没有生成报告">
      <el-button type="primary" :loading="generating" @click="generateReport">
        立即生成报告
      </el-button>
    </el-empty>

    <template v-if="report">
      <el-card class="score-card" shadow="never">
        <el-row :gutter="24" align="middle">
          <el-col :span="8">
            <div class="score">{{ report.overall_score }}</div>
            <div class="score-label">综合评分</div>
          </el-col>
          <el-col :span="16">
            <div class="task-line">
              <span class="task-title">任务完成度</span>
              <el-tag :type="report.task_completion.goal_achieved ? 'success' : 'warning'">
                {{ report.task_completion.goal_achieved ? '已达成' : '未达成' }}
              </el-tag>
              <span class="task-score">得分：{{ report.task_completion.score }}</span>
            </div>
            <p class="task-comment">{{ report.task_completion.comment }}</p>
            <el-divider />
            <p class="summary">{{ report.summary }}</p>
          </el-col>
        </el-row>
        <div class="created-at">生成时间：{{ new Date(report.created_at).toLocaleString() }}</div>
      </el-card>

      <el-card class="section-card" shadow="never">
        <h3>语法问题</h3>
        <el-empty
          v-if="report.grammar_issues.length === 0"
          description="没有明显语法问题，很棒！"
        />
        <div
          v-for="(item, index) in report.grammar_issues"
          :key="index"
          class="report-item"
        >
          <div class="original">✕ {{ item.original }}</div>
          <div class="corrected">✓ {{ item.corrected }}</div>
          <div class="reason">{{ item.reason }}</div>
        </div>
      </el-card>

      <el-card class="section-card" shadow="never">
        <h3>词汇建议</h3>
        <el-empty
          v-if="report.vocab_suggestions.length === 0"
          description="本次没有新增生词"
        />
        <div
          v-for="(item, index) in report.vocab_suggestions"
          :key="index"
          class="report-item"
        >
          <div><strong class="word">{{ item.word }}</strong> — {{ item.meaning }}</div>
          <div class="reason">{{ item.example }}</div>
        </div>
      </el-card>

      <el-card class="section-card" shadow="never">
        <h3>表达升级</h3>
        <el-empty
          v-if="report.expression_upgrades.length === 0"
          description="表达已经很地道！"
        />
        <div
          v-for="(item, index) in report.expression_upgrades"
          :key="index"
          class="report-item"
        >
          <div class="original">{{ item.original }}</div>
          <div class="corrected">→ {{ item.upgraded }}</div>
          <div class="reason">{{ item.reason }}</div>
        </div>
      </el-card>
    </template>
  </div>
</template>

<style scoped>
.report-page {
  max-width: 920px;
  margin: 0 auto;
}

.report-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.report-head h2 {
  margin: 4px 0 6px;
}

.head-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.score-card {
  border-radius: 12px;
}

.score {
  font-size: 64px;
  font-weight: 700;
  color: #409eff;
  text-align: center;
  line-height: 1;
}

.score-label {
  text-align: center;
  color: #6b7280;
  margin-top: 8px;
}

.task-line {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.task-score {
  color: #6b7280;
}

.task-comment {
  color: #4b5563;
  margin: 10px 0 0;
  line-height: 1.7;
}

.summary {
  color: #374151;
  line-height: 1.8;
  margin: 0;
}

.created-at {
  margin-top: 16px;
  font-size: 12px;
  color: #9ca3af;
  text-align: right;
}

.section-card {
  margin-top: 16px;
  border-radius: 12px;
}

.section-card h3 {
  margin: 0 0 12px;
  color: #111827;
}

.report-item {
  padding: 12px 0;
  border-bottom: 1px dashed #e5e7eb;
  line-height: 1.6;
}

.report-item:last-child {
  border-bottom: 0;
}

.original {
  color: #dc2626;
}

.corrected {
  color: #16a34a;
  margin-top: 4px;
}

.reason {
  color: #6b7280;
  font-size: 13px;
  margin-top: 4px;
}

.word {
  color: #111827;
}

@media (max-width: 720px) {
  .report-head {
    flex-direction: column;
  }
}
</style>