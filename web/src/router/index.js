import { createRouter, createWebHashHistory } from 'vue-router'

// 路由懒加载
const SmartGrader = () => import('/src/pages/SmartGrader.vue')
const TaskManage = () => import('/src/pages/TaskManage.vue')
// 1. 引入 BatchUpload 组件 (注意路径要对)
const BatchUpload = () => import('/src/components/BatchUpload/BatchUpload.vue')

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
  },
  // 2. 新增批量上传路由
  {
    path: '/batch-upload',
    name: 'BatchUpload',
    component: BatchUpload,
    meta: { title: '批量上传' }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router