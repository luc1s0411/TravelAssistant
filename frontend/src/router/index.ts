import { createRouter, createWebHistory } from 'vue-router'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'assistant', component: () => import('../views/AssistantView.vue') },
    { path: '/login', name: 'login', component: () => import('../views/LoginView.vue') },
    { path: '/catalog/:category(lodging|dining|attraction)', name: 'catalog', component: () => import('../views/CatalogView.vue') },
    { path: '/confirm', name: 'confirm', component: () => import('../views/ConfirmView.vue') },
    { path: '/plans', name: 'plans', component: () => import('../views/PlansView.vue') },
    { path: '/plans/:planId', name: 'plan-detail', component: () => import('../views/PlanDetailView.vue') },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('../views/NotFoundView.vue') },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
