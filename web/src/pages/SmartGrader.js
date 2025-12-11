import { ref, reactive, computed, onActivated, onMounted } from 'vue' // 1. 引入生命周期
import { useRouter } from 'vue-router' // 2. 引入路由
import { Message } from '@arco-design/web-vue'
import { 
  IconUpload, IconScan, IconPlayCircle, IconRobot, IconDelete, 
  IconInfoCircleFill, IconEye, IconFolderAdd, IconDown,
  IconCheckCircle, IconLoading, IconFileImage, IconRight, IconLeft, IconPlus,
  IconComputer, IconApps, IconArrowLeft,
  IconThumbUpFill, IconThumbDownFill, IconBulb,IconCode , IconCloseCircle
} from '@arco-design/web-vue/es/icon'

import { 
  UploadAssignmentAPI, 
  ocrRequestAPI, 
  deepseekOcrRequestAPI, 
  compileRequestAPI, 
  generateReportAPI,
  uploadAssignmentBatchAPI,
  ocrBatchRequestAPI ,
  
} from '../api/assignment.js'

// 不再需要引入 BatchUpload 组件了
// import BatchUpload from '../components/BatchUpload/BatchUpload.vue'

export default {
  components: {
    IconUpload, IconScan, IconPlayCircle, IconRobot, IconDelete, 
    IconInfoCircleFill, IconEye, IconApps, IconArrowLeft,
    IconPlus, IconCheckCircle, IconRight, IconLeft, IconFileImage,
    IconLoading, IconCode, IconComputer, IconDown, IconFolderAdd,
    IconThumbUpFill, IconBulb, IconThumbDownFill, IconCloseCircle
    // BatchUpload // 删除注册
  },
  setup() {
    const router = useRouter() // 获取路由

    // ==========================================
    // 1. 状态定义
    // ==========================================
    // const showBatchModal = ref(false) // 删除
    const isGlobalLoading = ref(false)
    const imagePreviewVisible = ref(false)
    
    const ocrLoading = ref(false)
    const compileLoading = ref(false)
    const aiLoading = ref(false)
    
    // const pendingBatchList = ref([]) // 删除（移到新页面了）
    
    const mode = ref('single') 
    const assignmentList = ref([])
    const currentAssignment = ref(null)
    const currentImageIndex = ref(0) 

    const code = ref('')            
    const compileInfo = ref(null)   
    const aiResult = ref(null)      
    const timings = ref({ total: null })
    const aiTimings = ref({ total: null })

    const ocrProgress = ref({ visible: false, percent: 0, status: 'normal' })
    const compileProgress = ref({ visible: false, percent: 0, status: 'normal' })
    const aiProgress = ref({ visible: false, percent: 0, status: 'normal' })
    
    const codeResultStep = reactive({
      ocrDone: false, compileDone: false, aiDone: false
    })

    const modals = reactive({ code: false, run: false, ai: false })
    const modalData = ref('')
    const currentAiResult = ref(null)
    const currentCompileInfo = ref(null)

    // ==========================================
    // 2. 路由与数据接收逻辑 (新增)
    // ==========================================
    
    // 打开批量页面 -> 路由跳转
    const openBatchMode = () => {
      router.push('/batch-upload')
    }

    // 检查是否有带回来的数据
    const checkBatchData = () => {
      const dataStr = sessionStorage.getItem('temp_batch_uploads')
      if (dataStr) {
        try {
          const newAssignments = JSON.parse(dataStr)
          
          const formattedItems = newAssignments.map(item => ({
            ...item,
            status: 'ready',
            isBatch: true,
            results: { code: '', compile: null, ai: null }
          }))
          
          assignmentList.value.push(...formattedItems)
          mode.value = 'list'
          currentAssignment.value = null
          Message.success(`已导入 ${formattedItems.length} 份新作业`)
        } catch (e) {
          console.error('Parse batch data failed', e)
        }
        // 清除数据，防止刷新页面重复添加
        sessionStorage.removeItem('temp_batch_uploads')
      }
    }

    // 使用 onActivated (如果是 KeepAlive) 或 onMounted 监听
    onMounted(() => {
      checkBatchData()
    })
    // 推荐加上 onActivated 以防使用了 KeepAlive
    onActivated(() => {
      checkBatchData()
    })
    // ==========================================
    // 2. 计算属性
    // ==========================================
    const displayImageUrl = computed(() => {
      if (currentAssignment.value) {
        const files = currentAssignment.value.localFiles || []
        if (files && files.length > 0 && files[currentImageIndex.value]) {
           return files[currentImageIndex.value].url
        }
      }
      return null
    })

    const hasAnyResults = computed(() => {
      return assignmentList.value.some(item => item.results && item.results.code)
    })

    const canOperateCurrent = computed(() => {
      return currentAssignment.value && currentAssignment.value.results && currentAssignment.value.results.code
    })

    // ==========================================
    // 3. 批量工作台逻辑
    // ==========================================
    const handleBatchUploadSuccess = (newAssignments) => {
      const formattedItems = newAssignments.map(item => ({
        ...item,
        status: 'ready',
        isBatch: true,
        results: { code: '', compile: null, ai: null }
      }))
      assignmentList.value.push(...formattedItems)
      mode.value = 'list'
      currentAssignment.value = null
      showBatchModal.value = false 
    }

    // ==========================================
    // 4. 主界面逻辑 (单图 & 列表)
    // ==========================================
    const customUploadRequest = async (option) => {
      const file = option.fileItem.file
      const localUrl = URL.createObjectURL(file)
      const formData = new FormData()
      formData.append('file', file) // 单图接口字段通常是 file

      isGlobalLoading.value = true
      try {
        const res = await UploadAssignmentAPI(formData) 
        if (res.code === 0) {
          addSingleItemToState(res.data.assignmentId, res.data.title, localUrl, 1)
          Message.success('上传成功')
        } else {
          throw new Error(res.message)
        }
      } catch (err) { 
        console.error(err)
        Message.warning('接口异常，使用本地预览')
        addSingleItemToState(Date.now(), '本地预览作业', localUrl, 1)
      } 
      finally { isGlobalLoading.value = false }
    }

    const addSingleItemToState = (id, title, url, count) => {
      const newItem = {
        assignmentId: id,
        title: title || `作业 ${id}`,
        localFiles: [{ url: url }],
        imageCount: count,
        status: 'ready',
        isBatch: false,
        results: { code: '', compile: null, ai: null }
      }
      assignmentList.value.push(newItem)
      selectAssignment(newItem)
    }

    const selectAssignment = (item) => {
      currentAssignment.value = item
      currentImageIndex.value = 0
      mode.value = 'single'
      syncDataToUI(item)
    }

    const syncDataToUI = (item) => {
      if(!item.results) item.results = { code: '', compile: null, ai: null }
      code.value = item.results.code || ''
      compileInfo.value = item.results.compile || null
      aiResult.value = item.results.ai || null
      codeResultStep.ocrDone = !!code.value
      codeResultStep.compileDone = !!compileInfo.value
      codeResultStep.aiDone = !!aiResult.value
      ocrProgress.value.visible = false
      compileProgress.value.visible = false
      aiProgress.value.visible = false
    }

    const handleDeleteCurrent = () => {
      if (!currentAssignment.value) return
      const idx = assignmentList.value.findIndex(i => i.assignmentId === currentAssignment.value.assignmentId)
      if (idx !== -1) assignmentList.value.splice(idx, 1)
      currentAssignment.value = null
      mode.value = assignmentList.value.length > 0 ? 'list' : 'single'
    }

    const prevImage = () => { if (currentImageIndex.value > 0) currentImageIndex.value-- }
    const nextImage = () => { if (currentAssignment.value && currentImageIndex.value < currentAssignment.value.imageCount - 1) currentImageIndex.value++ }

    // ==========================================
    // 5. 业务触发
    // ==========================================
    let progressInterval = null
    const startProgressAnim = (progressRef) => {
      progressRef.value.visible = true; progressRef.value.percent = 0; 
      if(progressInterval) clearInterval(progressInterval)
      progressInterval = setInterval(() => { 
        if(progressRef.value.percent < 90) progressRef.value.percent += Math.random() * 8
      }, 300)
    }
    const stopProgressAnim = (progressRef) => {
      if(progressInterval) clearInterval(progressInterval)
      progressRef.value.percent = 100
      setTimeout(() => progressRef.value.visible = false, 600)
    }

    const processTasks = async (taskName, apiCallStrategy, onSuccess) => {
      let targets = []
      if (mode.value === 'single' && currentAssignment.value) {
        targets = [currentAssignment.value]
      } else {
        targets = assignmentList.value
      }

      if (targets.length === 0) return

      isGlobalLoading.value = true
      Message.info(`开始${taskName}...`)

      for (const item of targets) {
        const isCurrentView = currentAssignment.value?.assignmentId === item.assignmentId
        item.status = 'loading' // 强制重置状态，修复重复点击不转圈的问题
        
        if (isCurrentView) {
           if (taskName === '识别') startProgressAnim(ocrProgress)
           if (taskName === '编译') startProgressAnim(compileProgress)
           if (taskName === 'AI批改') startProgressAnim(aiProgress)
        }
        item.status = 'loading'

        try {
          const res = await apiCallStrategy(item)
          if (res.code === 0) {
            onSuccess(item, res.data, isCurrentView)
            item.status = 'success'
          } else {
            throw new Error(res.message || 'API Error')
          }
        } catch (e) {
          console.warn(`${taskName} API Error`, e)
          item.status = 'error'
          if (isCurrentView) {
             ocrProgress.value.visible = false
             compileProgress.value.visible = false
             aiProgress.value.visible = false
          }
        }
      }
      isGlobalLoading.value = false
      Message.success(`${taskName}流程结束`)
    }

    const triggerIdentify = async (type = 'standard') => {
      await processTasks('识别', 
        (item) => {
          if (item.isBatch || item.imageCount > 1) {
             return ocrBatchRequestAPI(item.assignmentId, type)
          } else {
             if (type === 'deep') return deepseekOcrRequestAPI(item.assignmentId)
             else return ocrRequestAPI(item.assignmentId)
          }
        },
        (item, data, isView) => {
          const codeStr = data.fullRecognizedCode || data.recognizedCode
          item.results.code = codeStr
          if (isView) {
            code.value = codeStr
            codeResultStep.ocrDone = true
            stopProgressAnim(ocrProgress)
            timings.value.total = '2.5' 
          }
        }
      )
    }

    const triggerCompile = async () => {
      await processTasks('编译', 
        (item) => compileRequestAPI(item.assignmentId),
        (item, data, isView) => {
          item.results.compile = { ...data }
          if (isView) {
            compileInfo.value = data
            codeResultStep.compileDone = true
            stopProgressAnim(compileProgress)
          }
        }
      )
    }

    const triggerAi = async () => {
      await processTasks('AI批改',
        (item) => generateReportAPI(item.assignmentId),
        (item, data, isView) => {
          const resultData = {
            score: data.score,
            comment: data.reason, 
            breakdown: data.breakdown,
            suggestions: data.suggestions || [], 
            strengths: data.strengths || [],     
            weaknesses: data.weaknesses || []    
          }
          item.results.ai = resultData
          if (isView) {
            aiResult.value = resultData
            codeResultStep.aiDone = true
            stopProgressAnim(aiProgress)
          }
        }
      )
    }

    const showCodeModal = (str) => { modalData.value = str; modals.code = true }
    const showAiModal = (res) => { currentAiResult.value = res; modals.ai = true }
    const showCompileModal = (info) => { currentCompileInfo.value = info; modals.run = true }

    return {
       isGlobalLoading, imagePreviewVisible, mode,
       assignmentList, currentAssignment, currentImageIndex, displayImageUrl,
      hasAnyResults, canOperateCurrent,
      modals, modalData, currentAiResult, currentCompileInfo, 
      code, compileInfo, aiResult, timings, aiTimings, 
      ocrProgress, compileProgress, aiProgress, codeResultStep,
      ocrLoading, compileLoading, aiLoading,
      
      openBatchMode, 
      customUploadRequest, selectAssignment, handleDeleteCurrent, prevImage, nextImage,
      triggerIdentify, triggerCompile, triggerAi, 
      showCodeModal, showAiModal, showCompileModal
    }
  }
}