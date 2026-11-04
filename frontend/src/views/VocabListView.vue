<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { reportApi, type Vocab } from '@/api/report'

const vocabs = ref<Vocab[]>([])
const loading = ref(false)
const reviewingId = ref<number | null>(null)
const filter = ref<'all' | 'unmastered' | 'mastered'>('all')

async function loadVocabs() {
  loading.value = true
  try {
    const mastered = filter.value === 'all' ? undefined : filter.value === 'mastered' ? 1 : 0
    vocabs.value = await reportApi.listVocabs(1, 100, mastered)
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    loading.value = false
  }
}

async function handleReview(vocab: Vocab, mastered: boolean) {
  reviewingId.value = vocab.id
  try {
    const res = await reportApi.reviewVocab(vocab.id, mastered)
    Object.assign(vocab, res)
    ElMessage.success(mastered ? '已标记为掌握' : '已复习一次')
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    reviewingId.value = null
  }
}

function changeFilter(value: string | number | boolean | undefined) {
  filter.value = value as typeof filter.value
  void loadVocabs()
}

onMounted(loadVocabs)
</script>

<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h2>生词本</h2>
        <p class="muted">来自历次学习报告的生词，复习会累计次数。</p>
      </div>
      <el-radio-group :model-value="filter" @change="changeFilter">
        <el-radio-button value="all">全部</el-radio-button>
        <el-radio-button value="unmastered">未掌握</el-radio-button>
        <el-radio-button value="mastered">已掌握</el-radio-button>
      </el-radio-group>
    </div>

    <el-card v-loading="loading" shadow="never" class="table-card">
      <el-empty v-if="!loading && vocabs.length === 0" description="暂无生词，完成一次学习后会自动沉淀" />
      <el-table v-else :data="vocabs" style="width: 100%">
        <el-table-column prop="word" label="单词" width="180">
          <template #default="{ row }">
            <strong>{{ row.word }}</strong>
          </template>
        </el-table-column>
        <el-table-column prop="meaning" label="释义" min-width="180" />
        <el-table-column prop="example" label="例句" min-width="260" />
        <el-table-column prop="review_count" label="复习次数" width="100" align="center" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.mastered ? 'success' : 'info'">
              {{ row.mastered ? '已掌握' : '未掌握' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button
              size="small"
              :loading="reviewingId === row.id"
              @click="handleReview(row, false)"
            >
              复习
            </el-button>
            <el-button
              size="small"
              type="primary"
              :disabled="row.mastered === 1"
              :loading="reviewingId === row.id"
              @click="handleReview(row, true)"
            >
              掌握
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.table-card {
  border-radius: 12px;
}
</style>