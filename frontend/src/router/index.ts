import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/articles' },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/articles',
    name: 'articles',
    component: () => import('@/views/ArticlesView.vue'),
  },
  {
    path: '/articles/:id',
    name: 'article-detail',
    component: () => import('@/views/ArticleDetailView.vue'),
  },
  {
    path: '/sessions/:sessionId',
    name: 'session',
    component: () => import('@/views/SessionView.vue'),
  },
  {
    path: '/reports/:sessionId',
    name: 'report',
    component: () => import('@/views/ReportView.vue'),
  },
  {
    path: '/vocabs',
    name: 'vocabs',
    component: () => import('@/views/VocabListView.vue'),
  },
  {
    path: '/mistakes',
    name: 'mistakes',
    component: () => import('@/views/MistakeListView.vue'),
  },
  { path: '/:pathMatch(.*)*', redirect: '/articles' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (!to.meta.public && !token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.path === '/login' && token) {
    return { path: '/articles' }
  }
  return true
})

export default router