import { http } from './request'

export interface AIRole {
  name: string
  stance: string
  example: string
}

export interface TaskStep {
  stage: string
  task: string
  user_action: string
}

export interface Scene {
  id: number
  article_id: number
  title: string
  user_role: string
  goal: string
  ai_roles: AIRole[]
  conflict: string
  task_chain: TaskStep[]
  language_goals: string
  final_output: string
  difficulty: string
  created_at: string
}

export interface SceneGeneratePayload {
  article_id: number
  difficulty: string
  extra_instructions?: string
}

export const sceneApi = {
  list: (articleId: number) =>
    http.get<Scene[]>('/scenes', { params: { article_id: articleId, page_size: 100 } }),
  generate: (payload: SceneGeneratePayload) =>
    http.post<Scene>('/scenes/generate', payload),
}