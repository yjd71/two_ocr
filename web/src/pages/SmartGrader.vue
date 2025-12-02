<template>
  <div class="page-background">
    <div class="grader-container">
      
      <a-row :gutter="40" class="main-row">
        
        <a-col :span="12" style="height: 100%">
          <a-card class="styled-card left-card" :bordered="false">
            <template #title>
              <div class="card-title">
                <span class="title-icon">📤</span> 原始作业上传
              </div>
            </template>
            
            <div class="upload-wrapper-layer">
              <div v-if="imageUrl" class="preview-btn" @click.stop="imagePreviewVisible = true">
                <icon-eye />
              </div>
              <div v-if="imageUrl" class="delete-btn" @click.stop="handleDelete"><icon-delete /></div>
              <div class="visual-layer">
                <div v-if="imageUrl" class="preview-mode">
                  <img :src="imageUrl" class="preview-img" />
                  <div class="re-upload-tip">点击任意处更换</div>
                </div>
                <div v-else class="empty-mode">
                  <div class="icon-bg">
                    <icon-upload class="upload-icon" />
                  </div>
                  <div class="upload-main-text">点击或拖拽上传作业图片</div>
                  <div class="upload-sub-text">支持 JPG, PNG, BMP 格式</div>
                </div>
              </div>
              <a-upload
                class="invisible-uploader"
                draggable
                :show-file-list="false"
                :custom-request="customUploadRequest"
              />
            </div>
            
            <div class="left-footer">
               <a-dropdown @select="triggerOCR" position="top" :disabled="!assignmentId_globle">
                 <a-button type="primary" size="large" long class="action-btn-main" 
                   :loading="ocrLoading" 
                   :disabled="!assignmentId_globle"
                 >
                    <template #icon><icon-scan /></template>
                    开始识别
                    <icon-down style="margin-left: 8px"/>
                 </a-button>
                 <template #content>
                   <a-doption value="standard">⚡ 智能识别 (快速)</a-doption>
                   <a-doption value="deep">🧠 深度识别 (DeepSeek)</a-doption>
                 </template>
               </a-dropdown>
            </div>
            
            </a-card>
        </a-col>
  
        <a-col :span="12" style="height: 100%">
          <a-card class="styled-card right-card" :bordered="false">
            <template #title>
              <div class="card-title">
                <span class="title-icon">📊</span> 识别与处理结果
              </div>
            </template>
            
            <div class="result-stream">
              <div v-if="!codeResultStep.ocrDone && !ocrProgress.visible" class="empty-state">
                 <div class="empty-icon-bg"><icon-scan style="font-size: 32px; color: #c9cdd4;" /></div>
                 <p>请在左侧上传图片并点击“开始识别”</p>
                 <p class="sub">识别结果将在此处展示</p>
              </div>
  
              <div v-if="ocrProgress.visible" class="progress-card animate-in">
                <div class="progress-header">
                  <span class="loading-text">🔄 正在进行文字识别...</span>
                  <span class="percentage">{{ ocrProgress.percent }}%</span>
                </div>
                <a-progress :percent="ocrProgress.percent/100" :status="ocrProgress.status" :show-text="false" size="large" :color="{ '0%': '#165dff', '100%': '#722ed1' }" />
              </div>
  
              <div v-if="codeResultStep.ocrDone && !ocrProgress.visible" class="result-item animate-in">
                <a-alert type="success" show-icon :title="null" class="styled-alert">
                  <div class="alert-content">
                    <span>✅ 识别成功 <span class="time-tag">({{ timings.total }}s)</span></span>
                    <a-button type="text" size="small" @click="modals.code = true">查看代码</a-button>
                  </div>
                </a-alert>
              </div>

              <div v-if="compileProgress.visible" class="progress-card animate-in">
                <div class="progress-header">
                  <span class="loading-text">⚡ 正在编译运行代码...</span>
                  <span class="percentage">{{ compileProgress.percent }}%</span>
                </div>
                <a-progress :percent="compileProgress.percent/100" :status="compileProgress.status" :show-text="false" size="large" :color="{ '0%': '#00b42a', '100%': '#86df6b' }" />
              </div>
  
              <div v-if="codeResultStep.compileDone && !compileProgress.visible" class="result-item animate-in">
                <a-alert :type="compileInfo?.compileSuccess ? 'success' : 'error'" show-icon :title="null" class="styled-alert">
                  <div class="alert-content">
                    <span>{{ compileInfo?.compileSuccess ? '✅ 运行成功' : '❌ 运行失败' }}</span>
                    <a-button type="text" size="small" @click="modals.run = true">查看详情</a-button>
                  </div>
                </a-alert>
              </div>
  
              <div v-if="aiProgress.visible" class="progress-card animate-in">
                <div class="progress-header">
                  <span class="loading-text">🤖 正在生成 AI 评分报告...</span>
                  <span class="percentage">{{ aiProgress.percent }}%</span>
                </div>
                <a-progress :percent="aiProgress.percent/100" :status="aiProgress.status" :show-text="false" size="large" :color="{ '0%': '#ff7d00', '100%': '#f53f3f' }"/>
                <div class="steps-detail">
                  <div class="step-item"><span>🔍 代码分析</span><a-progress :percent="aiProgress.steps[0].percent/100" style="width:50px" size="mini" :show-text="false"/></div>
                  <div class="step-item"><span>📄 报告生成</span><a-progress :percent="aiProgress.steps[1].percent/100" style="width:50px" size="mini" :show-text="false"/></div>
                </div>
              </div>
  
              <div v-if="codeResultStep.aiDone && !aiProgress.visible" class="result-item animate-in">
                <a-alert type="success" show-icon :title="null" class="styled-alert">
                  <div class="alert-content">
                    <span>🤖 AI 批改完成 <span class="time-tag">(得分: {{ aiResult?.score || 0 }}, {{ aiTimings.total }}s)</span></span>
                    <a-button type="text" size="small" @click="modals.ai = true">查看报告</a-button>
                  </div>
                </a-alert>
              </div>
            </div>
            
            <div class="right-footer-actions">
              <a-space size="large">
                <a-button type="primary" status="success" shape="round" size="large" 
                  @click="triggerCompile" 
                  :loading="compileLoading" 
                  :disabled="!codeResultStep.ocrDone || ocrLoading || compileProgress.visible"
                >
                  <template #icon><icon-play-circle /></template>
                  {{ codeResultStep.ocrDone ? '编译运行' : '等待识别...' }}
                </a-button>
  
                <a-button type="primary" status="warning" shape="round" size="large" 
                  @click="triggerAI" 
                  :loading="aiLoading" 
                  :disabled="!codeResultStep.ocrDone || ocrLoading || aiProgress.visible"
                >
                  <template #icon><icon-robot /></template>
                  {{ codeResultStep.ocrDone ? 'AI 智能批改' : '等待识别...' }}
                </a-button>
              </a-space>
            </div>
          </a-card>
        </a-col>
      </a-row>
<a-image-preview
        :src="imageUrl"
        v-model:visible="imagePreviewVisible"
      />
      <div class="mode-info-box">
        <div class="info-title">
          <icon-info-circle-fill /> 模式说明
        </div>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">⚡ 智能识别：</span>
            <span class="info-text">采用 Paddle-OCR 模型，适用于印刷体和简单的手写体，快速方便识别。</span>
          </div>
          <div class="info-item">
            <span class="info-label">🧠 深度识别：</span>
            <span class="info-text">采用 DeepSeek 模型，适用于复杂的识别场景，识别精度高但耗时较长。</span>
          </div>
        </div>
      </div>
  
      <a-modal v-model:visible="modals.code" title="代码预览" width="700px" :footer="false">
        <div class="code-box">
          <a-textarea v-model="code" :auto-size="{ minRows: 10, maxRows: 25 }" readonly />
        </div>
      </a-modal>

      <a-modal v-model:visible="modals.run" title="🖥️ 编译运行详情" width="600px" :footer="false">
      <div v-if="compileInfo">
        <a-descriptions :column="2" bordered size="small" layout="inline-horizontal">
          <a-descriptions-item label="运行状态">
            <a-tag :color="compileInfo.compileSuccess ? 'green' : 'red'">{{ compileInfo.compileSuccess ? '✅ 编译成功' : '❌ 编译失败' }}</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="编程语言">{{ compileInfo.language || 'Unknown' }}</a-descriptions-item>
          <a-descriptions-item label="评测耗时">{{ compileInfo.evalTime || '0ms' }}</a-descriptions-item>
          <a-descriptions-item label="代码长度">{{ compileInfo.codeLengthBytes || 0 }} Bytes</a-descriptions-item>
          <a-descriptions-item label="提交时间" :span="2">{{ compileInfo.submitTime || '-' }}</a-descriptions-item>
        </a-descriptions>
        <a-divider orientation="left" style="margin: 15px 0 10px 0;">终端输出</a-divider>
        <div class="terminal-box" :class="{ 'is-error': !compileInfo.compileSuccess }">
          {{ compileInfo.compileSuccess ? (compileInfo.output || '无输出') : (compileInfo.error || '编译失败') }}
        </div>
      </div>
    </a-modal>

    <a-modal v-model:visible="modals.ai" title="🧠 AI 智能批改报告" width="800px" :footer="false">
      <div v-if="aiResult" class="ai-report">
        <a-alert type="success" :show-icon="false" style="margin-bottom: 20px;">
          <a-row align="middle" :gutter="24">
            <a-col :span="6" style="text-align: center; border-right: 1px solid #e5e6eb;">
              <div style="font-size: 14px; color: #86909c;">综合得分</div>
              <div style="font-size: 36px; font-weight: bold; color: #00b42a; line-height: 1.2;">{{ aiResult.ai_score }}</div>
            </a-col>
            <a-col :span="18">
              <div style="font-weight: bold; margin-bottom: 5px;">综合评语：</div>
              <div style="color: #4e5969;">{{ aiResult.comment }}</div>
            </a-col>
          </a-row>
        </a-alert>
        <a-descriptions title="📊 能力维度分析" :column="2" bordered size="small" style="margin-bottom: 20px;">
          <a-descriptions-item label="代码正确性">
            <a-progress :percent="aiResult.breakdown?.correctness / 100" status="success" :show-text="false" style="width: 100px; margin-right: 10px;" />
            <strong>{{ aiResult.breakdown?.correctness }}</strong> / 100
          </a-descriptions-item>
          <a-descriptions-item label="代码规范性">
             <a-progress :percent="aiResult.breakdown?.standardization / 100" status="normal" :show-text="false" style="width: 100px; margin-right: 10px;" />
             <strong>{{ aiResult.breakdown?.standardization }}</strong> / 100
          </a-descriptions-item>
          <a-descriptions-item label="运行效率">
             <a-progress :percent="aiResult.breakdown?.efficiency / 100" status="warning" :show-text="false" style="width: 100px; margin-right: 10px;" />
             <strong>{{ aiResult.breakdown?.efficiency }}</strong> / 100
          </a-descriptions-item>
          <a-descriptions-item label="代码可读性">
             <a-progress :percent="aiResult.breakdown?.readability / 100" status="info" :show-text="false" style="width: 100px; margin-right: 10px;" />
             <strong>{{ aiResult.breakdown?.readability }}</strong> / 100
          </a-descriptions-item>
        </a-descriptions>
        <a-row :gutter="20">
          <a-col :span="12">
            <h4 style="color: #00b42a; margin: 10px 0;">👍 优点</h4>
            <ul style="padding-left: 20px; color: #4e5969;">
              <li v-for="(item, i) in aiResult.strengths" :key="'s'+i">{{ item }}</li>
            </ul>
          </a-col>
          <a-col :span="12">
            <h4 style="color: #f53f3f; margin: 10px 0;">👎 不足</h4>
            <ul style="padding-left: 20px; color: #4e5969;">
              <li v-for="(item, i) in aiResult.weaknesses" :key="'w'+i">{{ item }}</li>
            </ul>
          </a-col>
        </a-row>
        <a-divider />
        <div>
          <h4 style="color: #ff7d00; margin: 10px 0;">💡 改进建议</h4>
          <a-list size="small" :split="false">
             <a-list-item v-for="(suggestion, i) in aiResult.suggestions" :key="'sg'+i">{{ i + 1 }}. {{ suggestion }}</a-list-item>
          </a-list>
        </div>
      </div>
    </a-modal>
    </div>
  </div>
</template>

<script src="./SmartGrader.js"></script>

<style scoped src="./SmartGrader.css"></style>>