import { http } from './request'

export interface ArticleBrief {
  id: number
  title: string
  level: string
  source: string
  created_at: string
}

export interface Article extends ArticleBrief {
  content: string
}

export interface ArticleCreate {
  title: string
  content: string
  level: string
  source?: string
}

export const articleApi = {
  list: (page = 1, pageSize = 20) =>
    http.get<ArticleBrief[]>('/articles', { params: { page, page_size: pageSize } }),
  detail: (id: number) => http.get<Article>(`/articles/${id}`),
  create: (payload: ArticleCreate) => http.post<Article>('/articles', payload),
}