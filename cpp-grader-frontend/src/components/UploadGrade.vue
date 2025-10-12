<template>
  <div class="page-container">
    <el-row :gutter="20">
      <!-- 左边：上传与预览 -->
      <el-col :span="12">
  <el-card>
    <h3>上传作业图片（OCR识别）</h3>
    <el-upload
      drag
      action="#"
      :auto-upload="false"
      :on-change="handleOCR"
      accept="image/*"
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">拖拽或点击上传图片</div>
    </el-upload>

    <!-- OCR识别结果 -->
    <div v-if="ocrText" class="ocr-result">
      <el-divider></el-divider>
      <h4>OCR识别结果：</h4>
      <pre>{{ ocrText }}</pre>
    </div>

    <el-button
      type="primary"
      style="margin-top: 10px"
      :loading="loading"
      @click="handleSubmit"
    >
      调用AI批改
    </el-button>
  </el-card>
</el-col>

      <!-- 右边：Monaco 编辑器 + 打分结果 -->
      <el-col :span="12">
  <el-card>
    <h3>作业编辑与评分</h3>

    <!-- Monaco 编辑器 -->
    <monaco-editor
      v-model="code"
      language="cpp"
      theme="vs-dark"
      height="400px"
    />

    <!-- AI 批改结果展示 -->
    <div v-if="aiResult" class="ai-result">
      <el-divider></el-divider>
      <h4>AI 批改结果：</h4>
      <p><b>得分：</b> {{ aiResult.score }} / 100</p>
      <el-progress :percentage="aiResult.score" :color="'#409EFF'"></el-progress>
      <p><b>评语：</b> {{ aiResult.comment }}</p>
    </div>
  </el-card>
</el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import MonacoEditor from 'monaco-editor-vue3'

// ---------------------
// 状态变量
// ---------------------
const ocrText = ref('')
const editorText = ref('')
const aiResult = ref('')
const loading = ref(false)

// ---------------------
// 上传并OCR识别
// ---------------------
async function handleUpload({ file }) {
  try {
    // 将图片转为 base64
    const reader = new FileReader()
    reader.onload = async (e) => {
      const base64 = e.target.result

      // 调用后端 OCR 接口
      const res = await fetch('http://127.0.0.1:8000/api/ocr', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: base64 }),
      })

      if (!res.ok) throw new Error('OCR识别失败')

      const data = await res.json()
      ocrText.value = data.text
      editorText.value = data.text // 自动填入 Monaco
      ElMessage.success('OCR识别成功！')
    }

    reader.readAsDataURL(file)
  } catch (err) {
    console.error(err)
    ElMessage.error('上传或识别失败')
  }

  return false // 阻止默认上传行为
}

const handleSubmit = async () => {
  // 模拟调用AI接口
  aiResult.value = {
    score: 92,
    comment: '代码结构清晰，变量命名合理，但可以进一步优化循环部分。'
  }
}
// ---------------------
// 上传逻辑 + OCR调用
// ---------------------
const handleOCR = async (file) => {
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file.raw)

    const res = await fetch('http://127.0.0.1:8000/api/ocr', {
      method: 'POST',
      body: formData
    })
    const data = await res.json()
    ocrText.value = data.text  // 显示在左边
    code.value = data.text     // 自动填入右边 Monaco
    ElMessage.success('OCR识别完成')
  } catch (err) {
    console.error(err)
    ElMessage.error('OCR识别失败')
  } finally {
    loading.value = false
  }
  return false // 阻止 element-plus 自动上传
}

// ---------------------
// 调用 AI 批改接口
// ---------------------
async function sendToAI() {
  loading.value = true
  aiResult.value = ''
  try {
    const res = await fetch('http://127.0.0.1:8000/api/grade', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: editorText.value }),
    })

    if (!res.ok) throw new Error('AI批改失败')

    const data = await res.json()
    aiResult.value = data.result
    ElMessage.success('AI批改完成！')
  } catch (err) {
    console.error(err)
    ElMessage.error('批改失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.upload-card,
.editor-card {
  border-radius: 12px;
}

.upload-box {
  width: 100%;
  border: 2px dashed #aaa;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
}

.ocr-text-preview {
  margin-top: 20px;
}

.score-section {
  background: #1e1e1e;
  color: #00e676;
  padding: 15px;
  border-radius: 8px;
  white-space: pre-wrap;
}
</style>