import os
import logging
from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from core.core_db.database import get_db
from core.core_db.models import Assignment, Score, ImageProcess
from common.res.response import success_response, service_error_response

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由实例
router = APIRouter()


@router.delete("/api/assignments/{assignmentId}")
async def delete_assignment_api(
        assignmentId: int = Path(..., description="要删除的作业唯一标识符"),
        db: Session = Depends(get_db)
):
    """
    删除单个作业接口
    1. 检查作业是否存在
    2. 检查关联数据的存在性（OCR、编译、评分），用于响应反馈
    3. 删除物理文件
    4. 删除数据库记录（级联删除）
    """
    try:
        # 1. 查询作业是否存在
        assignment = db.query(Assignment).filter(Assignment.id == assignmentId).first()

        if not assignment:
            # 根据 API 文档，资源不存在返回 code 1003
            return JSONResponse(
                content={
                    "code": 1003,
                    "message": "作业不存在",
                    "data": None
                }
            )

        # 2. 检查关联数据状态 (用于构建响应数据，告知用户删除了哪些关联项)
        # 2.1 检查 OCR 结果 (通常存储在 assignment.extracted_code 字段)
        has_ocr = bool(assignment.extracted_code)

        # 2.2 检查编译结果 (ImageProcess 表)
        # 使用 query(...).limit(1).count() 或者 .first() 判断是否存在
        has_compile = db.query(ImageProcess.id).filter(
            ImageProcess.assignment_id == assignmentId
        ).first() is not None

        # 2.3 检查评分报告 (Score 表)
        has_report = db.query(Score.id).filter(
            Score.assignment_id == assignmentId
        ).first() is not None

        # 3. 删除物理文件
        # 删除原始图片
        if assignment.original_image_path and os.path.exists(assignment.original_image_path):
            try:
                os.remove(assignment.original_image_path)
            except OSError:
                # 记录日志，但不阻断流程
                pass

        # 删除处理后的图片 (如果有)
        if assignment.processed_image_path and os.path.exists(assignment.processed_image_path):
            try:
                os.remove(assignment.processed_image_path)
            except OSError:
                pass

        # 4. 删除数据库记录
        # 删除 Assignment 对象，ORM 会根据配置 (cascade) 处理关联表，
        # 或者如果没有级联配置，需要手动删除关联表。
        # 此处直接删除主对象。
        db.delete(assignment)
        db.commit()

        # 5. 返回成功响应
        return success_response(data={
            "deletedAssignmentId": assignmentId,
            "deletedRelatedRecords": {
                "ocrResults": has_ocr,
                "compileResults": has_compile,
                "reports": has_report
            }
        })

    except Exception as e:
        # 如果发生异常，应该回滚事务以防止数据库会话被污染。
        # db.rollback() # 生产环境中，如果异常发生在 db.commit() 之前，应添加 db.rollback()
        # 发生未知异常时，必须进行回滚操作，释放数据库锁并恢复会话状态
        db.rollback()
        logger.error(f"deepseek-ocr识别接口发生异常: {str(e)}", exc_info=True)
        return service_error_response(message=f"删除作业失败: {str(e)}")