
# 自动批改C++作业系统 — 更新后 API 接口文档

> 路由前缀：所有接口以 `/api` 为前缀。  
> HTTP 响应统一返回状态码 `200`，业务成功/失败由响应体内的 `code` 字段表示。  
>
> **业务 code 含义**：
> - `0` — SuccessCode（成功）
> - `1001` — FailValidCode（参数校验失败）
> - `1002` — FailServiceCode（服务异常）
>
> **全局响应结构**（HTTP 200）
> ```json
> {
>   "code": int,
>   "message": string,
>   "data": object | null
> }
> ```
>
> 注意：本次文档已按用户要求修改：
> - **OCR 接口**：必须能接收上传的图片（multipart/form-data 或 Base64 JSON），并返回 `recognizedCode`（OCR 识别到的源代码文本）。
> - **编译并运行接口**：要求请求中提供 `recognizedCode`（OCR 的识别结果），以此为输入进行编译和运行。
> - **生成并持久化评分报告接口**：要求请求中提供 `recognizedCode` 与 `compileResult`（编译并运行的返回结果对象）。`compileResult` 示例见下方，并作为参考字段说明使用。
>
---

## 接口总览（最小核心集合）
1. `POST /api/assignments` — 上传作业（Create assignment）  
2. `POST /api/assignments/{assignmentId}/ocr` — OCR 识别（接收图片并返回 recognizedCode）  
3. `POST /api/assignments/{assignmentId}/compile` — 编译并运行（要求请求体包含 recognizedCode）  
4. `POST /api/assignments/{assignmentId}/report` — 生成并持久化评分报告（请求体包含 recognizedCode 与 compileResult）

---

# 1. 上传作业（Create assignment）

- **方法 / 路径**：`POST /api/assignments`  
- **用途**：上传作业文件（图片或源码文件），服务端存储并返回 `assignmentId` 供后续处理使用。

### 支持的上传方式（任选其一）
1. `multipart/form-data` 上传文件（推荐用于图片）  
   - 字段：
     - `file` — 文件二进制（必填）
     - `fileName` — 可选，文件名（若不提供由服务端生成）
2. `application/json`（Base64）  
   - JSON 字段：
     - `fileName` (`string`, 必填) — 文件名（含后缀）
     - `fileContentBase64` (`string`, 必填) — 文件内容的 Base64 编码

### 响应（HTTP 200）
成功时 `data` 字段包含：
- `assignmentId` (`string`) — 系统生成的唯一作业 ID
- `fileName` (`string`) — 回显上传的文件名
- `storedAt` (`string`) — 资源存储路径或文件 URL（可选）

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "assignmentId": "abcd1234",
    "fileName": "homework1.jpg",
    "storedAt": "/files/abcd1234/homework1.jpg"
  }
}
```

---

# 2. OCR 识别（OCR 接口：必须接收上传图片）

- **方法 / 路径**：`POST /api/assignments/{assignmentId}/ocr`  
- **用途**：对指定 `assignmentId` 的上传文件执行 OCR，返回识别到的源代码文本 `recognizedCode`。**此接口必须能够接收图片上传（multipart/form-data）或使用已上传 assignmentId 对应的文件进行 OCR。**

### 路径参数
- `assignmentId` (`string`) — 由上传接口返回的作业 ID。

### 请求方式（任选其一）
1. **通过 assignmentId 使用服务器已存文件（最常用）**  
   - 无请求体（服务器从存储读取 assignmentId 对应的文件并 OCR）。
2. **直接上传图片并即时 OCR（multipart/form-data）**  
   - 字段：
     - `file` (`file`, 必填) — 要 OCR 的图片文件（如 jpg/png）。
     - `fileName` (`string`, 可选) — 文件名。
3. **Base64 JSON（备用）**  
   - JSON 字段：
     - `fileName` (`string`, 必填)
     - `fileContentBase64` (`string`, 必填）

> **重要**：OCR 结果会作为 `recognizedCode` 返回，同时会被保存在服务端与该 `assignmentId` 关联，供后续 `compile` 与 `report` 接口使用。

### 响应（HTTP 200）
成功返回：
- `data.recognizedCode` (`string`) — OCR 识别到的源代码文本（包含换行符）。

示例：
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "recognizedCode": "#include <iostream>\nusing namespace std;\nint main() { cout << \"Hello, World!\" << endl; return 0; }\n"
  }
}
```

---

# 3. 编译并运行（Compile & Run — 要求请求体包含 recognizedCode）

- **方法 / 路径**：`POST /api/assignments/{assignmentId}/compile`  
- **用途**：对提交的源代码（通过 `recognizedCode` 提供）进行编译并运行（支持超时时间、内存限制等配置），返回编译与运行的元数据与输出。

### 路径参数
- `assignmentId` (`string`) — 作业 ID。

### 请求 JSON 字段（**必填**）
> 编译接口**必须**从请求体获取 `recognizedCode`（即 OCR 的识别结果）作为编译输入：
- `recognizedCode` (`string`, 必填) — 要编译运行的源代码文本（UTF-8）。
- `language` (`string`, 可选，默认 "C++") — 源语言标识。
- `timeoutSeconds` (`int`, 可选) — 运行超时时间（秒）。
- `memoryLimitMB` (`int`, 可选) — 内存限制（MB）。
- `runArgs` (`string[]`, 可选) — 程序运行时的命令行参数。

### 响应 JSON 字段（HTTP 200）
`data` 对象包含以下字段（与原文档保持一致并严格化）：

| 字段 | 类型 | 说明 |
|---|---:|---|
| `language` | `string` | 语言，例如 `"C++"`。 |
| `codeLengthBytes` | `int` | 源代码长度（字节）。 |
| `submitTime` | `string` | 提交时间（格式 `YYYY-MM-DD HH:mm:ss`）。 |
| `evalTime` | `string` | 评测时间（格式 `YYYY-MM-DD HH:mm:ss`）。 |
| `compileSuccess` | `boolean` | 编译是否成功。 |
| `output` | `string` 或 `null` | 程序标准输出（若有）。 |
| `error` | `string` 或 `null` | 编译或运行错误信息（若有）。 |
| `score` | `int` | 编译阶段即时分（默认 0，最终分由评分流程覆盖）。 |

#### 成功示例（编译并运行成功）
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

#### 编译失败示例
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

# 4. 生成并持久化评分报告（Write & Save report — 请求需包含 recognizedCode 与 compileResult）

- **方法 / 路径**：`POST /api/assignments/{assignmentId}/report`  
- **用途**：触发评分流程（规则评分 + LLM 或其他评分器），生成结构化评分报告并写入数据库。**此接口要求请求体中提供 OCR 识别的 `recognizedCode` 与 `compileResult`（即编译并运行的返回结果）作为输入来源，以保证评分结果可复现与审计。**

### 路径参数
- `assignmentId` (`string`) — 作业 ID。

### 请求 JSON 字段（**必填**）
- `recognizedCode` (`string`, 必填) — OCR 识别到的源代码文本（UTF-8）。
- `compileResult` (`object`, 必填) — 来自 `/compile` 接口或本地执行器的编译运行结果对象，结构如下（与上文 `compile` 响应中 `data` 部分一致）：
  - `language` (`string`)
  - `codeLengthBytes` (`int`)
  - `submitTime` (`string`, `YYYY-MM-DD HH:mm:ss`)
  - `evalTime` (`string`, `YYYY-MM-DD HH:mm:ss`)
  - `compileSuccess` (`boolean`)
  - `output` (`string` 或 `null`)
  - `error` (`string` 或 `null`)
  - `score` (`int`)
- `originalFile` (`object`, 可选) — 若需要，在评分报告中附带上传原图或文件信息：
  - `fileName` (`string`)
  - `fileContentBase64` (`string`) 或 `fileUrl` (`string`)（建议使用 `fileUrl` 避免响应过大）
- `forceRegenerate` (`boolean`, 可选) — 是否强制重新生成并覆盖已有报告（默认 `false`）

### 返回（HTTP 200）
`data` 为已生成并持久化的评分报告对象，包含（示例）：

- `assignmentId` (`string`)
- `score` (`int`) — 最终评分（例如 0-100）
- `breakdown` (`object`) — 分项得分，如 correctness、standardization、efficiency、readability
- `reason` (`string`) — 评分摘要/原因
- `suggestions` (`string[]`)
- `strengths` (`string[]`)
- `weaknesses` (`string[]`)
- `recognizedCode` (`string`) — 嵌入报告的识别代码
- `compileResult` (`object`) — 原样存储的编译运行结果（同请求）
- `originalFile` (`object`) — 上传文件信息或文件 URL（若提供）
- `generatedAt` (`string`) — 报告生成时间（格式 `YYYY-MM-DD HH:mm:ss`）

#### 成功示例（包含你给出的 compileResult 示例）
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
    "reason": "代码基本实现了栈的基本功能，但存在若干风格和边界条件问题，建议改进。",
    "suggestions": [
      "使用固定大小数组以匹配题目要求。",
      "增加错误处理与边界条件检测。"
    ],
    "strengths": ["实现了基本功能", "逻辑清晰"],
    "weaknesses": ["边界检查不全", "代码注释不足"],
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
      "fileUrl": "/files/abcd1234/homework1.jpg"
    },
    "generatedAt": "2025-10-24 21:40:05"
  }
}
```

---

# 5. 错误码与常见问题

- `1001 参数校验失败`：常见原因：请求缺少 `recognizedCode`／`compileResult`，或时间格式不符合 `YYYY-MM-DD HH:mm:ss`。
- `1002 服务异常`：评分服务超时、OCR 服务不可用、编译沙箱故障等。

---

# 6. 安全与实现建议（非接口规范，但强烈建议）
1. **OCR 输入校验**：对图片大小、分辨率与格式做限制（例如最大 8MB，支持 jpg/png），并对 base64 长度进行限制。
2. **Sandbox 编译执行**：必须在隔离沙箱中执行用户代码（容器、chroot、seccomp、资源 cgroup 限制），避免任意代码执行导致服务器被攻破。
3. **复现性记录**：将 `recognizedCode`、`compileResult` 与 `originalFile` 做长期存档以支持争议复核与审计。
4. **响应体大小控制**：报告中不建议直接保存大量 base64 内容，优先使用文件存储并返回 `fileUrl`。
5. **版本与语言扩展**：`language` 字段保留以便后续支持多语言（如 Python、Java 等）。

---

# 7. 变更记录
- 2025-10-26：按照需求修改：
  - OCR 接口明确支持接收上传图片（multipart/form-data 或 Base64）。
  - 编译接口强制从请求体读取 `recognizedCode`。
  - 评分报告接口强制要求 `recognizedCode` 与 `compileResult` 作为输入以保证可复现性。

---
