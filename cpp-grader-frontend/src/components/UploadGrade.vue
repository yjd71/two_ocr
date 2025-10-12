<template>
  <div class="upload-container">
    <!-- 左侧：上传 + OCR识别 -->
    <div class="left-panel">
      <h3>📤 上传作业图片</h3>
      <el-upload
        class="upload-demo"
        drag
        :http-request="handleUpload"
        :show-file-list="false"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
      </el-upload>

      <div v-if="ocrText" class="ocr-result">
        <h4>🧾 OCR识别结果</h4>
        <pre>{{ ocrText }}</pre>
        <el-button
          type="primary"
          size="small"
          @click="loadToEditor"
        >
          填入右侧编辑器
        </el-button>
      </div>
    </div>

    <!-- 右侧：编辑器 + AI批改 -->
    <div class="right-panel">
      <h3>💻 代码编辑区</h3>
      <monaco-editor
        v-model="code"
        language="cpp"
        theme="vs-dark"
        height="400px"
      />

      <div class="actions">
        <el-button
          type="success"
          :disabled="!code"
          @click="handleSubmit"
        >
          调用AI批改
        </el-button>

        <el-button
          type="warning"
          :disabled="!aiResult"
          @click="resetForEdit"
        >
          修改后再批改
        </el-button>
      </div>

      <div v-if="aiResult" class="ai-result">
        <h4>🧠 AI 批改结果</h4>
        <el-card>
          <p><strong>得分：</strong>{{ aiResult.score }}/100</p>
          <p><strong>评语：</strong>{{ aiResult.comment }}</p>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import MonacoEditor from 'monaco-editor-vue3'

// ---------------- 数据状态 ----------------
const code = ref('')
const ocrText = ref('')
const aiResult = ref(null)

// ---------------- 上传并识别 ----------------
const handleUpload = async (options) => {
  const file = options.file
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    ElMessage.info('正在进行 OCR 识别...')
    // 模拟 OCR 请求（实际应调用后端）
    await new Promise((r) => setTimeout(r, 1000))
    ocrText.value = `#include <iostream>\nusing namespace std;\nint main(){\n    cout << "Hello World";\n    return 0;\n}`
    ElMessage.success('OCR识别完成，请点击“填入右侧编辑器”')
  } catch (err) {
    ElMessage.error('OCR识别失败')
  }
}

// ---------------- 将OCR结果加载到编辑器 ----------------
const loadToEditor = () => {
  code.value = ocrText.value
  aiResult.value = null
  ElMessage.info('识别代码已填入右侧，可修改后再批改')
}

// ---------------- 触发AI批改 ----------------
const handleSubmit = async () => {
  if (!code.value) {
    ElMessage.warning('请先输入或加载代码')
    return
  }

  ElMessage.info('正在调用AI批改，请稍候...')
  aiResult.value = null

  // 模拟 AI 批改接口
  await new Promise((r) => setTimeout(r, 1500))

  // 模拟结果
  aiResult.value = {
    score: Math.floor(Math.random() * 40 + 60),
    comment: '代码逻辑清晰，格式规范，输出结果正确，可适当优化变量命名。'
  }
  ElMessage.success('批改完成 ✅')
}

// ---------------- 修改后再批改 ----------------
const resetForEdit = () => {
  aiResult.value = null
  ElMessage.info('请修改代码后重新点击“调用AI批改”')
}
</script>

<style scoped>
.upload-container {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 20px;
}

.left-panel, .right-panel {
  width: 48%;
}

.ocr-result {
  margin-top: 15px;
  background: #f9f9f9;
  padding: 10px;
  border-radius: 10px;
}

.actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

.ai-result {
  margin-top: 15px;
}
</style>