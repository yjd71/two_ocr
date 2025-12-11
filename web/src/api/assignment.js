// src/api/assignment.js
import request from './index.js'
/**
 * 1. 上传单个作业批次 (包含多张图片)
 * 对应 md 文档: POST /api/assignments_batches
 * @param {FormData} formData - 包含 files (File[]) 和 title
 */
export const uploadAssignmentBatchAPI = async (formData) => {
  // 注意：这里使用 fetch 以便更好控制 FormData，或者保持统一用 request (axios)
  // 如果用 axios，Content-Type 设为 'multipart/form-data' 即可
  const response = await fetch('/api/assignments_batches', {
    method: 'POST',
    body: formData, 
  });
  return response.json();
};

/**
 * 2. 识别单份作业批次 (多图)
 * 对应 md 文档: POST /api/assignments_batches/{assignmentId}/ocr
 * @param {String|Number} assignmentId 
 * @param {String} type - 'standard' | 'deep'
 */
export const ocrBatchRequestAPI = (assignmentId, type = 'standard') => {
  const url = type === 'deep' 
    ? `/assignments_batches/${assignmentId}/deepseek_ocr`
    : `/assignments_batches/${assignmentId}/ocr`;
    
  return request({
    url: url,
    method: 'post'
  })
}
/**
 * 上传作业文件
 * @param {FormData} formData - 包含文件的 FormData 对象
 */
export const UploadAssignmentAPI = async (formData) => {
  const response = await fetch('/api/assignments', {
    method: 'POST',
    body: formData, // fetch 会自动设置 Content-Type 为 multipart/form-data
  });
  return response.json();
};

/**
 * 1. 普通 OCR 识别 (智能识别)
 * @param {String} assignmentId 
 */
export const ocrRequestAPI = (assignmentId) => {
  return request({
    url: `/assignments/${assignmentId}/ocr`,
    method: 'post',
    // headers: { 'Content-Type': 'application/json' } // axios 默认就是 json，可省略
  })
}

/**
 * 2.  新增：DeepSeek 深度识别
 * @param {String} assignmentId 
 */
export const deepseekOcrRequestAPI = (assignmentId) => {
  return request({
    url: `/assignments/${assignmentId}/deepseek_ocr`,
    method: 'post'
  })
}

/**
 * 编译并运行代码
 * @param {String} assignmentId - 作业ID
 */
export const compileRequestAPI = async (assignmentId) => {
  const response = await fetch(`/api/assignments/${assignmentId}/Compile_run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response.json();
};

/**
 * 生成 AI 评分报告
 * @param {String} assignmentId - 作业ID
 */
export const generateReportAPI = async (assignmentId) => {
  const response = await fetch(`/api/assignments/${assignmentId}/report`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response.json();
};
// ==========================================
//     任务管理页新增的接口
// ==========================================

/**
 * 5. 批量删除作业
 * @param {Array} assignmentIds 
 */
export const deleteAssignmentsAPI = (assignmentIds) => {
  return request({
    url: '/assignments',
    method: 'delete',
    data: { assignmentIds }
  })
}

/**
 * 6. 查看单个作业详情 (包含所有结果)
 * @param {String|Number} assignmentId 
 */
export const getAssignmentDetailAPI = (assignmentId) => {
  return request({
    url: `/assignments/${assignmentId}`,
    method: 'get'
  })
}

/**
 * 7. 批量查看作业列表 (支持分页、模糊搜索、排序)
 * @param {Object} params - { page, pageSize, key, sortBy, sortOrder }
 */
export const getAssignmentListAPI = (params) => {
  return request({
    url: '/assignments',
    method: 'get',
    params: params // axios 会自动把对象转为 ?page=1&key=xxx
  })
}