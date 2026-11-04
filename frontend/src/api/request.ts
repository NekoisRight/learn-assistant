import axios, { type AxiosRequestConfig } from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 120_000,
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const status = err.response?.status
    if (status === 401) {
      localStorage.removeItem('token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }

    const detail = err.response?.data?.detail
    let message: string = err.message
    if (typeof detail === 'string') {
      message = detail
    } else if (Array.isArray(detail)) {
      message = detail
        .map((item: { msg?: string }) => item.msg ?? '')
        .filter(Boolean)
        .join('；')
    }
    return Promise.reject(new Error(message))
  },
)

interface HttpClient {
  get<T>(url: string, config?: AxiosRequestConfig): Promise<T>
  post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
}

export const http = client as unknown as HttpClient