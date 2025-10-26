
# 自动批改C++作业系统 — 核心 API 接口文档

> 路由前缀：所有接口以 `/api` 为前缀。  
> HTTP 响应统一返回状态码 `200`，业务成功/失败由响应体内的 `code` 字段表示。  
>
> **业务 code 含义**：
> - `0` — SuccessCode（成功）
> - `1001` — FailValidCode（参数校验失败）
> - `1002` — FailServiceCode（服务异常）
>
> **全局响应结构**：
> ```json
> {
>   "code": int,
>   "message": string,
>   "data": object | null
> }
> ```
>
> 对应 message（自动映射）：
> - `0` -> "成功"  
> - `1001` -> "参数校验失败"  
> - `1002` -> "服务异常"

---

## 接口概览（最小核心集合）
1. `POST /api/assignments` — 上传作业（Create assignment）  
2. `POST /api/assignments/{assignmentId}/ocr` — OCR 识别（Trigger OCR / 获取识别文本）  
3. `POST /api/assignments/{assignmentId}/compile` — 编译并运行（Compile & Run）  
4. `POST /api/assignments/{assignmentId}/report` — 生成并持久化评分报告（Write & Save report）
---

# 1. 上传作业（Create assignment）

- **方法 / 路径**：`POST /api/assignments`  
- **用途**：上传作业文件（支持图片或源码文件），服务端存储并返回 `assignmentId` 供后续处理使用。

### 请求 JSON 字段
| 字段 | 类型 | 必填 | 说明 |
|---|---:|:---:|---|
| `fileName` | `string` | 是 | 文件名（含后缀），例如 `"homework1.jpg"` 或 `"solution.cpp"`。 |
| `fileContent` | `string` | 是 | 文件内容的 Base64 编码字符串。若文件过大建议使用文件 URL（扩展）。 |

### 响应 JSON 字段（HTTP 200）
| 字段 | 类型 | 说明 |
|---|---:|---|
| `code` | `int` | 业务状态码（见全局约定）。 |
| `message` | `string` | 状态描述（由 code 对应）。 |
| `data` | `object` 或 `null` | 成功时包含： |
| `data.assignmentId` | `string` | 系统生成的唯一作业 ID。 |
| `data.fileName` | `string` | 回显上传的文件名。 |

### 成功示例
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "assignmentId": "abcd1234",
    "fileName": "homework1.jpg"
  }
}
```

### 参数校验失败示例
```json
{
  "code": 1001,
  "message": "参数校验失败",
  "data": null
}
```

---

# 2. OCR 识别（PaddleOCR / 获取识别文本）

- **方法 / 路径**：`POST /api/assignments/{assignmentId}/ocr`  
- **用途**：对指定 `assignmentId` 的上传文件执行 OCR，返回识别到的 C++ 源代码文本（同步模式）。

### 路径参数
| 参数 | 类型 | 说明 |
|---|---:|---|
| `assignmentId` | `string` | 由上传接口返回的作业 ID。 |

### 请求 JSON 字段
- 无（URL 指定 `assignmentId`）。可扩展为可选字段 `overrideCode`（用于覆盖 OCR 结果）。

### 响应 JSON 字段（HTTP 200）
| 字段 | 类型 | 说明 |
|---|---:|---|
| `code` | `int` | 业务状态码。 |
| `message` | `string` | 状态描述。 |
| `data` | `object` 或 `null` | 包含： |
| `data.recognizedCode` | `string` | OCR 识别到的源代码文本（含换行符）。 |

### 成功示例
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "recognizedCode": "#include <iostream>\nusing namespace std;\nint main() { /* ... */ }\n"
  }
}
```

---

# 3. 编译并运行（Compile & Run）

- **方法 / 路径**：`POST /api/assignments/{assignmentId}/compile`  
- **用途**：对 `assignmentId` 的代码（OCR 得到或上传的源文件）进行编译并运行测试用例，返回编译/运行信息与基础元数据。

### 路径参数
| 参数 | 类型 | 说明 |
|---|---:|---|
| `assignmentId` | `string` | 作业 ID。 |

### 请求 JSON 字段
- 无（可扩展至运行配置，如超时、内存限制，但此处保持最小）。

### 响应 JSON 字段（HTTP 200）
| 字段 | 类型 | 说明 |
|---|---:|---|
| `code` | `int` | 业务状态码（0 表示请求处理成功）。 |
| `message` | `string` | 状态描述。 |
| `data` | `object` 或 `null` | 编译结果对象，包含： |
| `data.language` | `string` | 语言，例如 `"C++"`。 |
| `data.codeLengthBytes` | `int` | 源代码长度（字节）。 |
| `data.submitTime` | `string` | 提交时间（格式 `YYYY-MM-DD HH:mm:ss`）。 |
| `data.evalTime` | `string` | 评测时间（格式 `YYYY-MM-DD HH:mm:ss`）。 |
| `data.compileSuccess` | `boolean` | 编译是否成功。 |
| `data.output` | `string` 或 `null` | 程序标准输出（若有）。 |
| `data.error` | `string` 或 `null` | 编译或运行错误信息（若有）。 |
| `data.score` | `int` | 编译阶段即时分（可为 0，最终分由评分接口覆盖）。 |

### 成功示例（编译运行成功）
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "language": "C++",
    "codeLengthBytes": 102,
    "submitTime": "2025-10-24 21:39:50",
    "evalTime": "2025-10-24 21:39:50",
    "compileSuccess": true,
    "output": "Hello, World!\n",
    "error": null,
    "score": 0
  }
}
```

### 成功示例（编译失败）
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "language": "C++",
    "codeLengthBytes": 87,
    "submitTime": "2025-10-24 21:39:50",
    "evalTime": "2025-10-24 21:39:51",
    "compileSuccess": false,
    "output": null,
    "error": "main.cpp: error: expected ';' before 'return'",
    "score": 0
  }
}
```

---

# 4. 生成并持久化评分报告（Write & Save report）

- **方法 / 路径**：`POST /api/assignments/{assignmentId}/report`  
- **用途**：触发评分流程（规则评分 + LLM/DeepSeek 等），生成结构化评分报告并写入数据库。同步返回生成的完整报告（包含上传的原图或文件引用）。


### 路径参数
| 参数 | 类型 | 说明 |
|---|---:|---|
| `assignmentId` | `string` | 作业 ID。 |


### 响应 JSON 字段（HTTP 200）
| 字段 | 类型 | 说明 |
|---|---:|---|
| `code` | `int` | 业务状态码。 |
| `message` | `string` | 状态描述。 |
| `data` | `object` 或 `null` | 生成并保存的完整评分报告，包含： |

**`data`（评分报告）字段说明**

| 字段 | 类型 | 说明 |
|---|---:|---|
| `assignmentId` | `string` | 作业 ID。 |
| `score` | `int` | 最终评分（例如 0-100）。 |
| `breakdown` | `object` | 分项得分。 |
| `breakdown.correctness` | `int` | 正确性得分。 |
| `breakdown.standardization` | `int` | 规范化（代码风格）得分。 |
| `breakdown.efficiency` | `int` | 效率得分。 |
| `breakdown.readability` | `int` | 可读性得分。 |
| `reason` | `string` | 评分原因/摘要。 |
| `suggestions` | `string[]` | 改进建议列表。 |
| `strengths` | `string[]` | 优点列表。 |
| `weaknesses` | `string[]` | 缺点列表。 |
| `recognizedCode` | `string` | OCR 识别的代码文本（若有）。 |
| `compileResult` | `object` | 嵌套的编译执行结果（与编译接口返回格式一致）。 |
| `originalFile` | `object` | 上传文件信息： |
| `originalFile.fileName` | `string` | 上传的文件名。 |
| `originalFile.fileContentBase64` | `string` | 上传文件的 Base64 内容（建议：生产使用 fileUrl 替代以避免响应过大）。 |
| `generatedAt` | `string` | 报告生成时间（格式 `YYYY-MM-DD HH:mm:ss`）。 |

### 成功示例（参考截图结构）
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "assignmentId": "abcd1234",
    "score": 90,
    "breakdown": {
      "correctness": 55,
      "standardization": 20,
      "efficiency": 10,
      "readability": 5
    },
    "reason": "代码基本实现了栈的基本功能，包括push, pop, top, isEmpty和isFull。但是，使用vector而不是固定大小的数组，这与题的固定大小概念不符，可能导致maxSize限制不准确。此外，代码的可读性有待提高，例如函数命名和注释。",
    "suggestions": [
      "使用固定大小的数组或明确说明容量以保证题目要求的大小特性。",
      "改进函数命名和注释，提升代码的可读性。"
    ],
    "strengths": [
      "代码实现了栈的基本功能，包括push, pop, top, isEmpty和isFull。",
      "代码格式规范，命名清晰。"
    ],
    "weaknesses": [
      "使用vector而不是固定大小的数组，可能导致maxSize限制不准确。",
      "代码的可读性有待提高，例如函数命名和注释。"
    ],
    "recognizedCode": "#include <iostream> ...",
    "compileResult": {
      "language": "C++",
      "codeLengthBytes": 102,
      "submitTime": "2025-10-24 21:39:50",
      "evalTime": "2025-10-24 21:39:50",
      "compileSuccess": true,
      "output": "Hello, World!\n",
      "error": null,
      "score": 0
    },
    "originalFile": {
      "fileName": "homework1.jpg",
      "fileContentBase64": "<base64 string here>"
    },
    "generatedAt": "2025-10-24 21:40:05"
  }
}
```

### 参数校验失败示例
```json
{
  "code": 1001,
  "message": "参数校验失败",
  "data": null
}
```

### 服务异常示例
```json
{
  "code": 1002,
  "message": "服务异常",
  "data": {
    "detail": "评分服务调用超时"
  }
}
```
