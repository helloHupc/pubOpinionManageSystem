import axios from 'axios';

// 从 meta 标签中获取 CSRF Token
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api', // 替换为你的后端 API 基础 URL
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json',
  },
});

if (csrfToken) {
  axiosInstance.defaults.headers.common['X-CSRFToken'] = csrfToken;
}

export default axiosInstance;
