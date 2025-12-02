import { createRouter, createWebHashHistory } from 'vue-router'

// 路由懒加载
const SmartGrader = () => import('/src/pages/SmartGrader.vue')
const TaskManage = () => import('/src/pages/TaskManage.vue')

const routes = [
  { path: '/', redirect: '/grader' },
  { 
    path: '/grader', 
    name: 'SmartGrader', 
    component: SmartGrader,
    meta: { title: '文字识别' }
  },
  { 
    path: '/tasks', 
    name: 'TaskManage', 
    component: TaskManage,
    meta: { title: '任务管理' }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router