// src/api/assignment.js
import request from './index.js'
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