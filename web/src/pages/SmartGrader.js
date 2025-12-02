import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'
import { 
  IconUpload, 
  IconScan, 
  IconPlayCircle, 
  IconRobot,
  IconDelete,
  IconInfoCircleFill,
  IconEye
} from '@arco-design/web-vue/es/icon'

import { 
  UploadAssignmentAPI, 
  ocrRequestAPI, 
  deepseekOcrRequestAPI,
  compileRequestAPI, 
  generateReportAPI 
} from '../api/assignment.js'

export default {
  components: {
    IconUpload, IconScan, IconPlayCircle, IconRobot, IconDelete,IconInfoCircleFill,IconEye
  },
  setup() {
    // ---------- 核心状态 ----------
    const imagePreviewVisible = ref(false)
    const uploadLoading = ref(false) 
    const ocrLoading = ref(false)    // 专门控制识别按钮的 loading
    const compileLoading = ref(false) // 专门控制编译按钮
    const aiLoading = ref(false)      // 专门控制 AI 按钮
    const assignmentId_globle = ref(null)
    const imageUrl = ref(null)      // 原始上传图片预览
    const code = ref('')            // 识别出的代码
    const codeResult = ref('')      // 编译运行结果字符串
    
    // ---------- 结果对象 ----------
    const compileInfo = ref(null)   // 编译详情对象
    const aiResult = ref(null)      // AI 报告对象

    // ---------- 图片路径  ----------
    const processedImageUrl = ref(null)   
    const ocrResultImageUrl = ref(null)
    const processedImagePath = ref(null)
    const resImagePath = ref(null)

    // ---------- 计时与进度 ----------
    const timings = ref({ total: null })   // OCR 总耗时
    const aiTimings = ref({ total: null }) // AI 总耗时

    // OCR 进度对象
    const ocrProgress = ref({
      visible: false,
      percent: 0,
      status: 'normal',
      steps: [
        { percent: 0, time: null },
        { percent: 0, time: null }
      ]
    })
    let progressInterval = null
// 编译进度 (Compile Progress)
    const compileProgress = ref({
      visible: false, percent: 0, status: 'normal'
    })
    let compileProgressInterval = null
    // AI 进度对象
    const aiProgress = ref({
      visible: false,
      percent: 0,
      status: 'normal',
      steps: [
        { name: '代码特征分析', percent: 0, time: null },
        { name: '评分报告生成', percent: 0, time: null }
      ]
    })
    let aiProgressInterval = null

    // ---------- UI 流程控制 ----------
    const codeResultStep = reactive({
      ocrDone: false,
      compileDone: false,
      aiDone: false
    })

    const modals = reactive({
      code: false,
      run: false,
      ai: false
    })

    // =========================================================
    // 1. 进度条动画
    // =========================================================

    // --- OCR 动画 ---
    const startOcrAnimation = () => {
      ocrProgress.value.visible = true
      ocrProgress.value.status = 'normal'
      ocrProgress.value.percent = 0
      ocrProgress.value.steps[0].percent = 0
      ocrProgress.value.steps[1].percent = 0
      timings.value.total = null

      if (progressInterval) clearInterval(progressInterval)
      let p0 = 0, p1 = 0
      
      progressInterval = setInterval(() => {
        // 模拟随机增长
        if (p0 < 60 && Math.random() < 0.7) {
          p0 += 1 + Math.random() * 3
        } else {
          p1 += 0.5 + Math.random() * 3
        }
        p0 = Math.min(p0, 95); p1 = Math.min(p1, 95)
        
        ocrProgress.value.percent = Math.round(Math.min(99, p0 + p1 * 0.9))
        ocrProgress.value.steps[0].percent = Math.round(p0)
        ocrProgress.value.steps[1].percent = Math.round(p1)
      }, 200)
    }
// 编译动画
    const startCompileAnimation = () => {
      compileProgress.value.visible = true; compileProgress.value.status = 'normal'; compileProgress.value.percent = 0
      if (compileProgressInterval) clearInterval(compileProgressInterval)
      let p = 0
      compileProgressInterval = setInterval(() => {
        if (p < 95) p += Math.random() * 8 // 编译通常快一点
        compileProgress.value.percent = Math.round(p)
      }, 150)
    }
    const stopCompileAnimation = () => {
      if (compileProgressInterval) clearInterval(compileProgressInterval)
      compileProgress.value.percent = 100
      compileProgress.value.status = 'success'
      setTimeout(() => { compileProgress.value.visible = false }, 800)
    }
    const stopOcrAnimation = (elapsedMs) => {
      if (progressInterval) clearInterval(progressInterval)
      const totalSec = elapsedMs / 1000
      timings.value.total = totalSec.toFixed(2)

      // 进度时间分配算法
      const p0 = Math.max(ocrProgress.value.steps[0].percent, 0)
      const p1 = Math.max(ocrProgress.value.steps[1].percent, 0)
      const sum = p0 + p1
      const t0 = sum <= 0 ? totalSec/2 : totalSec * (p0/sum)
      const t1 = sum <= 0 ? totalSec/2 : totalSec * (p1/sum)

      ocrProgress.value.steps[0].time = t0.toFixed(2)
      ocrProgress.value.steps[1].time = t1.toFixed(2)
      
      // 拉满进度
      ocrProgress.value.percent = 100
      ocrProgress.value.steps[0].percent = 100
      ocrProgress.value.steps[1].percent = 100
      ocrProgress.value.status = 'success'
      
      // 延迟消失
      setTimeout(() => { ocrProgress.value.visible = false }, 800)
    }

    // --- AI 动画 ---
    const startAiAnimation = () => {
      aiProgress.value.visible = true
      aiProgress.value.status = 'normal'
      aiProgress.value.percent = 0
      aiProgress.value.steps[0].percent = 0
      aiProgress.value.steps[1].percent = 0
      aiTimings.value.total = null

      if (aiProgressInterval) clearInterval(aiProgressInterval)
      let p0 = 0, p1 = 0
      
      aiProgressInterval = setInterval(() => {
        if (p0 < 60 && Math.random() < 0.7) p0 += 1 + Math.random() * 3
        else p1 += 0.5 + Math.random() * 3
        
        p0 = Math.min(p0, 95); p1 = Math.min(p1, 95)
        aiProgress.value.percent = Math.round(Math.min(99, p0 + p1 * 0.9))
        aiProgress.value.steps[0].percent = Math.round(p0)
        aiProgress.value.steps[1].percent = Math.round(p1)
      }, 200)
    }

    const stopAiAnimation = (elapsedMs) => {
      if (aiProgressInterval) clearInterval(aiProgressInterval)
      const totalSec = elapsedMs / 1000
      aiTimings.value.total = totalSec.toFixed(2)
      
      const p0 = aiProgress.value.steps[0].percent
      const p1 = aiProgress.value.steps[1].percent
      const sum = p0 + p1
      const t0 = sum <= 0 ? totalSec/2 : totalSec * (p0/sum)
      const t1 = sum <= 0 ? totalSec/2 : totalSec * (p1/sum)
      
      aiProgress.value.steps[0].time = t0.toFixed(2)
      aiProgress.value.steps[1].time = t1.toFixed(2)
      
      aiProgress.value.percent = 100
      aiProgress.value.steps[0].percent = 100
      aiProgress.value.steps[1].percent = 100
      aiProgress.value.status = 'success'
      
      setTimeout(() => { aiProgress.value.visible = false }, 800)
    }

    // =========================================================
    // 2. 业务 API 调用
    // =========================================================

    // --- 上传 ---
    const customUploadRequest = async (option) => {
      const { fileItem } = option
      const file = fileItem.file
      const formData = new FormData()
      formData.append('file', file)

      const reader = new FileReader()
      reader.onload = (e) => { imageUrl.value = e.target.result }
      reader.readAsDataURL(file)

      try {
        uploadLoading.value = true
        const res = await UploadAssignmentAPI(formData)
        // mock请求
        // await new Promise(resolve => setTimeout(resolve, 1000))
        // const res = { code: 0, data: { assignmentId: 'mock-id-001', fileName: file.name } }
        if (res.code === 0) {
          assignmentId_globle.value = res.data.assignmentId
          handleReset() // 重置状态
          uploadLoading.value = false // 显式关闭
          Message.success('上传成功，请点击“开始识别”')
        } else {
          Message.error('上传失败: ' + (res.message || '未知错误'))
        }
      } catch (err) {
        Message.error('上传请求异常')
      }
      // finally {
      //   loading.value = false
      // }
    }
// --- OCR 逻辑 (修改版：支持两种模式) ---
    //  type 参数：'standard' (默认) 或 'deep'
    const triggerOCR = async (type = 'standard') => {
      if (!assignmentId_globle.value) return
      ocrLoading.value = true
      
      startOcrAnimation() 
      const startTime = performance.now()

      try {
        let res
        //  根据类型选择调用的接口
        if (type === 'deep') {
          Message.info('正在调用 DeepSeek 进行深度识别...')
          res = await deepseekOcrRequestAPI(assignmentId_globle.value)
        } else {
          // 默认为普通智能识别
          res = await ocrRequestAPI(assignmentId_globle.value)
        }

        const endTime = performance.now()
        
        if (res.code === 0) {
          const { recognizedCode, processed_image_path, res_image_path } = res.data
          code.value = recognizedCode
          processedImagePath.value = processed_image_path || null
          resImagePath.value = res_image_path || null
          processedImageUrl.value = processed_image_path
          ocrResultImageUrl.value = res_image_path
          
          stopOcrAnimation(endTime - startTime) 
          codeResultStep.ocrDone = true 
          
          // 提示语也可以区分一下
          const modeText = type === 'deep' ? '深度识别' : '智能识别'
          Message.success(`${modeText}完成`)
        } else {
          clearInterval(progressInterval)
          ocrProgress.value.status = 'danger'
          Message.error('识别失败: ' + res.message)
        }
      } catch (err) {
        clearInterval(progressInterval)
        ocrProgress.value.status = 'danger'
        Message.error('识别请求异常')
      } finally {
        ocrLoading.value = false
      }
    }

    // --- 编译运行 ---
    const triggerCompile = async () => {
      if (!code.value) return
      
      compileLoading.value = true
      compileInfo.value = null; 
      codeResult.value = ''; 
      
      // 启动进度条
      startCompileAnimation() 

      try {
        const res = await compileRequestAPI(assignmentId_globle.value)
        
        // 成功逻辑
        if (res.code === 0 && res.data) {
          compileInfo.value = res.data 
          codeResult.value = res.data.compileSuccess ? (res.data.output || '无输出') : (res.data.error || '编译错误')
          stopCompileAnimation() 
          codeResultStep.compileDone = true 
          Message.success('运行完成')
        } 
        // 业务失败逻辑 (比如后端返回 code: 1002)
        else {
          if (compileProgressInterval) clearInterval(compileProgressInterval)
          compileProgress.value.status = 'danger'
          setTimeout(() => { compileProgress.value.visible = false }, 1000)
          
          Message.error(`请求失败: ${res.message || '未知错误'} (code: ${res.code})`)
        }
      } catch (err) {
        //  异常捕获逻辑 
        if (compileProgressInterval) clearInterval(compileProgressInterval)
        compileProgress.value.status = 'danger'
        setTimeout(() => { compileProgress.value.visible = false }, 1000)
        
        console.error('完整报错对象:', err) // 请务必看控制台

        //  让界面直接告诉你错在哪
        if (err.message && err.message.includes('timeout')) {
          Message.error('运行超时：后端处理时间过长 (超过60s)')
        } else if (err.response) {
          // 后端返回了非 200 的状态码 (404, 500, 502)
          Message.error(`服务器报错: ${err.response.status} ${err.response.statusText}`)
        } else {
          // 其他网络错误或前端代码写错了
          Message.error(`运行异常: ${err.message}`)
        }
      } finally {
        compileLoading.value = false
      }
    }

    // --- AI 评分 ---
    const triggerAI = async () => {
      if (!code.value) return
      aiLoading.value = true
      aiResult.value = null
      startAiAnimation() //  动画开始
      const startTime = performance.now()

      try {
        const res = await generateReportAPI(assignmentId_globle.value)
        //  模拟耗时 4秒 (AI 通常比较慢，模拟真实感)
        // await new Promise(resolve => setTimeout(resolve, 4000))
        const endTime = performance.now()
        // 模拟完美的 AI 报告数据
        // const res = {
        //   code: 0,
        //   data: {
        //     score: 92,
        //     reason: "代码逻辑清晰，标准输入输出使用规范，变量命名合理。", // 对应 comment
        //     breakdown: {
        //       correctness: 100,     // 正确性
        //       standardization: 90,  // 规范性
        //       efficiency: 85,       // 效率
        //       readability: 95       // 可读性
        //     },
        //     strengths: [
        //       "正确使用了 iostream 库",
        //       "主函数返回值规范",
        //       "代码缩进整齐"
        //     ],
        //     weaknesses: [
        //       "缺少必要的代码注释",
        //       "变量名 a, b 过于简单，建议使用更有意义的名称"
        //     ],
        //     suggestions: [
        //       "建议为变量添加注释说明用途",
        //       "考虑处理可能的整数溢出情况",
        //       "可以尝试将求和逻辑封装为函数"
        //     ]
        //   }
        // }
        if (res.code === 0) {
          const { score, rule_score,ai_score,breakdown, reason, suggestions, strengths, weaknesses } = res.data
          // 字段映射：reason -> comment
          aiResult.value = {
            score, 
            rule_score,
            ai_score,
            comment: reason,
            breakdown, 
            suggestions, 
            strengths, 
            weaknesses
          }
          
          stopAiAnimation(endTime - startTime) // 动画结束
          codeResultStep.aiDone = true 
        } else {
          clearInterval(aiProgressInterval)
          aiProgress.value.status = 'danger'
          Message.error('AI 批改失败: ' + res.message)
        }
      } catch (err) {
        clearInterval(aiProgressInterval)
        aiProgress.value.status = 'danger'
        Message.error('AI 请求异常')
      } finally {
        aiLoading.value = false
      }
    }

    // --- 清空逻辑 ---
    const handleDelete = (e) => {
      if (e) e.stopPropagation() 
      imageUrl.value = null
      assignmentId_globle.value = null
      handleReset()
      Message.info('已删除当前作业')
    }

    const handleReset = () => {
      code.value = ''
      processedImageUrl.value = null
      ocrResultImageUrl.value = null
      compileInfo.value = null
      aiResult.value = null
      codeResult.value = ''
      codeResultStep.ocrDone = false
      codeResultStep.compileDone = false
      codeResultStep.aiDone = false
      ocrProgress.value.visible = false
      aiProgress.value.visible = false
    }

    return {
      uploadLoading, ocrLoading, compileLoading, aiLoading,
      imageUrl, code, assignmentId_globle,
      codeResult, compileInfo, aiResult,
      processedImageUrl, ocrResultImageUrl,
      timings, aiTimings,
      ocrProgress, aiProgress, compileProgress,
      codeResultStep, modals,
      customUploadRequest, triggerOCR, triggerCompile, triggerAI, handleDelete,
      IconDelete,
      imagePreviewVisible,
      IconEye
    }
  }
}