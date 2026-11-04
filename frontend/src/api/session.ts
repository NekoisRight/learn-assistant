import { http } from './request'
import type { Scene } from './scene'

export interface Session {
  id: number
  user_id: number
  article_id: number
  scene_id: number
  status: string
  created_at: string
  updated_at: string
}

export interface SessionDetail extends Session {
  scene: Scene | null
}

export interface Message {
  id: number
  session_id: number
  role: string
  content: string
  created_at: string
}

export interface SendMessageResponse {
  user_message: Message
  ai_message: Message
}

export const sessionApi = {
  create: (payload: { article_id: number; scene_id: number }) =>
    http.post<Session>('/sessions', payload),
  detail: (id: number) => http.get<SessionDetail>(`/sessions/${id}`),
  messages: (id: number) => http.get<Message[]>(`/sessions/${id}/messages`),
  send: (id: number, content: string) =>
    http.post<SendMessageResponse>(`/sessions/${id}/messages`, { content }),
  end: (id: number) => http.patch<Session>(`/sessions/${id}/end`),
}