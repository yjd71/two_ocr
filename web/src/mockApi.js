// mockApi.js
// 模拟上传作业接口，接收 formData 参数
export const mockUploadAssignment = (formData) => {
  return new Promise((resolve, reject) => {
    // 模拟从 formData 中提取文件
    const file = formData.get('file');  // 获取 formData 中的文件对象

    setTimeout(() => {
      if (file) {
        resolve({
          code: 0,
          message: '成功',
          data: {
            assignmentId: 'abcd1234',  // 模拟返回的作业ID
            fileName: file.name,  // 模拟返回的文件名
          }
        });
      } else {
        resolve({
          code: 1001,
          message: '参数校验失败',
          data: null,
        });
      }
    }, 1000);  // 模拟延时1秒
  });
};

// 模拟 OCR 识别接口
export const mockOCRRecognition = (assignmentId) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (assignmentId) {
        resolve({
          code: 0,
          message: '成功',
          data: {
            recognizedCode: `#include <iostream>
              using namespace std;

  int main() {
    // OCR 识别的代码
    cout << "Hello World!" << endl;
    return 0;
}`
          }
        })
      } else {
        reject({
          code: 1001,
          message: '作业 ID 无效',
          data: null
        })
      }
    }, 1000)  // 模拟 OCR 识别延迟
  })
}

// 模拟运行代码接口
export const mockRunCode = (assignmentId, code) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (code && assignmentId) {
        resolve({
          code: 0,
          message: '成功',
          data: {
            language: 'C++',
            codeLengthBytes: code.length,
            compileSuccess: true,
            output: 'Hello, World!\n', // 模拟输出
            error: null,
            score: 0 // 模拟即时分数
          }
        })
      } else {
        reject({
          code: 1002,
          message: '代码运行失败',
          data: null
        })
      }
    }, 1500)  // 模拟运行时间
  })
}

// 模拟生成评分报告接口
export const mockGenerateReport = (assignmentId) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (assignmentId) {
        resolve({
          code: 0,
          message: '成功',
          data: {
            assignmentId: 'abcd1234',
            score: 90,
            breakdown: {
              correctness: 55,
              standardization: 20,
              efficiency: 10,
              readability: 5
            },
            reason: '代码实现基本功能，但使用了不符合题意的数据结构。',
            suggestions: ['改用固定大小数组以符合题目要求'],
            strengths: ['基本功能实现完整'],
            weaknesses: ['不符合题目要求的实现方式'],
            recognizedCode: '#include <iostream>...',
            compileResult: {
              language: 'C++',
              codeLengthBytes: 102,
              submitTime: '2025-10-24 21:39:50',
              evalTime: '2025-10-24 21:39:50',
              compileSuccess: true,
              output: 'Hello, World!\n',
              error: null,
              score: 0
            },
            originalFile: {
              fileName: 'homework1.jpg',
              fileContentBase64: 'base64string'
            },
            generatedAt: '2025-10-24 21:40:05'
          }
        })
      } else {
        reject({
          code: 1001,
          message: '参数校验失败',
          data: null
        })
      }
    }, 1500)  // 模拟生成报告延迟
  })
}
