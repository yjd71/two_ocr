// 导入模拟的 API 函数
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
const imageUrl = ref(null)  // 确保这里正确地定义了 imageUrl
import {
  mockUploadAssignment,
  mockOCRRecognition,
  mockRunCode,
  mockGenerateReport
} from '/src/mockApi.js'  // 引入 mock 文件
// 1. 引入封装好的 API (路径根据你的项目结构，@ 代表 src 是常见配置，如果报错请用 ../api/assignment.js)
import { 
  UploadAssignmentAPI, 
  ocrRequestAPI, 
  compileRequestAPI, 
  generateReportAPI 
} from '/src/api/assignment.js'
// 状态管理
const code = ref('')  // Monaco 编辑器中显示的代码
const codeResult = ref('')  // 存储代码运行结果
const aiResult = ref(null)  // 存储AI批改结果
const loading = ref(false)
const assignmentId_globle = ref(null)
// ---------- 新增：图片相关状态 ----------
const processedImageUrl = ref(null)   // 可直接用于 <img :src="...">
const ocrResultImageUrl = ref(null)
const processedImagePath = ref(null)  // 原始后端返回路径（用于调试显示）
const resImagePath = ref(null)

const previewDialogVisible = ref(false)
const currentPreviewImage = ref(null)
// 计时对象（前端测得）
const timings = ref({ total: null })
const recognizedCode = ref('')  // 添加该变量用于模拟OCR代码
// 新增：编译详情对象
const compileInfo = ref(null)
// OCR 进度（可视化两阶段）
const ocrProgress = ref({
  visible: false,
  percent: 0,           // overall
  status: 'active',     // 'active'|'success'|'exception'
  steps: [
    { name: 'preprocess', percent: 0, time: null }, // 预处理
    { name: 'recognize', percent: 0, time: null }   // 识别
  ]
})
// 用于控制进度动画的 interval
let progressInterval = null
// ---------- 新增：AI 评分进度与计时 ----------
const aiTimings = ref({ total: null })

const aiProgress = ref({
  visible: false,
  percent: 0,
  status: 'active', // 'active'|'success'|'exception'
  steps: [
    { name: 'analysis', percent: 0, time: null }, // 分析/特征提取
    { name: 'report', percent: 0, time: null }    // 报告生成
  ]
})
// 启动 AI 假进度动画
const startAiProgressAnimation = () => {
  aiProgress.value.visible = true
  aiProgress.value.status = 'active'
  aiProgress.value.percent = 5
  aiProgress.value.steps[0].percent = 0
  aiProgress.value.steps[1].percent = 0
  aiProgress.value.steps[0].time = null
  aiProgress.value.steps[1].time = null
  aiTimings.value.total = null

  if (aiProgressInterval) {
    clearInterval(aiProgressInterval)
    aiProgressInterval = null
  }

  let p0 = 0, p1 = 0
  aiProgressInterval = setInterval(() => {
    const r = Math.random()
    // 先偏向分析阶段，然后报告阶段推进
    if (p0 < 60 && r < 0.7) {
      p0 += 1 + Math.random() * 3
    } else {
      p1 += 0.5 + Math.random() * 3
    }
    p0 = Math.min(p0, 95)
    p1 = Math.min(p1, 95)
    const combined = Math.min(99, p0 + p1 * 0.9)
    aiProgress.value.percent = Math.round(combined)
    aiProgress.value.steps[0].percent = Math.round(p0)
    aiProgress.value.steps[1].percent = Math.round(p1)
  }, 200)
}

// 结束 AI 动画并把耗时按比例分配到两个阶段
const finalizeAiProgress = (elapsedMs) => {
  if (aiProgressInterval) { clearInterval(aiProgressInterval); aiProgressInterval = null }

  const totalSec = elapsedMs / 1000
  aiTimings.value.total = totalSec.toFixed(2)

  const p0 = Math.max(aiProgress.value.steps[0].percent, 0)
  const p1 = Math.max(aiProgress.value.steps[1].percent, 0)
  const sum = p0 + p1
  let t0 = 0, t1 = 0
  if (sum <= 0) {
    t0 = t1 = totalSec / 2
  } else {
    t0 = totalSec * (p0 / sum)
    t1 = totalSec * (p1 / sum)
  }

  aiProgress.value.steps[0].time = t0.toFixed(2)
  aiProgress.value.steps[1].time = t1.toFixed(2)

  aiProgress.value.steps[0].percent = 100
  aiProgress.value.steps[1].percent = 100
  aiProgress.value.percent = 100
  aiProgress.value.status = 'success'
}

let aiProgressInterval = null
// ---------------- 上传并识别 ----------------
  const handleUpload = async (options) => {
    const file = options.file
    if (!file) return

   const formData = new FormData();
  formData.append("file", file); // 添加文件到 FormData
    try {
      ElMessage.info('正在上传作业文件...')
       const reader = new FileReader()
      reader.onloadend = () => {
        imageUrl.value = reader.result  // 设置预览图片
      }
      reader.readAsDataURL(file)  // 将文件转换为 Base64 图片 URL

      // 调用上传作业 API，将文件名和 Base64 编码的文件内容发送到后端
      const response = await UploadAssignmentAPI(formData)
      //const response = await mockUploadAssignment(formData)
      // 判断上传是否成功
      if (response.code === 0) {
        const {assignmentId, fileName} = response.data  // 获取返回的 assignmentId 和 fileName
        ElMessage.success(`作业上传成功！作业ID：${assignmentId}，文件名：${fileName}`)
        assignmentId_globle.value = assignmentId
        // 上传成功后立即触发 OCR 识别
        startProgressAnimation()
        await handleOCR(assignmentId)  // 调用 OCR 识别接口
        // 显示上传的文件图片预览

      }
      else {
        // 上传失败时显示错误消息
        if (response.code === 1001) {
          ElMessage.error('参数校验失败，上传的文件格式或内容不符合要求')
        } else {
          ElMessage.error( response.message + '上传失败，请重试')
        }
      }
    } catch (err) {
      // 网络请求或其他错误
      ElMessage.error('作业上传失败')
    }
  }

// ----------------- 进度动画控制（启动） -----------------
const startProgressAnimation = () => {
  // reset
  ocrProgress.value.visible = true
  ocrProgress.value.status = 'active'
  ocrProgress.value.percent = 5
  ocrProgress.value.steps[0].percent = 0
  ocrProgress.value.steps[1].percent = 0
  ocrProgress.value.steps[0].time = null
  ocrProgress.value.steps[1].time = null
  timings.value.total = null

  // clear existing
  if (progressInterval) {
    clearInterval(progressInterval)
    progressInterval = null
  }

  // internal "simulated" progress values (floats)
  let p0 = 0
  let p1 = 0

  progressInterval = setInterval(() => {
    // random but biased to advance p0 first, then p1
    const r = Math.random()
    if (p0 < 60 && r < 0.7) {
      p0 += 1 + Math.random() * 3
    } else {
      p1 += 0.5 + Math.random() * 3
    }

    // cap
    p0 = Math.min(p0, 95)
    p1 = Math.min(p1, 95)

    // overall percent roughly p0+p1 but scaled to max 99 while waiting
    const combined = Math.min(99, p0 + p1 * 0.9)
    ocrProgress.value.percent = Math.round(combined)
    ocrProgress.value.steps[0].percent = Math.round(p0)
    ocrProgress.value.steps[1].percent = Math.round(p1)
  }, 200)
}

// ----------------- Stop animation and finalize progress 根据 response 填充耗时 -----------------
const finalizeProgress = (elapsedMs) => {
  if (progressInterval) {
    clearInterval(progressInterval)
    progressInterval = null
  }

  // total seconds
  const totalSec = (elapsedMs / 1000)
  timings.value.total = totalSec.toFixed(2)

  // Use last percent values to split time. If both zero, split equally.
  const p0 = Math.max(ocrProgress.value.steps[0].percent, 0)
  const p1 = Math.max(ocrProgress.value.steps[1].percent, 0)
  const sum = p0 + p1
  let t0 = 0, t1 = 0
  if (sum <= 0) {
    t0 = t1 = (totalSec / 2)
  } else {
    t0 = totalSec * (p0 / sum)
    t1 = totalSec * (p1 / sum)
  }

  ocrProgress.value.steps[0].time = t0.toFixed(2)
  ocrProgress.value.steps[1].time = t1.toFixed(2)

  // finalize percents to 100
  ocrProgress.value.steps[0].percent = 100
  ocrProgress.value.steps[1].percent = 100
  ocrProgress.value.percent = 100
  ocrProgress.value.status = 'success'
}

// ---------------- OCR 识别 ----------------
  const handleOCR = async (assignmentId) => {
    try {
      ElMessage.info('正在进行 OCR 识别...')
      console.log("OCR 识别图片ID",assignmentId_globle.value);
      const startTime = performance.now()
      const response = await ocrRequestAPI(assignmentId_globle.value)
      const endTime = performance.now()
      const elapsed = endTime - startTime
      if (response.code === 0) {
        const {recognizedCode, processed_image_path, res_image_path} = response.data  // 获取 OCR 识别到的代码
        console.log('✅ OCR 识别到的代码:', recognizedCode)
        code.value = recognizedCode
      processedImagePath.value = processed_image_path || null
      resImagePath.value = res_image_path || null
        processedImageUrl.value = processed_image_path
      ocrResultImageUrl.value = res_image_path
        // stop animation & finalize progress using elapsed time
      finalizeProgress(elapsed)
      ElMessage.success(`OCR识别完成，前端测得耗时 ${(elapsed/1000).toFixed(2)} 秒`)
      } else {
        if (progressInterval) { clearInterval(progressInterval); progressInterval = null }
      ocrProgress.value.status = 'exception'
        ElMessage.error(response.message || 'OCR 识别失败')
      }
    } catch (err) {
      console.error('handleOCR error', err)
    if (progressInterval) { clearInterval(progressInterval); progressInterval = null }
    ocrProgress.value.status = 'exception'
      ElMessage.error('OCR 识别失败')
    }
  }

// ---------------- 运行代码 ----------------
 const runCode = async () => {
  if (!code.value) {
    ElMessage.warning('请先输入代码')
    return
  }

  loading.value = true
  compileInfo.value = null // 每次运行前清空旧信息

  try {
    const response = await compileRequestAPI(assignmentId_globle.value)
    console.log("编译运行图片ID", assignmentId_globle.value);

    if (response.code === 0 && response.data) {
      const { compileSuccess, output, error, language, codeLengthBytes, submitTime, evalTime } = response.data

      // ✅ 设置 codeResult：保留现有逻辑
      codeResult.value = compileSuccess ? (output || '无输出') : (error || '编译失败')

      // ✅ 保存编译详情
      compileInfo.value = {
        compileSuccess,
        output,
        error,
        language,
        codeLengthBytes,
        submitTime,
        evalTime,
      }

      if (compileSuccess) {
        ElMessage.success('编译成功！')
      } else {
        ElMessage.error('编译失败！')
      }
    } else {
      ElMessage.error(response.message || '请求失败')
    }
  } catch (err) {
    ElMessage.error('编译请求失败')
    console.error('runCode error', err)
  } finally {
    loading.value = false
  }
}

// ---------------- 生成评分报告 ----------------
  const handleSubmit = async () => {
    if (!code.value) {
      ElMessage.warning('请先输入代码')
      return
    }

    loading.value = true
    aiResult.value = null
    try {
      console.log(" 生成评分报告图片ID",assignmentId_globle.value);
      // 发送生成评分报告请求到后端
      startAiProgressAnimation()
    const startTime = performance.now()
      ElMessage.info('正在进行 AI 评分...')
      const response = await generateReportAPI(assignmentId_globle.value)
      //const response = await mockGenerateReport('abcd1234')
       const endTime = performance.now()
    const elapsed = endTime - startTime
      // 判断报告生成是否成功
      if (response.code === 0) {
        const {
          score,
          breakdown,
          reason,
          suggestions,
          strengths,
          weaknesses,


        } = response.data
        // 展示评分报告
        aiResult.value = {
          score: score,
          comment: reason,
          breakdown: breakdown,  // 分项得分
          suggestions: suggestions,  // 改进建议
          strengths: strengths,  // 优点
          weaknesses: weaknesses,  // 缺点


        }
  // finalize progress and timings (前端测得)
      finalizeAiProgress(elapsed)
        ElMessage.success('评分报告生成完成！')
      } else if (response.code === 1001) {
        if (aiProgressInterval) { clearInterval(aiProgressInterval); aiProgressInterval = null }
      aiProgress.value.status = 'exception'
        ElMessage.error('参数校验失败')
      } else if (response.code === 1002) {
        if (aiProgressInterval) { clearInterval(aiProgressInterval); aiProgressInterval = null }
      aiProgress.value.status = 'exception'
        ElMessage.error(`服务异常: ${response.data?.detail || '未知错误'}`)
      } else {
        if (aiProgressInterval) { clearInterval(aiProgressInterval); aiProgressInterval = null }
      aiProgress.value.status = 'exception'
        ElMessage.error(response.message || '请求处理失败')
      }
    } catch (err) {
      if (aiProgressInterval) { clearInterval(aiProgressInterval); aiProgressInterval = null }
      aiProgress.value.status = 'exception'
      aiResult.value = null
      ElMessage.error('生成评分报告失败')
    } finally {
      loading.value = false
    }
  }

/* -------------- 预览弹窗 -------------- */
const openPreview = (url) => {
  if (!url) return
  currentPreviewImage.value = url
  previewDialogVisible.value = true
}

// ✅ 必须添加默认导出！
export default {
    components: {
     UploadFilled,
  },
  setup() {
    return {
      imageUrl,
      processedImageUrl,
      ocrResultImageUrl,
      processedImagePath,
      resImagePath,
      previewDialogVisible,
      currentPreviewImage,
      code,
      codeResult,
      aiResult,
      assignmentId_globle,
      loading,
      timings, // ✅ 确保 timings 在 setup 中返回
      ocrProgress,
      compileInfo,
      handleUpload,
      handleOCR,
      runCode,
      handleSubmit,
      openPreview,
      aiProgress,
      aiTimings,
      startAiProgressAnimation,   // 非必需对外暴露，但可以暴露用于调试
      finalizeAiProgress,         // 同上（可选）
    }
  }
}