import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import DatasetDetail from '../views/DatasetDetail.vue'
import DataAnalysis from '../views/DataAnalysis.vue'
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { guest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dataset/:id',
    name: 'DatasetDetail',
    component: DatasetDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/analysis/:id',
    name: 'DataAnalysis',
    component: DataAnalysis,
    meta: { requiresAuth: true },
    beforeEnter: async (to, from, next) => {
      try {
        // 在进入分析页面前先加载数据集
        const datasetId = Number(to.params.id);
        if (!store.getters.currentDataset || store.getters.currentDataset.id !== datasetId) {
          await store.dispatch('fetchDataset', datasetId);
        }
        next();
      } catch (error) {
        console.error('加载数据集失败，无法进入分析页面:', error);
        next('/dashboard');
      }
    }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 导航守卫
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 需要认证的路由
    if (!store.getters.isAuthenticated) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
    } else {
      next()
    }
  } else if (to.matched.some(record => record.meta.guest)) {
    // 仅限游客的路由
    if (store.getters.isAuthenticated) {
      next({ name: 'Dashboard' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router 