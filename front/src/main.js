import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'


// 设置axios默认值
axios.defaults.baseURL = 'http://10.83.216.164:5000/api'
axios.defaults.withCredentials = true

// 添加请求拦截器以便调试
axios.interceptors.request.use(config => {
  console.log('发送请求:', config.url, config);
  return config;
}, error => {
  console.error('请求错误:', error);
  return Promise.reject(error);
});

// 添加响应拦截器以便调试
axios.interceptors.response.use(response => {
  console.log('收到响应:', response.config.url, response);
  return response;
}, error => {
  console.error('响应错误:', error);
  return Promise.reject(error);
});

const app = createApp(App)
app.use(router)
app.use(store)
app.config.errorHandler = (err) => {
  console.error('Vue 错误:', err)
}
app.mount('#app')

