<template>
  <div class="upload-container">
    <!-- 左侧：上传 + 代码运行结果 -->
    <div class="left-panel">
      <h3>📤 上传作业图片</h3>
      <el-upload
        class="upload-demo"
        drag
        :http-request="handleUpload"
        @change="handleUpload"
        :show-file-list="false"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
      </el-upload>
     <!-- 上传原图预览 -->
      <div v-if="imageUrl" class="image-preview">
        <h4>📷 上传图片（原图）</h4>
        <img
          :src="imageUrl"
          alt="上传的作业图片"
          class="thumb"
          @click="openPreview(imageUrl)"
        />
      </div>
<!-- OCR 进度（整体 + 两阶段） -->
      <div v-if="ocrProgress.visible" class="ocr-progress-panel">
        <h4>🔄 OCR 进度</h4>

        <div class="overall">
          <p class="small">整体进度</p>
          <el-progress :percentage="ocrProgress.percent" :status="ocrProgress.status" />
        </div>

        <div class="stage-list">
          <div class="stage-item">
            <div class="stage-head">
              <strong>预处理</strong>
              <span v-if="ocrProgress.steps[0].time !== null" class="time">⏱ {{ ocrProgress.steps[0].time }}s</span>
            </div>
            <el-progress :percentage="ocrProgress.steps[0].percent" :status="ocrProgress.status" :stroke-width="12" />
          </div>

          <div class="stage-item">
            <div class="stage-head">
              <strong>识别</strong>
              <span v-if="ocrProgress.steps[1].time !== null" class="time">⏱ {{ ocrProgress.steps[1].time }}s</span>
            </div>
            <el-progress :percentage="ocrProgress.steps[1].percent" :status="ocrProgress.status" :stroke-width="12" />
          </div>
        </div>
      </div>
      <!-- 处理后/识别结果 两张图并列展示 -->
      <div v-if="processedImageUrl || ocrResultImageUrl || processedImagePath || resImagePath" class="process-preview">
        <h4>🔍 识别过程可视化</h4>
        <div class="process-grid">
          <div class="process-item" v-if="processedImageUrl || processedImagePath">
            <p class="caption">预处理图片</p>
            <img
              v-if="processedImageUrl"
              :src="processedImageUrl"
              class="thumb"
              alt="预处理图片"
              @click="openPreview(processedImageUrl)"
            />
            <div v-else class="no-image">
              <p class="no-image-text">无法直接显示图片</p>
            </div>
            <p class="small-path" v-if="processedImagePath">{{ processedImagePath }}</p>
          </div>

          <div class="process-item" v-if="ocrResultImageUrl || resImagePath">
            <p class="caption">OCR 识别结果图</p>
            <img
              v-if="ocrResultImageUrl"
              :src="ocrResultImageUrl"
              class="thumb"
              alt="OCR结果图"
              @click="openPreview(ocrResultImageUrl)"
            />
            <div v-else class="no-image">
              <p class="no-image-text">无法直接显示图片</p>
            </div>
            <p class="small-path" v-if="resImagePath">{{ resImagePath }}</p>
          </div>
        </div>
        <!-- 显示前端测得总耗时 -->
        <div v-if="timings.total" class="timing-info">
          ⏱️ 总耗时：<strong>{{ timings.total }} 秒</strong>
        </div>
      </div>
      <!-- 代码运行结果 -->
      <div v-if="codeResult || compileInfo" class="code-result">
  <h4>📜 代码运行结果</h4>
  <!-- 编译详情 -->
  <div v-if="compileInfo" class="compile-info">
    <h5>🧩 编译/运行详情</h5>
    <p>
      <strong>状态：</strong>
      <el-tag :type="compileInfo.compileSuccess ? 'success' : 'danger'">
        {{ compileInfo.compileSuccess ? '成功' : '失败' }}
      </el-tag>
    </p>
    <!-- 输出结果 -->
  <p><strong>运行结果：</strong>{{ codeResult || '无输出' }}</p>
    <p><strong>语言：</strong>{{ compileInfo.language || '未知' }}</p>
    <p><strong>代码长度：</strong>{{ compileInfo.codeLengthBytes || '未知' }} 字节</p>
    <p v-if="compileInfo.submitTime"><strong>提交时间：</strong>{{ compileInfo.submitTime }}</p>
    <p v-if="compileInfo.evalTime"><strong>评测耗时：</strong>{{ compileInfo.evalTime }}</p>
  </div>
</div>
    </div>

    <!-- 右侧：编辑器 + 运行按钮 -->
    <div class="right-panel">
      <h3>💻 代码编辑区</h3>
        <!-- 使用 Element Plus 的文本区域 -->
      <el-input
        v-model="code"
        type="textarea"
        :rows="20"
        placeholder="请输入 C++ 代码"
        resize="none"
        style="font-family: 'Courier New', monospace; font-size: 14px;"
      />

      <div class="actions">
        <el-button
          type="primary"
          :disabled="!code"
          @click="runCode"
        >
          运行代码
        </el-button>

        <el-button
          type="warning"
          :disabled="!code"
          @click="handleSubmit"
        >
          调用AI批改
        </el-button>
      </div>
      <!-- 🧭 AI 评分进度（放在结果区域上方） -->
      <div v-if="aiProgress.visible" class="ocr-progress-panel">
        <h4>🤖 AI 评分进度</h4>

        <div class="overall">
          <p class="small">整体进度</p>
          <el-progress :percentage="aiProgress.percent" :status="aiProgress.status" />
        </div>

        <div class="stage-list">
          <div class="stage-item">
            <div class="stage-head">
              <strong>分析</strong>
              <span v-if="aiProgress.steps[0].time !== null" class="time">⏱ {{ aiProgress.steps[0].time }}s</span>
            </div>
            <el-progress :percentage="aiProgress.steps[0].percent" :status="aiProgress.status" :stroke-width="12" />
          </div>

          <div class="stage-item">
            <div class="stage-head">
              <strong>报告生成</strong>
              <span v-if="aiProgress.steps[1].time !== null" class="time">⏱ {{ aiProgress.steps[1].time }}s</span>
            </div>
            <el-progress :percentage="aiProgress.steps[1].percent" :status="aiProgress.status" :stroke-width="12" />
          </div>
        </div>

        <div v-if="aiTimings.total" class="timing-info">
          ⏱️ 前端测得 AI 总耗时：<strong>{{ aiTimings.total }} 秒</strong>
        </div>
      </div>

      <div v-if="aiResult" class="ai-result">
        <!-- AI 进度（整体 + 两阶段） -->
        <h4>🧠 AI 批改结果</h4>
        <el-card>
          <p><strong>得分：</strong>{{ aiResult.score }}/100</p>
          <p><strong>评语：</strong>{{ aiResult.comment }}</p>

          <!-- 分项得分 -->
          <div>
            <p><strong>正确性得分：</strong>{{ aiResult.breakdown.correctness }}/100</p>
            <p><strong>规范化得分：</strong>{{ aiResult.breakdown.standardization }}/100</p>
            <p><strong>效率得分：</strong>{{ aiResult.breakdown.efficiency }}/100</p>
            <p><strong>可读性得分：</strong>{{ aiResult.breakdown.readability }}/100</p>
          </div>

          <!-- 改进建议 -->
          <div>
            <p><strong>改进建议：</strong></p>
            <ul>
              <li v-for="(suggestion, index) in aiResult.suggestions" :key="index">{{ suggestion }}</li>
            </ul>
          </div>

          <!-- 优缺点 -->
          <div>
            <p><strong>优点：</strong></p>
            <ul>
              <li v-for="(strength, index) in aiResult.strengths" :key="index">{{ strength }}</li>
            </ul>
            <p><strong>缺点：</strong></p>
            <ul>
              <li v-for="(weakness, index) in aiResult.weaknesses" :key="index">{{ weakness }}</li>
            </ul>
          </div>
          <!-- 文件信息 -->
          <div v-if="aiResult.originalFile">
            <p><strong>文件名：</strong>{{ aiResult.originalFile.fileName }}</p>
            <p><strong>文件内容（Base64）：</strong>{{ aiResult.originalFile.fileContentBase64 }}</p>
          </div>
          <!-- <p><strong>报告生成时间：</strong>{{ aiResult.generatedAt }}</p> -->
        </el-card>
      </div>
    </div>
    <!-- 图片放大预览弹窗 -->
    <el-dialog :visible.sync="previewDialogVisible" width="70%">
      <img :src="currentPreviewImage" style="width: 100%; height: auto;" />
    </el-dialog>
  </div>
</template>
<script src="./UploadGrade.js"></script>
<style scoped src="./UploadGrade.css"></style>
