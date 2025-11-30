# 自动批改C++作业系统 — 新增删改查接口文档（详细字段说明）

> 路由前缀：所有接口以 `/api` 为前缀。  
> HTTP 响应统一返回状态码 `200`，业务成功/失败由响应体内的 `code` 字段表示。  
>
> **业务 code 含义**：
> - `0` — SuccessCode（成功）
> - `1001` — FailValidCode（参数校验失败）
> - `1002` — FailServiceCode（服务异常）
> - `1003` — ResourceNotFoundCode（资源不存在）
> - `1004` — InvalidParameterCode（参数无效）
>
> **全局响应结构**（HTTP 200）
> ```json
> {
>   "code": int,
>   "message": string,
>   "data": object | null
> }
> ```

---

## 接口总览（新增删改查接口）
1. `DELETE /api/assignments/{assignmentId}` — 删除单个作业（包括关联数据）
2. `DELETE /api/assignments` — 批量删除作业（包括关联数据）
3. `GET /api/assignments/{assignmentId}` — 查看单个作业（包括关联数据）
4. `GET /api/assignments` — 批量查看作业列表（包括关联数据）

---

# 1. 删除单个作业（Delete assignment）

- **方法 / 路径**：`DELETE /api/assignments/{assignmentId}`
- **用途**：删除指定 `assignmentId` 的作业，同时删除与之关联的OCR结果、编译结果、评分报告等数据。

### 路径参数
| 字段 | 类型    | 必填 | 说明 |
|------|-------|------|------|
| `assignmentId` | `int` | 是 | 要删除的作业唯一标识符 |

### 响应字段说明（HTTP 200）
| 字段 | 类型        | 说明 |
|------|-----------|------|
| `code` | `int`     | 业务状态码，0表示成功 |
| `message` | `string`  | 操作结果描述信息 |
| `data.deletedAssignmentId` | `int`     | 已删除的作业ID |
| `data.deletedRelatedRecords.ocrResults` | `boolean` | 是否成功删除关联的OCR结果 |
| `data.deletedRelatedRecords.compileResults` | `boolean` | 是否成功删除关联的编译结果 |
| `data.deletedRelatedRecords.reports` | `boolean` | 是否成功删除关联的评分报告 |

成功响应示例：
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "deletedAssignmentId": 1,
    "deletedRelatedRecords": {
      "ocrResults": true,
      "compileResults": true,
      "reports": true
    }
  }
}
```

如果作业不存在，返回：
```json
{
  "code": 1003,
  "message": "作业不存在",
  "data": null
}
```

---

# 2. 批量删除作业（Batch delete assignments）

- **方法 / 路径**：`DELETE /api/assignments`
- **用途**：批量删除作业，同时删除这些作业关联的OCR结果、编译结果、评分报告等数据。

### 请求参数说明（JSON 体）
| 字段 | 类型      | 必填 | 说明 |
|------|---------|------|------|
| `assignmentIds` | `int[]` | 是 | 要删除的作业ID数组 |

### 响应字段说明（HTTP 200）
| 字段 | 类型       | 说明            |
|------|----------|---------------|
| `code` | `int`    | 业务状态码，0表示成功   |
| `message` | `string` | 操作结果描述信息      |
| `data.deletedCount` | `int`    | 成功删除的作业数量     |
| `data.failedCount` | `int`    | 删除失败的作业数量     |
| `data.failedAssignmentIds` | `int[]`  | 删除失败的作业ID列表   |
| `data.details.assignments` | `int`    | 删除的作业记录数量     |
| `data.details.compileResults` | `int`    | 删除的编译结果记录数量   |
| `data.details.ai_reports` | `int`    | 删除的AI评分报告记录数量 |

成功响应示例：
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "deletedCount": 3,
    "failedCount": 1,
    "failedAssignmentIds": [4,5],
    "details": {
      "assignments": 3,
      "compileResults": 2,
      "ai_reports": 2
    }
  }
}
```



---

# 3. 查看单个作业（Get assignment）

- **方法 / 路径**：`GET /api/assignments/{assignmentId}`
- **用途**：获取指定作业的详细信息，包括作业文件信息以及关联的OCR结果、编译结果、评分报告。

### 路径参数说明
| 字段 | 类型    | 必填 | 说明 |
|------|-------|------|------|
| `assignmentId` | `int` | 是 | 要查询的作业唯一标识符 |

### 响应字段说明（HTTP 200）
#### 基础作业信息
| 字段 | 类型       | 说明 |
|------|----------|------|
| `assignmentId` | `int`    | 作业唯一标识符 |
| `fileName` | `string` | 原始文件名 |
| `storedAt` | `string` | 文件存储路径或URL |
| `createdAt` | `string` | 创建时间戳（YYYY-MM-DD HH:mm:ss格式） |
| `updatedAt` | `string` | 最后更新时间戳（YYYY-MM-DD HH:mm:ss格式） |

#### OCR结果信息
| 字段 | 类型 | 说明 |
|------|------|------|
| `ocrResult.recognizedCode` | `string` | OCR识别到的源代码文本 |

#### 编译结果信息
| 字段 | 类型 | 说明 |
|------|------|------|
| `compileResult.language` | `string` | 编程语言标识 |
| `compileResult.codeLengthBytes` | `int` | 源代码字节长度 |
| `compileResult.submitTime` | `string` | 提交时间戳 |
| `compileResult.evalTime` | `string` | 评测时间戳 |
| `compileResult.compileSuccess` | `boolean` | 编译是否成功 |
| `compileResult.output` | `string` | 程序标准输出内容 |
| `compileResult.error` | `string` | 编译或运行错误信息 |
| `compileResult.score` | `int` | 编译阶段得分 |
| `compileResult.createdAt` | `string` | 编译结果创建时间 |

#### 评分报告信息
| 字段 | 类型         | 说明 |
|------|------------|------|
| `report.assignmentId` | `int`      | 关联的作业ID |
| `report.score` | `int`      | 最终评分（0-100分） |
| `report.breakdown.correctness` | `int`      | 正确性得分 |
| `report.breakdown.standardization` | `int`      | 标准化得分 |
| `report.breakdown.efficiency` | `int`      | 效率得分 |
| `report.breakdown.readability` | `int`      | 可读性得分 |
| `report.reason` | `string`   | 评分理由摘要 |
| `report.suggestions` | `string[]` | 改进建议列表 |
| `report.strengths` | `string[]` | 代码优点列表 |
| `report.weaknesses` | `string[]` | 代码缺点列表 |
| `report.generatedAt` | `string`   | 报告生成时间戳 |

完整响应示例：
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "assignmentId": 1,
    "fileName": "homework1.jpg",
    "storedAt": "/files/abcd1234/homework1.jpg",
    "createdAt": "2025-10-24 21:39:50",
    "updatedAt": "2025-10-24 21:40:05",
    "ocrResult": {
      "recognizedCode": "#include <iostream>..."
    },
    "compileResult": {
      "language": "C++",
      "codeLengthBytes": 102,
      "submitTime": "2025-10-24 21:39:50",
      "evalTime": "2025-10-24 21:39:50",
      "compileSuccess": true,
      "output": "Hello, World!\n",
      "error": null,
      "score": 0,
      "createdAt": "2025-10-24 21:39:56"
    },
    "report": {
      "assignmentId": 1,
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
      "generatedAt": "2025-10-24 21:40:05"
    }
  }
}
```

---

# 4. 批量查看作业列表（Get assignment list）

- **方法 / 路径**：`GET /api/assignments`
- **用途**：分页获取作业列表，包括每个作业的简要信息以及关联的OCR结果、编译结果、评分报告。

### 查询参数说明
| 字段 | 类型 | 必填 | 说明                               |
|------|------|------|----------------------------------|
| `page` | `int` | 否 | 页码，从1开始，默认1                      |
| `pageSize` | `int` | 否 | 每页数量，默认10，最大100                  |
| `sortBy` | `string` | 否 | 排序字段：createdAt/score，默认createdAt |
| `sortOrder` | `string` | 否 | 排序顺序：asc/desc，默认desc             |

### 响应字段说明（HTTP 200）
#### 作业列表信息
| 字段                           | 类型       | 说明      |
|------------------------------|----------|---------|
| `assignments[].assignmentId` | `int`    | 作业唯一标识符 |
| `assignments[].fileName`     | `string` | 文件名     |
| `assignments[].storedAt`     | `string` | 文件存储路径  |
| `assignments[].status`       | `string` | 状态      |
| `assignments[].score`        | `string` | 总分      |
| `assignments[].createdAt`    | `string` | 创建时间戳   |
| `assignments[].updatedAt`    | `string` | 最后更新时间戳 |


#### 分页信息
| 字段 | 类型 | 说明 |
|------|------|------|
| `pagination.page` | `int` | 当前页码 |
| `pagination.pageSize` | `int` | 每页数量 |
| `pagination.total` | `int` | 总记录数 |
| `pagination.totalPages` | `int` | 总页数 |

成功响应示例：
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "assignments": [
      {
        "assignmentId": 1,
        "fileName": "homework1.jpg",
        "storedAt": "/files/abcd1234/homework1.jpg",
        "status": "识别成功",
        "score": 80,
        "createdAt": "2025-10-24 21:39:50",
        "updatedAt": "2025-10-24 21:40:05"
      },
      {
        "assignmentId": 2,
        "fileName": "homework2.cpp",
        "storedAt": "/files/efgh5678/homework2.cpp",
        "status": "识别成功",
        "score": 90,
        "createdAt": "2025-10-24 22:15:30",
        "updatedAt": "2025-10-24 22:15:30"
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 10,
      "total": 25,
      "totalPages": 3
    }
  }
}
```

---

# 6. 错误码详细说明

| 错误码 | 类型 | 说明 |
|--------|------|------|
| `1001` | `FailValidCode` | 参数校验失败：请求缺少必填字段、参数格式不正确等 |
| `1002` | `FailServiceCode` | 服务异常：评分服务超时、OCR服务不可用、编译沙箱故障等 |
| `1003` | `ResourceNotFoundCode` | 资源不存在：指定的作业ID不存在或已被删除 |
| `1004` | `InvalidParameterCode` | 参数无效：传入的参数值不符合要求，如页码为负数等 |

---

# 7. 变更记录

- 2025-10-27：新增5个删改查接口：
  - 删除单个作业（包括关联数据清理）
  - 批量删除作业（支持批量操作和关联数据清理）
  - 查看单个作业（包含完整的关联数据查询）
  - 批量查看作业列表（支持分页和条件筛选）