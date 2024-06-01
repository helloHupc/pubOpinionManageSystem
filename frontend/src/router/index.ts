import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'

const routes = [
    {
      path: '/',
      alias:'/home',
      name: 'Home',
      component: HomeView
    },
    {
     path: '/login',
     name: 'Login',
     component: LoginView,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue')
    }
  ]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 全局导航守卫
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token');
    console.log("token",token);
    console.log("to",to);
    if (!token) {
        if (to.name !== 'Login') {
          next({ name: 'Login' });
        } else {
          next();
        }
    } else {
        if (to.name === 'Login') {
          next({ name: 'Home' });
        } else {
          next();
        }
    }
});

export default router
