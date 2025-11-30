import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('../views/DashboardView.vue')
        },
        {
          path: 'users',
          name: 'Users',
          component: () => import('../views/UsersView.vue')
        },
        {
          path: 'dishes',
          name: 'Dishes',
          component: () => import('../views/DishesView.vue')
        },
        {
          path: 'logs',
          name: 'Logs',
          component: () => import('../views/LogsView.vue')
        }
      ]
    }
  ],
})

export default router
