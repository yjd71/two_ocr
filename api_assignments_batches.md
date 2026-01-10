
-----

## 1\. 上传单份作业批次 (Create Assignment_Batch)

  * **设计理念**：一个请求对应前端的一个“作业批次卡片”。
  * **方法 / 路径**：`POST /api/assignments_batches`
  * **Content-Type**：`multipart/form-data`

### 请求参数 (Form-Data)

| 字段名 | 类型 | 必填    | 说明 |
| :--- | :--- |:------| :--- |
| **`files`** | `File[]` (Binary) | **是** | **多文件数组**。<br>包含当前这一个批次下的所有图片（例如 3 张图）。 |
| **`title`** | `String` | **是** | **作业标题**。<br>例如前端生成的 "作业批次 \#1"。 |

### 后端处理逻辑

1.  在 `assignments` 表创建一条记录（主表），生成 `assignment_id`。
2.  遍历 `files` 数组，将图片保存，并在 `assignments_batches` 表创建多条记录（子表），外键关联 `assignment_id`。

### 响应结果 (HTTP 200)

```json
{
  "code": 0,
  "message": "批次上传成功",
  "data": {
    "assignmentId": 50,       // 【关键】后端生成的作业ID，前端需绑定到卡片上
    "title": "作业批次 #1",
    "createTime": "2025-12-09 16:20:00",
    "imageCount": 3,
    "assignmentBatch": [                 // 返回子表图片信息用于回显
      {
        "assignmentBatchId": 1,         // 图片的唯一ID（用于单独删除）
        "fileName": "page1.jpg",
        "url": "/uploads/1001/page1.jpg"
      },
      {
        "assignmentBatchId": 2,
        "fileName": "page2.jpg",
        "url": "/uploads/1001/page2.jpg"
      },
      {
        "assignmentBatchId": 3,
        "fileName": "page3.jpg",
        "url": "/uploads/1001/page3.jpg"
      }
    ]
  }
}
```

-----

## 2\. 识别单份作业批次 (Recognize Assignment)

  * **设计理念**：针对已上传的某一个作业 ID，触发 OCR 识别。
  * **方法 / 路径**：`POST /api/assignments_batches/{assignmentId}/ocr`
  * **方法 / 路径**：`POST /api/assignments_batches/{assignmentId}/deepseek_ocr`
  * **Content-Type**：`application/json`

### 路径参数 (Path Variable)

  * `assignmentId`: (Int) 上传接口返回的 `data.assignmentId`。

### 请求参数 (Body)

通常为空

### 后端处理逻辑

1.  根据 `assignmentId` 查询 `assignments_batches` 表，找到关联的 N 张图片。
2.  依次（或并发）对图片进行 OCR 识别。
3.  (可选) 将 N 段代码按图片顺序拼接。

### 响应结果 (HTTP 200)

```json
{
  "code": 0,
  "message": "识别完成",
  "data": {
    "assignmentId": 50, //作业ID
    "fullRecognizedCode": "#include <iostream>...\nint main() { ... }", // 拼接后的完整代码
    "assignmentBatch": [  // 作业ID下的每张图的独立识别结果
      {
        "assignmentBatchId": 1,
        "success": true,
        "recognizedCode": "#include <iostream>"
      },
      {
        "assignmentBatchId": 2,
        "success": true,
        "recognizedCode": "using namespace std;"
      },
      {
        "assignmentBatchId": 3,
        "success": false,
        "recognizedCode": null  // 无法识别, 容错处理
      }
    ]
  }
}
```

-----
