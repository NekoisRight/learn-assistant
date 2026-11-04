import { http } from './request'

export interface User {
  id: number
  username: string
  email: string
  created_at: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface RegisterPayload {
  username: string
  email: string
  password: string
}

export const authApi = {
  register: (payload: RegisterPayload) =>
    http.post<User>('/auth/register', payload),
  login: (payload: { username: string; password: string }) =>
    http.post<Token>('/auth/login', payload),
  me: () => http.get<User>('/users/me'),
}