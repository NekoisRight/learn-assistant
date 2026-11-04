import { http } from './request'

export interface GrammarIssue { original: string; corrected: string; reason: string }
export interface VocabSuggestion { word: string; meaning: string; example: string }
export interface ExpressionUpgrade { original: string; upgraded: string; reason: string }
export interface TaskCompletion { goal_achieved: boolean; score: number; comment: string }

export interface Report {
  id: number
  session_id: number
  user_id: number
  grammar_issues: GrammarIssue[]
  vocab_suggestions: VocabSuggestion[]
  expression_upgrades: ExpressionUpgrade[]
  task_completion: TaskCompletion
  overall_score: number
  summary: string
  created_at: string
}

export interface Vocab {
  id: number
  word: string
  meaning: string
  example: string
  review_count: number
  mastered: number
  created_at: string
}

export interface Mistake {
  id: number
  original: string
  corrected: string
  reason: string
  category: string
  created_at: string
}

export const reportApi = {
  generate: (sessionId: number) =>
    http.post<Report>('/reports/generate', null, { params: { session_id: sessionId } }),
  detail: (sessionId: number) => http.get<Report>(`/reports/${sessionId}`),
  listVocabs: (page = 1, pageSize = 100, mastered?: number) =>
    http.get<Vocab[]>('/vocabs', {
      params: { page, page_size: pageSize, mastered },
    }),
  reviewVocab: (vocabId: number, mastered: boolean) =>
    http.post<Vocab>(`/vocabs/${vocabId}/review`, null, { params: { mastered } }),
  listMistakes: (page = 1, pageSize = 100) =>
    http.get<Mistake[]>('/mistakes', { params: { page, page_size: pageSize } }),
}