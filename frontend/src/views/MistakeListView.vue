<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { reportApi, type Mistake } from '@/api/report'

const mistakes = ref<Mistake[]>([])
const loading = ref(false)

async function loadMistakes() {
  loading.value = true
  try {
    mistakes.value = await reportApi.listMistakes(1, 100)
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    loading.value = false
  }
}

onMounted(loadMistakes)
</script>

<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h2>错题本</h2>
        <p class="muted">历次对话中的语法与表达错误，按时间倒序排列。</p>
      </div>
    </div>

    <el-card v-loading="loading" shadow="never" class="table-card">
      <el-empty v-if="!loading && mistakes.length === 0" description="暂无错题，继续保持" />
      <el-table v-else :data="mistakes" style="width: 100%">
        <el-table-column prop="original" label="原句" min-width="220">
          <template #default="{ row }">
            <span class="original">{{ row.original }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="corrected" label="修正后" min-width="220">
          <template #default="{ row }">
            <span class="corrected">{{ row.corrected }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="说明" min-width="260" />
        <el-table-column prop="category" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small" type="warning">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="170">
          <template #default="{ row }">
            <span class="muted">{{ new Date(row.created_at).toLocaleString() }}</span>
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

.original {
  color: #dc2626;
}

.corrected {
  color: #16a34a;
}
</style>