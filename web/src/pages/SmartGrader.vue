<template>
  <div class="page-background">
    <div class="grader-container">
      <a-row :gutter="40" class="main-row">
        
        <a-col :span="12" style="height: 100%">
          <a-card class="styled-card left-card" :bordered="false">
            <template #title>
              <div class="card-title"><span class="title-icon">📂</span> 作业管理中心</div>
            </template>

            <div class="toolbar-row">
              <div class="status-text">
                <span v-if="assignmentList.length > 0">已就绪: <b>{{ assignmentList.length }}</b> 份</span>
                <span v-else class="text-gray">支持单图或批量上传</span>
              </div>
              <div class="action-group">
                <a-button type="primary" status="success" size="small" @click="openBatchMode">
                  <template #icon><icon-folder-add /></template> 批量上传
                </a-button>
              </div>
            </div>

            <div class="card-content-area">
              <div v-if="mode === 'list' && assignmentList.length > 0" class="file-list-view">
                <div class="scrollable-list">
                  <div 
                    v-for="item in assignmentList" 
                    :key="item.assignmentId" 
                    class="file-list-item animate-in"
                    :class="{ 
                      active: currentAssignment?.assignmentId === item.assignmentId,
                      'is-loading': item.status === 'loading'
                    }"
                    @click="selectAssignment(item)"
                  >
                    <div class="item-icon">
                      <icon-loading v-if="item.status === 'loading'" spin style="color: #165dff"/>
                      <icon-check-circle v-else-if="item.status === 'success'" style="color: #00b42a"/>
                      <icon-close-circle v-else-if="item.status === 'error'" style="color: #f53f3f"/>
                      <icon-file-image v-else />
                    </div>
                    
                    <div class="item-info">
                      <div class="item-title">{{ item.title }}</div>
                      <div class="item-desc">
                        ID: {{ item.assignmentId }} | {{ item.imageCount }} 张图片
                        <span v-if="item.status === 'loading'" style="color: #165dff; margin-left: 8px;">(处理中...)</span>
                      </div>
                    </div>
                    <div class="item-arrow"><icon-right /></div>
                  </div>
                </div>
                <div class="list-footer-add">
                  <a-upload :custom-request="customUploadRequest" :show-file-list="false">
                    <template #upload-button><a-button long dashed><icon-plus /> 快速上传单份作业</a-button></template>
                  </a-upload>
                </div>
              </div>

              <div v-else class="upload-wrapper-layer">
                <div v-if="assignmentList.length > 0" class="back-floater" @click.stop="mode = 'list'">
                  <icon-arrow-left /> 返回列表
                </div>

                <div v-if="displayImageUrl" class="preview-btn" @click.stop="imagePreviewVisible = true">
                  <icon-eye />
                </div>
                <div v-if="displayImageUrl" class="delete-btn" @click.stop="handleDeleteCurrent">
                  <icon-delete />
                </div>

                <div class="visual-layer">
                  <div v-if="displayImageUrl" class="preview-mode">
                    <img :src="displayImageUrl" class="preview-img" />
                    <div v-if="currentAssignment && currentAssignment.imageCount > 1" class="pagination-pill">
                      <span @click.stop="prevImage"><icon-left /></span>
                      <span>{{ currentImageIndex + 1 }} / {{ currentAssignment.imageCount }}</span>
                      <span @click.stop="nextImage"><icon-right /></span>
                    </div>
                  </div>
                  <div v-else class="empty-mode">
                    <div class="dashed-border-box">
                      <div class="icon-bg"><icon-upload class="upload-icon" /></div>
                      <div class="upload-main-text">点击或拖拽上传作业图片</div>
                      <div class="upload-sub-text">支持 JPG, PNG, BMP 格式</div>
                    </div>
                  </div>
                </div>
                
                <a-upload v-if="!displayImageUrl" class="invisible-uploader" draggable :show-file-list="false" :custom-request="customUploadRequest" />
              </div>
            </div>
            
            <div class="left-footer">
               <a-dropdown @select="triggerIdentify" position="top" :disabled="assignmentList.length === 0">
                 <a-button type="primary" size="large" long class="action-btn-main" :loading="isGlobalLoading">
                    <template #icon><icon-scan /></template> 
                    {{ mode === 'list' && assignmentList.length > 1 ? `批量识别 (${assignmentList.length}份)` : '开始识别' }}
                    <icon-down style="margin-left: 8px"/>
                 </a-button>
                 <template #content>
                   <a-doption value="standard">⚡ 智能识别</a-doption>
                   <a-doption value="deep">🧠 深度识别</a-doption>
                 </template>
               </a-dropdown>
            </div>
          </a-card>
        </a-col>
  
        <a-col :span="12" style="height: 100%">
          <a-card class="styled-card right-card" :bordered="false">
            <template #title>
              <div class="card-title"><span class="title-icon">📊</span> 结果分析</div>
            </template>
            
            <div class="result-stream">
              <div v-if="!hasAnyResults && !isGlobalLoading && !ocrProgress.visible" class="empty-state">
                 <div class="empty-icon-bg"><icon-scan style="font-size: 32px; color: #c9cdd4;" /></div>
                 <p>请上传作业并点击“开始识别”</p>
              </div>

              <div v-else-if="mode === 'list'" class="batch-result-list">
                 <transition-group name="list-anim">
                   <div 
                      v-for="item in assignmentList" 
                      :key="item.assignmentId" 
                      v-show="item.results && item.results.code" 
                      class="result-card-wrapper"
                   >
                      <div class="result-card-header">
                        <span class="res-title">{{ item.title }}</span>
                        <a-tag v-if="item.results.ai?.score" color="green">{{ item.results.ai.score }}分</a-tag>
                        <a-tag v-else-if="item.results.code" color="blue">识别完成</a-tag>
                      </div>
                      <div class="res-row">
                         <span style="font-size:12px; color:#86909c">
                           状态: {{ item.results.ai ? 'AI批改完成' : (item.results.compile ? '编译完成' : 'OCR完成') }}
                         </span>
                         <a-button type="text" size="mini" @click="selectAssignment(item)">查看详情 <icon-right/></a-button>
                      </div>
                   </div>
                 </transition-group>
              </div>

              <div v-else-if="currentAssignment" class="single-detail-stream">
                <div v-if="ocrProgress.visible" class="progress-card animate-in">
                  <div class="progress-header"><span class="loading-text">🔄 识别中...</span><span class="percentage">{{ Math.round(ocrProgress.percent) }}%</span></div>
                  <a-progress :percent="ocrProgress.percent/100" status="active" :show-text="false" />
                </div>
                
                <div v-if="currentAssignment.results?.code" class="result-item animate-in">
                  <a-alert type="success" :show-icon="false" class="styled-alert">
                    <div class="alert-content"><span>✅ 识别成功</span><a-button type="text" size="small" @click="showCodeModal(currentAssignment.results.code)">查看代码</a-button></div>
                  </a-alert>
                </div>

                <div v-if="compileProgress.visible" class="progress-card animate-in">
                   <div class="progress-header"><span class="loading-text">⚡ 正在编译...</span></div>
                   <a-progress :percent="compileProgress.percent/100" status="warning" :show-text="false" />
                </div>

                <div v-if="currentAssignment.results?.compile" class="result-item animate-in">
                  <a-alert :type="currentAssignment.results.compile.compileSuccess ? 'success' : 'error'" :show-icon="false" class="styled-alert">
                    <div class="alert-content">
                      <span>{{ currentAssignment.results.compile.compileSuccess ? '✅ 编译成功' : '❌ 编译失败' }}</span>
                      <a-button type="text" size="small" @click="showCompileModal(currentAssignment.results.compile)">详情</a-button>
                    </div>
                  </a-alert>
                </div>

                <div v-if="aiProgress.visible" class="progress-card animate-in">
                   <div class="progress-header"><span class="loading-text">🤖 AI 正在批改...</span></div>
                   <a-progress :percent="aiProgress.percent/100" status="success" :show-text="false" />
                </div>

                <div v-if="currentAssignment.results?.ai" class="result-item animate-in">
                  <a-alert type="success" :show-icon="false" class="styled-alert">
                    <div class="alert-content">
                      <span>🤖 AI 批改完成 (得分: {{ currentAssignment.results.ai.score }})</span>
                      <a-button type="text" size="small" @click="showAiModal(currentAssignment.results.ai)">查看报告</a-button>
                    </div>
                  </a-alert>
                </div>
              </div>
            </div>
            
            <div class="right-footer-actions">
              <a-space size="large">
                <a-button type="primary" status="success" shape="round" @click="triggerCompile" :loading="isGlobalLoading" :disabled="mode === 'single' ? !canOperateCurrent : !hasAnyResults"><template #icon><icon-play-circle /></template> 编译运行</a-button>
                <a-button type="primary" status="warning" shape="round" @click="triggerAi" :loading="isGlobalLoading" :disabled="mode === 'single' ? !canOperateCurrent : !hasAnyResults"><template #icon><icon-robot /></template> AI 批改</a-button>
              </a-space>
            </div>
          </a-card>
        </a-col>
      </a-row>

      <a-image-preview :src="displayImageUrl" v-model:visible="imagePreviewVisible" />
    <a-modal v-model:visible="modals.code" title="📄 代码识别结果" width="700px" :footer="false">
        <div class="code-box">
          <a-textarea v-model="modalData" :auto-size="{ minRows: 10, maxRows: 25 }" readonly />
        </div>
      </a-modal>      
<a-modal v-model:visible="modals.run" title="🖥️ 编译运行详情" width="700px" :footer="false">
        <div v-if="currentCompileInfo">
          <a-descriptions :column="2" bordered size="small" layout="inline-horizontal" style="margin-bottom: 20px">
            <a-descriptions-item label="运行状态">
              <a-tag :color="currentCompileInfo.compileSuccess ? 'green' : 'red'">
                {{ currentCompileInfo.compileSuccess ? '✅ 编译成功' : '❌ 编译失败' }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="编程语言">{{ currentCompileInfo.language || 'C++' }}</a-descriptions-item>
            <a-descriptions-item label="评测耗时">{{ currentCompileInfo.evalTime || '0ms' }}</a-descriptions-item>
            <a-descriptions-item label="代码长度">{{ currentCompileInfo.codeLengthBytes || 0 }} Bytes</a-descriptions-item>
          </a-descriptions>
          <div style="font-weight:bold; margin-bottom:8px; color:#1d2129;">终端输出 (Output / Error):</div>
          <div class="terminal-box" :class="{ 'is-error': !currentCompileInfo.compileSuccess }">
            {{ currentCompileInfo.output || currentCompileInfo.error || '无输出' }}
          </div>
        </div>
      </a-modal>      
    <a-modal v-model:visible="modals.ai" title="🧠 AI 智能批改报告" width="800px" :footer="false">
        <div v-if="currentAiResult" class="ai-report-container">
           <a-alert type="success" :show-icon="false" style="margin-bottom:20px; border-radius:8px">
             <a-row align="middle" :gutter="24">
                <a-col :span="5" style="text-align: center; border-right: 1px solid #e5e6eb;">
                  <div style="font-size: 13px; color: #86909c;">综合得分</div>
                  <div style="font-size: 38px; font-weight: bold; color: #00b42a; line-height:1;">
                    {{ currentAiResult.score }}
                  </div>
                </a-col>
                <a-col :span="19">
                  <div style="font-weight: bold; margin-bottom: 6px;">综合评语</div>
                  <div style="color: #4e5969; font-size: 13px;">{{ currentAiResult.comment }}</div>
                </a-col>
             </a-row>
           </a-alert>

           <a-descriptions title="📊 维度分析" :column="2" bordered size="small">
              <a-descriptions-item label="正确性">
                 <a-progress :percent="(currentAiResult.breakdown?.correctness || 0)/100" status="success" style="width: 80px"/>
                 <span style="margin-left:8px; font-weight:bold">{{ currentAiResult.breakdown?.correctness }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="规范性">
                 <a-progress :percent="(currentAiResult.breakdown?.standardization || 0)/100" status="normal" style="width: 80px"/>
                 <span style="margin-left:8px; font-weight:bold">{{ currentAiResult.breakdown?.standardization }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="效率">
                 <a-progress :percent="(currentAiResult.breakdown?.efficiency || 0)/100" status="warning" style="width: 80px"/>
                 <span style="margin-left:8px; font-weight:bold">{{ currentAiResult.breakdown?.efficiency }}</span>
              </a-descriptions-item>
              <a-descriptions-item label="可读性">
                 <a-progress :percent="(currentAiResult.breakdown?.readability || 0)/100" status="info" style="width: 80px"/>
                 <span style="margin-left:8px; font-weight:bold">{{ currentAiResult.breakdown?.readability }}</span>
              </a-descriptions-item>
           </a-descriptions>

           <div class="feedback-grid">
             <div class="feedback-card pros">
               <div class="feedback-header" style="color: #00b42a;"><icon-thumb-up-fill /> 亮点</div>
               <ul class="feedback-list">
                 <li v-for="(s, i) in currentAiResult.strengths" :key="'s'+i">{{ s }}</li>
                 <li v-if="!currentAiResult.strengths?.length" style="color:#aaa">暂无明显亮点</li>
               </ul>
             </div>
             <div class="feedback-card cons">
               <div class="feedback-header" style="color: #f53f3f;"><icon-thumb-down-fill /> 不足</div>
               <ul class="feedback-list">
                 <li v-for="(w, i) in currentAiResult.weaknesses" :key="'w'+i">{{ w }}</li>
                 <li v-if="!currentAiResult.weaknesses?.length" style="color:#aaa">暂无明显不足</li>
               </ul>
             </div>
           </div>
           
           <div class="suggestion-box" style="margin-top:15px">
             <div class="suggestion-title"><icon-bulb /> 建议</div>
             <div class="suggestion-item" v-for="(s, i) in currentAiResult.suggestions" :key="i">
               <div class="idx-badge">{{ i+1 }}</div>
               <div>{{ s }}</div>
             </div>
           </div>
        </div>
      </a-modal>

    </div>
  </div>
</template>

<script>
import Logic from './SmartGrader.js'
// 不再引入 BatchUpload
export default { ...Logic }

</script>

<style scoped src="./SmartGrader.css"></style>