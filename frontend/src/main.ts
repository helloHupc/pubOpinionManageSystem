import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import axiosInstance from './axiosConfig'
import axios from 'axios';

const app = createApp(App)

// 将 axios 实例添加到全局属性中
app.config.globalProperties.$axios = axiosInstance;

// 从 meta 标签中获取 CSRF Token
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

// 设置 Axios 默认请求头
if (csrfToken) {
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
}

app.use(createPinia())
app.use(router)

app.mount('#app')
