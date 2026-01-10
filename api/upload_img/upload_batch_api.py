import logging
import shutil
from pathlib import Path
from typing import List, Optional
import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from common.res.response import success_response, validation_error_response, service_error_response

# 导入你的配置和数据库依赖
import config
from core.core_db.database import get_db
from core.core_db.models import Assignment, AssignmentBatch, User  # 导入 User 和 AssignmentBatch

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/assignments_batches")
async def upload_assignment_batch(
        files: List[UploadFile] = File(...),
        title: str = Form(...),
        db: Session = Depends(get_db)
):
    """
    上传单份作业批次 (多文件上传)
    1. 创建 Assignment 主记录
    2. 保存所有图片文件
    3. 创建 AssignmentBatch 子记录
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="未上传任何文件")

        # 1. 创建父级 Assignment 记录
        # 注意：models.py 中 Assignment 没有 title 字段，这里只存必需字段
        # original_image_path 设为临时值，稍后更新为第一张图的路径
        new_assignment = Assignment(
            user_id=1,  # 暂时硬编码 user_id，如同 upload_api.py
            original_image_path="BATCH_PROCESSING",
            status="上传成功",
        )
        db.add(new_assignment)
        db.flush()  # 立即刷新以获取 new_assignment.id

        # 准备存储上传文件的目录 img_upload_dir = "C:/IT/AI/OCR/two_ocr/uploads/original_image"
        upload_dir = Path(config.img_upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        batch_response_list = []
        saved_file_paths = []

        # 2. 遍历处理文件
        for file in files:
            # 生成安全文件名：作业ID_原始文件名 (避免重名覆盖)
            # 例如: 50_page1.jpg
            safe_filename = f"{new_assignment.id}_{file.filename}"
            file_path = upload_dir / safe_filename

            """
               将硬盘上的绝对路径转换为浏览器可识别的 URL 路径
            """
            # 1. 从 config 配置中提取文件夹名称
            # Path(config.img_upload_dir).name 会自动提取路径最后一部分 "original_image"
            sub_dir_name = Path(config.img_upload_dir).name
            # 2. 拼接 URL
            # "/uploads" 是 main.py 中 app.mount 定义的路由前缀
            # sub_dir_name 是 "original_image"
            # safe_filename 是 "50_xxx.jpg"
            url_path = f"/uploads/{sub_dir_name}/{safe_filename}"

            # 异步写入磁盘
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)

            saved_file_paths.append(str(file_path))

            # 3. 创建 AssignmentBatch 子记录
            batch_item = AssignmentBatch(
                assignment_id=new_assignment.id,
                original_image_path=str(file_path),
                status="上传成功"  # 初始状态
            )
            db.add(batch_item)
            db.flush()  # 刷新以获取 batch_item.id

            # 构建单个文件的响应数据
            batch_response_list.append({
                "assignmentBatchId": batch_item.id,
                "fileName": file.filename,
                "url": str(url_path)  # 根据实际需求，这里可能需要转为相对路径或Web URL
            })

        # 4. 更新父记录的 original_image_path 为第一张图的路径 (满足非空约束)
        if saved_file_paths:
            new_assignment.original_image_path = saved_file_paths[0]

        db.commit()  # 提交整个事务
        db.refresh(new_assignment)  # ✅ [关键修复] 刷新对象以获取数据库生成的 uploaded_at 时间

        # ✅ [关键修复] 处理时间格式化
        create_time_str = ""
        if new_assignment.uploaded_at:
            create_time_str = new_assignment.uploaded_at.strftime("%Y-%m-%d %H:%M:%S")

        # 5. 返回响应
        return success_response(data={
            "assignmentId": new_assignment.id,
            "title": title,  # 原样返回前端传来的标题
            "createTime": create_time_str,  # ORM 会自动处理时间，如果不回显可省略
            "imageCount": len(files),
            "assignmentBatch": batch_response_list
        })

    except Exception as e:
        db.rollback()
        logger.error(f"批次上传接口异常: {str(e)}", exc_info=True)
        # 清理已上传的残留文件 (可选)
        return service_error_response(message=f"请求服务器错误: {str(e)}")
