import logging
import os
from typing import List
from pydantic import BaseModel

from common.res.response import success_response, validation_error_response, service_error_response

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from core.core_db.database import get_db

# 导入相关模型
# 注意：假设 Score 对应文档中的"AI评分报告/分数"，ImageProcess 对应"编译结果"
from core.core_db.models import Assignment, Score, ImageProcess

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由实例
router = APIRouter()


# 定义请求体 Schema
class BatchDeleteRequest(BaseModel):
    assignmentIds: List[int]


@router.delete("/api/assignments")
async def batch_delete_assignments_api(
        params: BatchDeleteRequest,
        db: Session = Depends(get_db)
):
    """
    批量删除作业接口
    1. 接收作业ID列表
    2. 校验哪些ID存在，哪些不存在
    3. 统计即将删除的关联数据（用于响应详情）
    4. 删除物理文件（原始图、处理图）
    5. 删除数据库记录（级联删除关联表）
    """
    try:
        # 1. 参数获取
        target_ids = params.assignmentIds
        if not target_ids:
            return validation_error_response(message="参数无效：assignmentIds 不能为空")

        # 2. 查询所有存在的作业记录
        # SELECT * FROM assignment WHERE id IN (...)
        existing_assignments = db.query(Assignment).filter(Assignment.id.in_(target_ids)).all()

        # 提取存在的ID列表
        existing_ids = [assign.id for assign in existing_assignments]

        # 计算失败的ID (请求的ID - 存在的ID)
        failed_ids = list(set(target_ids) - set(existing_ids))

        if not existing_ids:
            # 如果没有一个ID是有效的
            return success_response(data={
                "deletedCount": 0,
                "failedCount": len(failed_ids),
                "failedAssignmentIds": failed_ids,
                "details": {
                    "assignments": 0,
                    "compileResults": 0,
                    "ai_reports": 0
                }
            })

        # 3. 统计关联数据 (为了满足 API 响应中的 details 字段)
        # 统计将要删除的编译结果数量 (ImageProcess表)
        compile_results_count = db.query(ImageProcess).filter(
            ImageProcess.assignment_id.in_(existing_ids)
        ).count()

        # 统计将要删除的评分报告数量 (Score表)
        # 根据文档语境，Score 通常对应评分报告数据
        ai_reports_count = db.query(Score).filter(
            Score.assignment_id.in_(existing_ids)
        ).count()

        # 4. 执行删除操作
        deleted_count = 0

        for assignment in existing_assignments:
            # 4.1 删除物理文件
            try:
                # 删除原始图片
                if assignment.original_image_path and os.path.exists(assignment.original_image_path):
                    os.remove(assignment.original_image_path)

                # 删除处理后的图片 (如果有)
                if assignment.processed_image_path and os.path.exists(assignment.processed_image_path):
                    os.remove(assignment.processed_image_path)
            except Exception as file_err:
                # 文件删除失败不应阻断数据库记录删除，记录日志即可
                print(f"Warning: Failed to delete file for assignment {assignment.id}: {file_err}")

            # 4.2 删除数据库记录
            # 注意：如果数据库配置了 ON DELETE CASCADE，删除 Assignment 会自动删除 Score 和 ImageProcess
            # 如果没有配置级联，则需要手动先删除关联表。
            # 这里假设使用 SQLAlchemy ORM 操作，直接删除父对象。
            db.delete(assignment)
            deleted_count += 1

        # 5. 提交事务
        db.commit()

        # 6. 构造响应
        return success_response(data={
            "deletedCount": deleted_count,
            "failedCount": len(failed_ids),
            "failedAssignmentIds": failed_ids,
            "details": {
                "assignments": deleted_count,
                "compileResults": compile_results_count,
                "ai_reports": ai_reports_count
            }
        })

    except Exception as e:
         # 如果发生异常，应该回滚事务以防止数据库会话被污染。
        # db.rollback() # 生产环境中，如果异常发生在 db.commit() 之前，应添加 db.rollback()
        # 发生未知异常时，必须进行回滚操作，释放数据库锁并恢复会话状态
        db.rollback()
        logger.error(f"deepseek-ocr识别接口发生异常: {str(e)}", exc_info=True)
        return service_error_response(message=f"批量删除失败: {str(e)}")