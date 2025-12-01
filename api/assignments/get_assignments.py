import os
import logging
from typing import Dict, Any, Optional

from fastapi import Depends, APIRouter, Path
from sqlalchemy.orm import Session
from core.core_db.database import get_db
# 引入数据库模型
from core.core_db.models import Assignment, ImageProcess, Score
from common.res.response import success_response, validation_error_response, service_error_response

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/api/assignments/{assignmentId}")
async def get_assignments_detail_api(
        assignment_id: int = Path(..., alias="assignmentId", description="作业ID"),
        db: Session = Depends(get_db)
):
    """
    获取单个作业的详情信息
    策略：查询主表，若存在则尝试查询关联表。如果关联表数据缺失，则返回 None，不阻断请求。
    """
    try:
        # ==========================================
        # 1. 数据库查询：获取作业主表信息 (必填)
        # ==========================================
        """
        db.query(Assignment): 创建一个针对 Assignment 模型的查询对象。
        .filter(Assignment.id == assignment_id): 添加 WHERE 条件，相当于 WHERE id = assignment_id。
        .first(): 执行查询并返回第一条匹配的记录。如果未找到，返回 None。
        """
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

        if not assignment:
            return validation_error_response(message="未找到对应的作业数据")

        # ==========================================
        # 2. 数据库查询与处理：编译运行结果 (可选)
        # ==========================================
        """
            查询 ImageProcess 表，查找外键 assignment_id 等于当前作业 ID 的记录。
        """
        image_process = db.query(ImageProcess).filter(
            ImageProcess.assignment_id == assignment_id
        ).first()

        # 初始化编译结果响应为 None
        compile_result_response = None

        # 只有当查询到记录时，才进行数据处理
        if image_process:
            # 2.1 数据清洗
            compile_data = image_process.process_result if image_process.process_result else {}
            compile_confidence = float(
                image_process.confidence_score) if image_process.confidence_score is not None else 0.0

            # 2.2 构建编译部分响应
            compile_result_response = {
                "language": compile_data.get("language", "cpp"),
                "codeLengthBytes": compile_data.get("codeLengthBytes", 0),
                "submitTime": str(compile_data.get("submitTime", "")),
                "evalTime": str(compile_data.get("evalTime", "")),
                "compileSuccess": compile_data.get("compileSuccess", False),
                "output": str(compile_data.get("output", "")),
                "error": str(compile_data.get("error", "")),
                "score": compile_confidence,
                "createdAt": str(image_process.processed_at)
            }

        # ==========================================
        # 3. 数据库查询与处理：AI 评分报告 (可选)
        # ==========================================
        """
        查询 Score 表，查找外键 assignment_id 等于当前作业 ID 的记录。
        """
        score_record = db.query(Score).filter(
            Score.assignment_id == assignment_id
        ).first()

        # 初始化评分报告响应为 None
        report_response = None

        # 只有当查询到记录时，才进行数据处理
        if score_record:
            # 3.1 数据清洗
            ai_score = float(score_record.ai_score) if score_record.ai_score is not None else 0.0
            ai_details = score_record.score_details if score_record.score_details else {}
            breakdown = ai_details.get("breakdown", {})

            # 3.2 构建评分部分响应
            report_response = {
                "assignmentId": assignment.id,
                "score": ai_score,
                "breakdown": {
                    "correctness": float(breakdown.get("correctness", 0)),
                    "standardization": float(breakdown.get("standardization", 0)),
                    "efficiency": float(breakdown.get("efficiency", 0)),
                    "readability": float(breakdown.get("readability", 0)),
                },
                "reason": ai_details.get("reason", ""),
                "suggestions": ai_details.get("suggestions", []),
                "strengths": ai_details.get("strengths", []),
                "weaknesses": ai_details.get("weaknesses", []),
                "generatedAt": str(score_record.scored_at)
            }

        # ==========================================
        # 4. 构建最终响应结构
        # ==========================================

        # 处理文件名
        original_filename = os.path.basename(
            assignment.original_image_path) if assignment.original_image_path else "unknown.jpg"

        response_data = {
            "assignmentId": assignment.id,
            "fileName": original_filename,
            "storedAt": assignment.original_image_path,
            "createdAt": str(assignment.uploaded_at),
            "updatedAt": str(assignment.processed_at),

            "ocrResult": {
                "recognizedCode": assignment.extracted_code
            },

            # 如果上面没查到，这里就是 None (JSON 中的 null)，前端需据此判断显示状态
            "compileResult": compile_result_response,
            "report": report_response
        }

        return success_response(data=response_data)

    except ValueError as e:
        logger.error(f"数据类型转换错误: {e}")
        # 这里改用 service_error 比较好，因为通过了数据库校验，说明是后端数据脏了，不是用户传参错误
        return service_error_response(message="后端数据处理异常")
    except Exception as e:
        logger.error(f"获取作业详情失败: {e}", exc_info=True)
        return service_error_response(message=f"服务器内部错误: {str(e)}")