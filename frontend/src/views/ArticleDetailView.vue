<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { articleApi, type Article } from '@/api/article'
import { sceneApi, type Scene } from '@/api/scene'
import { sessionApi } from '@/api/session'

const route = useRoute()
const router = useRouter()
const articleId = Number(route.params.id)

const article = ref<Article | null>(null)
const scenes = ref<Scene[]>([])
const loading = ref(false)
const generating = ref(false)
const startingId = ref<number | null>(null)
const dialogVisible = ref(false)
const form = reactive({ difficulty: 'standard', extra_instructions: '' })

async function load() {
  loading.value = true
  try {
    const [articleRes, sceneRes] = await Promise.all([
      articleApi.detail(articleId),
      sceneApi.list(articleId),
    ])
    article.value = articleRes
    scenes.value = sceneRes
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    loading.value = false
  }
}

async function generateScene() {
  generating.value = true
  try {
    const scene = await sceneApi.generate({
      article_id: articleId,
      difficulty: form.difficulty,
      extra_instructions: form.extra_instructions || undefined,
    })
    scenes.value = [scene, ...scenes.value]
    dialogVisible.value = false
    form.extra_instructions = ''
    ElMessage.success('场景生成成功')
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    generating.value = false
  }
}

async function startScene(scene: Scene) {
  startingId.value = scene.id
  try {
    const session = await sessionApi.create({
      article_id: articleId,
      scene_id: scene.id,
    })
    await router.push(`/sessions/${session.id}`)
  } catch (err) {
    ElMessage.error((err as Error).message)
  } finally {
    startingId.value = null
  }
}

function difficultyText(difficulty: string) {
  if (difficulty === 'easy') return '简单'
  if (difficulty === 'hard') return '困难'
  return '标准'
}

onMounted(load)
</script>

<template>
  <div v-loading="loading" class="page">
    <el-button text class="back-btn" @click="router.push('/articles')">← 返回文章库</el-button>

    <template v-if="article">
      <el-card class="article-panel">
        <div class="article-head">
          <h2>{{ article.title }}</h2>
          <el-tag>{{ article.level }}</el-tag>
        </div>
        <div class="article-body">{{ article.content }}</div>
      </el-card>

      <div class="page-head scene-head">
        <div>
          <h3>练习场景</h3>
          <p class="muted">AI 会基于文章生成角色扮演场景，选一个开始对话。</p>
        </div>
        <el-button type="primary" plain @click="dialogVisible = true">生成新场景</el-button>
      </div>

      <el-empty v-if="scenes.length === 0" description="还没有场景，生成一个开始练习" />

      <div v-else class="scene-list">
        <el-card v-for="scene in scenes" :key="scene.id" class="scene-card">
          <div class="scene-top">
            <div>
              <h4>{{ scene.title }}</h4>
              <el-tag size="small" type="info">{{ difficultyText(scene.difficulty) }}</el-tag>
            </div>
            <el-button
              type="primary"
              :loading="startingId === scene.id"
              @click="startScene(scene)"
            >
              开始对话
            </el-button>
          </div>

          <p class="scene-goal"><strong>核心目标：</strong>{{ scene.goal }}</p>
          <p class="scene-goal"><strong>你的身份：</strong>{{ scene.user_role }}</p>
          <p class="scene-goal"><strong>冲突：</strong>{{ scene.conflict }}</p>

          <el-collapse>
            <el-collapse-item title="查看 AI 角色与任务链">
              <div class="sub-title">AI 角色</div>
              <div v-for="role in scene.ai_roles" :key="role.name" class="scene-item">
                <strong>{{ role.name }}</strong>（{{ role.stance }}）
                <div class="muted">{{ role.example }}</div>
              </div>
              <div class="sub-title">任务链</div>
              <div v-for="step in scene.task_chain" :key="step.stage" class="scene-item">
                <strong>{{ step.stage }}：</strong>{{ step.task }}
                <div class="muted">你需要：{{ step.user_action }}</div>
              </div>
              <div class="sub-title">语言目标</div>
              <div class="scene-item">{{ scene.language_goals }}</div>
              <div class="sub-title">最终产出</div>
              <div class="scene-item">{{ scene.final_output }}</div>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </div>
    </template>

    <el-dialog v-model="dialogVisible" title="生成练习场景" width="520px">
      <el-form label-position="top">
        <el-form-item label="场景难度">
          <el-select v-model="form.difficulty" style="width: 180px">
            <el-option label="简单" value="easy" />
            <el-option label="标准" value="standard" />
            <el-option label="困难" value="hard" />
          </el-select>
        </el-form-item>
        <el-form-item label="额外要求（可选）">
          <el-input
            v-model="form.extra_instructions"
            type="textarea"
            :rows="3"
            placeholder="例如：场景发生在校园，冲突更温和一些"
          />
        </el-form-item>
        <p class="muted">生成需要约 10–20 秒，请稍候。</p>
      </el-form>
      <template #footer>
        <el-button :disabled="generating" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="generating" @click="generateScene">生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.back-btn {
  margin-bottom: 12px;
}

.article-panel {
  border-radius: 12px;
}

.article-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.article-head h2 {
  margin: 0;
}

.article-body {
  white-space: pre-wrap;
  line-height: 1.9;
  color: #374151;
  max-height: 360px;
  overflow: auto;
}

.scene-head {
  margin-top: 28px;
}

.scene-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.scene-card {
  border-radius: 12px;
}

.scene-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.scene-top h4 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #111827;
}

.scene-goal {
  color: #374151;
  line-height: 1.7;
  margin: 8px 0;
}

.sub-title {
  font-weight: 600;
  margin: 14px 0 8px;
  color: #111827;
}

.scene-item {
  margin-bottom: 10px;
  color: #374151;
  line-height: 1.6;
}
</style>