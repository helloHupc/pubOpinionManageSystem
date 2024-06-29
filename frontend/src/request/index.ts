import axios from 'axios'
import { ElMessage } from 'element-plus'

//创建axios实例
const service = axios.create({
    baseURL: 'http://localhost:8000/api', // 替换为你的后端 API 基础 URL
    timeout: 5000,
    headers: {'Content-Type': 'application/json;charset=utf-8'}
});
//请求拦截
service.interceptors.request.use((config)=>{
    config.headers = config.headers || {}
    if(localStorage.getItem('token')){
        config.headers.token = localStorage.getItem('token') || ''
    }
    return config
})
//响应拦截
service.interceptors.response.use((res)=>{
    console.log('interceptors res data',res.data)
    const code:number = res.data.code
    if(code != 200 && code != 0){
        ElMessage({
            message: res.data.message,
            grouping: false,
            type: 'error',
            duration: 2000
          })
        return Promise.reject(res.data)
    }
    return res.data
},(error)=>{
    ElMessage({
        message: '接口异常',
        grouping: false,
        type: 'error',
        duration: 2000
      })
    console.log('error',error)
})
export default service