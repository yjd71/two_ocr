// src/main.js
import { createApp } from 'vue'
import App from './App.vue'

// 1. 引入路由 
import router from './router' 

// 2. 引入 Arco Design
import ArcoVue from '@arco-design/web-vue';
import '@arco-design/web-vue/dist/arco.css';

// import ElementPlus from 'element-plus'
// import 'element-plus/dist/index.css'

const app = createApp(App)

// 4. 关键步骤：安装插件
app.use(router)   // 
app.use(ArcoVue)  // 

// app.use(ElementPlus) // 如果还需要可以用

app.mount('#app')