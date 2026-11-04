<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { articleApi, type ArticleBrief } from '@/api/article'

const router = useRouter()
const articles = ref<ArticleBrief[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const creating = ref(false)

const form = reactive({
  title: '',
  content: '',
  level: 'B1',
  source: 'user_upload',
})

async function loadArticles() {
  loading.value = true
  try {
    articles.value = await articleApi.list()
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    loading.value = false
  }
}

async function createArticle() {
  if (!form.title.trim() || form.content.trim().length < 20) {
    ElMessage.warning('请填写标题，正文至少 20 个字符')
    return
  }
  creating.value = true
  try {
    const article = await articleApi.create({
      title: form.title.trim(),
      content: form.content.trim(),
      level: form.level,
      source: form.source,
    })
    ElMessage.success('文章已创建')
    dialogVisible.value = false
    form.title = ''
    form.content = ''
    form.level = 'B1'
    await router.push(`/articles/${article.id}`)
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    creating.value = false
  }
}

function levelTag(level: string) {
  if (level === 'A2') return 'info'
  if (level === 'B2') return 'warning'
  if (level === 'C1') return 'danger'
  return 'success'
}

onMounted(loadArticles)
</script>

<template>
  <div class="page">
    <div class="page-head">
      <div>
        <h2>文章库</h2>
        <p class="muted">选择一篇文章，生成场景并开始沉浸式对话。</p>
      </div>
      <el-button type="primary" @click="dialogVisible = true">上传文章</el-button>
    </div>

    <div v-loading="loading">
      <el-empty v-if="!loading && articles.length === 0" description="还没有文章，先上传一篇吧">
        <el-button type="primary" @click="dialogVisible = true">上传文章</el-button>
      </el-empty>

      <div v-else class="article-grid">
        <el-card
          v-for="article in articles"
          :key="article.id"
          class="article-card"
          shadow="hover"
          @click="router.push(`/articles/${article.id}`)"
        >
          <div class="article-title">{{ article.title }}</div>
          <div class="article-meta">
            <el-tag size="small" :type="levelTag(article.level)">{{ article.level }}</el-tag>
            <span class="muted">{{ new Date(article.created_at).toLocaleString() }}</span>
          </div>
          <div class="article-link">进入文章 →</div>
        </el-card>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" title="上传文章" width="640px">
      <el-form label-position="top">
        <el-form-item label="标题">
          <el-input v-model="form.title" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="难度">
          <el-select v-model="form.level" style="width: 180px">
            <el-option label="A2 初级" value="A2" />
            <el-option label="B1 中级" value="B1" />
            <el-option label="B2 中高级" value="B2" />
            <el-option label="C1 高级" value="C1" />
          </el-select>
        </el-form-item>
        <el-form-item label="正文（英文）">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="10"
            placeholder="粘贴英文文章，至少 20 个字符"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="createArticle">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.article-card {
  cursor: pointer;
  border-radius: 12px;
  transition: transform 0.15s ease;
}

.article-card:hover {
  transform: translateY(-2px);
}

.article-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 14px;
  line-height: 1.5;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  gap: 8px;
}

.article-link {
  margin-top: 18px;
  color: #2563eb;
  font-size: 14px;
}
</style>