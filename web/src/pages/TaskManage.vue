<template>
  <div class="page-background">
    <div class="grader-container">
      
      <a-card class="styled-card" :bordered="false">
        <template #title>
          <div class="card-title">
            <span class="title-icon">📋</span> 任务管理列表
          </div>
        </template>

        <div class="toolbar">
         <div class="search-area">
            <a-input v-model="searchForm.fileName" placeholder="请输入作业名搜索" style="width: 240px" allow-clear>
              <template #prefix><icon-search /></template>
            </a-input>
            <a-select v-model="searchForm.status" placeholder="作业状态" style="width: 160px" allow-clear>
              <a-option>上传成功</a-option>
              <a-option>识别成功</a-option>
              <a-option>识别失败</a-option>
              <a-option>编译成功</a-option>
              <a-option>编译失败</a-option>
              <a-option>已评分</a-option>
              <a-option>评分失败</a-option>
            </a-select>
            <a-button type="primary" @click="handleSearch">
              <template #icon><icon-search /></template> 查询
            </a-button>
            <a-button @click="handleReset">
              <template #icon><icon-refresh /></template> 重置
            </a-button>
            </div>
          <div class="sort-area">
            <span class="sort-label">排序方式：</span>
            <a-select v-model="queryParams.sortBy" style="width: 140px" @change="fetchData">
              <a-option value="createdAt">提交时间</a-option>
              <a-option value="score">总分</a-option>
            </a-select>
            <a-tooltip :content="queryParams.sortOrder === 'asc' ? '当前：升序' : '当前：降序'">
              <a-button class="sort-btn" @click="toggleSortOrder">
                <template #icon>
                  <icon-sort-ascending v-if="queryParams.sortOrder === 'asc'" />
                  <icon-sort-descending v-else />
                </template>
              </a-button>
            </a-tooltip>
          </div>
        </div>

        <a-table 
          :data="tableData" 
          :pagination="false" 
          :loading="loading"
          row-key="assignmentId"
          :bordered="false"
          :row-selection="rowSelection"
          v-model:selectedKeys="selectedKeys"
          :scroll="{ y: '100%' }"
          class="custom-table"
        >
          <template #columns>
            <a-table-column title="作业ID" data-index="assignmentId" :width="120" align="center" />
            <a-table-column title="作业名" data-index="fileName" align="center" ellipsis tooltip />
            <a-table-column title="状态" data-index="status" :width="140" align="center">
              <template #cell="{ record }">
                <a-tag :color="getStatusColor(record.status)" bordered>
                  {{ record.status || '未知' }}
                </a-tag>
              </template>
            </a-table-column>
            <a-table-column title="提交时间" data-index="createdAt" :width="180" align="center" />
            <a-table-column title="总分" data-index="score" :width="100" align="center">
              <template #cell="{ record }">
                <span v-if="record.score !== null" :class="getScoreClass(record.score)">
                  {{ record.score }}
                </span>
                <span v-else style="color: #c9cdd4">-</span>
              </template>
            </a-table-column>
            
            <a-table-column title="操作" :width="180" align="center">
              <template #cell="{ record }">
                <div style="display: flex; justify-content: center; gap: 8px;">
                  <a-dropdown @select="(val) => handlePreview(val, record)" position="bl">
                    <a-button type="outline" size="small" shape="round">
                      <span style="margin-right: 4px;">查看结果</span>
                      <icon-down />
                    </a-button>
                    <template #content>
                      <a-doption value="code"><icon-code style="margin-right:6px"/>识别代码</a-doption>
                      <a-doption value="run"><icon-computer style="margin-right:6px"/>运行报告</a-doption>
                      <a-doption value="ai"><icon-robot style="margin-right:6px"/>AI 批改</a-doption>
                    </template>
                  </a-dropdown>

                  <a-popconfirm content="确定删除该作业？" @ok="handleDelete([record.assignmentId])">
                    <a-button type="text" status="danger" size="small">
                      <template #icon><icon-delete /></template>
                    </a-button>
                  </a-popconfirm>
                </div>
              </template>
            </a-table-column>
          </template>
        </a-table>

        <div class="table-footer">
          <div class="batch-actions">
            <a-popconfirm :content="`确定删除选中的 ${selectedKeys.length} 项？`" @ok="handleBatchDelete" position="tr">
              <a-button status="danger" :disabled="selectedKeys.length === 0">
                <template #icon><icon-delete /></template> 删除所选
              </a-button>
            </a-popconfirm>
            <span class="selected-text" v-if="selectedKeys.length > 0">已选 {{ selectedKeys.length }} 项</span>
          </div>
          <a-pagination 
            :total="pagination.total" 
            :current="pagination.current" 
            :page-size="pagination.pageSize" 
            show-total show-jumper show-page-size
            @change="onPageChange" 
            @page-size-change="onPageSizeChange"
          />
        </div>
      </a-card>
    </div>

    <a-modal v-model:visible="modals.code" title="📄 代码识别结果" width="700px" :footer="false">
      <a-spin :loading="detailLoading" style="width: 100%">
        <div class="code-box">
          <a-textarea 
            v-model="currentDetail.code" 
            :auto-size="{ minRows: 10, maxRows: 25 }" 
            readonly 
            style="resize: none;"
          />
        </div>
      </a-spin>
    </a-modal>

    <a-modal v-model:visible="modals.run" title="🖥️ 编译运行详情" width="600px" :footer="false">
      <a-spin :loading="detailLoading" style="width: 100%">
        <div v-if="currentDetail.compileInfo">
          <a-descriptions :column="2" bordered size="small" layout="inline-horizontal" style="margin-bottom: 20px">
            <a-descriptions-item label="运行状态">
              <a-tag :color="currentDetail.compileInfo.compileSuccess ? 'green' : 'red'">
                {{ currentDetail.compileInfo.compileSuccess ? '✅ 编译成功' : '❌ 编译失败' }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="编程语言">{{ currentDetail.compileInfo.language }}</a-descriptions-item>
            <a-descriptions-item label="评测耗时">{{ currentDetail.compileInfo.evalTime || '0ms' }}</a-descriptions-item>
            <a-descriptions-item label="代码长度">{{ currentDetail.compileInfo.codeLengthBytes }} Bytes</a-descriptions-item>
            <a-descriptions-item label="提交时间" :span="2">{{ currentDetail.compileInfo.submitTime }}</a-descriptions-item>
          </a-descriptions>
          
          <div style="font-weight:bold; margin-bottom:8px; color:#1d2129;">终端输出 (Output / Error):</div>
          
          <div 
            class="terminal-box"
            :class="{ 'is-error': !currentDetail.compileInfo.compileSuccess }"
          >
            {{ 
              currentDetail.compileInfo.compileSuccess 
                ? (currentDetail.compileInfo.output || '无输出') 
                : (currentDetail.compileInfo.error || '编译失败，未返回详细错误信息') 
            }}
          </div>
        </div>
        <a-empty v-else description="暂无编译数据" />
      </a-spin>
    </a-modal>

    <a-modal v-model:visible="modals.ai" title="🧠 AI 智能批改报告" width="800px" :footer="false">
      <a-spin :loading="detailLoading" style="width: 100%">
        <div v-if="currentDetail.aiResult" class="ai-report-container">
          
          <a-alert type="success" :show-icon="false" style="border-radius: 8px;">
            <a-row align="middle" :gutter="24">
              <a-col :span="5" style="text-align: center; border-right: 1px solid #e5e6eb;">
                <div style="font-size: 13px; color: #86909c; margin-bottom: 4px;">综合得分</div>
                <div style="font-size: 38px; font-weight: bold; color: #00b42a; line-height:1;">
                  {{ currentDetail.aiResult.score }}
                </div>
              </a-col>
              <a-col :span="19">
                <div style="font-weight: bold; margin-bottom: 6px; font-size:15px;">综合评语</div>
                <div style="color: #4e5969; font-size: 13px; line-height: 1.5;">
                  {{ currentDetail.aiResult.comment }}
                </div>
              </a-col>
            </a-row>
          </a-alert>
          
          <div style="margin-top: 20px;">
            <a-descriptions title="📊 维度分析" :column="2" bordered size="small">
               <a-descriptions-item label="代码正确性">
                 <a-progress :percent="currentDetail.aiResult.breakdown?.correctness/100" status="success" style="width: 80px"/>
                 <span style="margin-left:8px; font-weight:bold">{{ currentDetail.aiResult.breakdown?.correctness }}</span>
               </a-descriptions-item>
               <a-descriptions-item label="代码规范性">
                 <a-progress :percent="currentDetail.aiResult.breakdown?.standardization/100" status="normal" style="width: 80px"/>
                 <span style="margin-left:8px; font-weight:bold">{{ currentDetail.aiResult.breakdown?.standardization }}</span>
               </a-descriptions-item>
               <a-descriptions-item label="运行效率">
                 <a-progress :percent="currentDetail.aiResult.breakdown?.efficiency/100" status="warning" style="width: 80px"/>
                 <span style="margin-left:8px; font-weight:bold">{{ currentDetail.aiResult.breakdown?.efficiency }}</span>
               </a-descriptions-item>
               <a-descriptions-item label="代码可读性">
                 <a-progress :percent="currentDetail.aiResult.breakdown?.readability/100" status="info" style="width: 80px"/>
                 <span style="margin-left:8px; font-weight:bold">{{ currentDetail.aiResult.breakdown?.readability }}</span>
               </a-descriptions-item>
            </a-descriptions>
          </div>

          <div class="feedback-grid">
            <div class="feedback-card pros">
              <div class="feedback-header" style="color: #00b42a;">
                <icon-thumb-up-fill /> 亮点 (Strengths)
              </div>
              <ul class="feedback-list">
                <li v-for="(item, i) in currentDetail.aiResult.strengths" :key="'s'+i">{{ item }}</li>
                <li v-if="!currentDetail.aiResult.strengths?.length" style="color:#aaa">暂无明显亮点</li>
              </ul>
            </div>
            <div class="feedback-card cons">
              <div class="feedback-header" style="color: #f53f3f;">
                <icon-thumb-down-fill /> 不足 (Weaknesses)
              </div>
              <ul class="feedback-list">
                <li v-for="(item, i) in currentDetail.aiResult.weaknesses" :key="'w'+i">{{ item }}</li>
                <li v-if="!currentDetail.aiResult.weaknesses?.length" style="color:#aaa">暂无明显不足</li>
              </ul>
            </div>
          </div>

          <div class="suggestion-box">
            <div class="suggestion-title"><icon-bulb /> 改进建议</div>
            <div class="suggestion-item" v-for="(s, i) in currentDetail.aiResult.suggestions" :key="i">
              <div class="idx-badge">{{ i+1 }}</div>
              <div>{{ s }}</div>
            </div>
          </div>

        </div>
        <a-empty v-else description="暂无 AI 评分数据" />
      </a-spin>
    </a-modal>
  </div>
</template>

<script src="./TaskManage.js"></script>
<style scoped src="./TaskManage.css"></style>