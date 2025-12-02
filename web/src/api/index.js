import axios from 'axios'
import { Message } from '@arco-design/web-vue'

// 创建 axios 实例
const service = axios.create({
  baseURL: '/api', 
  timeout: 60000,
  // 参数序列化配置，确保数组参数格式为 likes=a&likes=b (不带 [])
  paramsSerializer: {
    indexes: null 
  }
})

// request 拦截器
service.interceptors.request.use(
  config => {
    // 如果以后有 token，可以在这里加：
    // config.headers['Authorization'] = 'Bearer ' + token
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// response 拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // 这里我们只剥离 HTTP 层，把业务数据返回去
    // 如果后端的 code 不是 0，你也可以在这里统一拦截报错，
    // 但为了灵活性，我们暂时只返回 res，在组件里处理 code
    return res
  },
  error => {
    console.log('err' + error)
    Message.error(error.message || '请求服务异常')
    return Promise.reject(error)
  }
)

export default service