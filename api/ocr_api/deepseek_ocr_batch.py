import logging
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# 导入项目依赖
from src.DeepSeekOCR.deepseekOCR_1 import deepseek_ocr
from src.DeepSeekOCR.deepseek_ocr_split import deepseek_ocr_split

from common.res.response import success_response, validation_error_response, service_error_response
from core.core_db.database import get_db
from core.core_db.models import Assignment, AssignmentBatch  # 确保导入了 AssignmentBatch

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/assignments_batches/{assignment_id}/deepseek_ocr")
async def batch_ocr_api(
        assignment_id: int,
        db: Session = Depends(get_db)
):
    """
    批量OCR识别接口：识别指定作业下的所有图片批次
    """
    try:
        # 1. 查询作业及其关联的批次图片
        # SQLAlchemy 默认懒加载，访问 assignment.batches 时会自动查询子表
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

        if not assignment:
            return validation_error_response(message="未找到对应的作业数据")

        # 检查是否有子批次
        if not assignment.batches:
            return validation_error_response(message="该作业下没有可识别的图片批次")

        # 2. 初始化变量
        full_code_parts = []  # 用于拼接完整代码
        batch_response_list = []  # 用于返回前端的子项列表
        current_timestamp = datetime.now(timezone.utc)

        # 3. 遍历批次图片进行识别
        # 建议按 ID 排序确保代码拼接顺序正确 (假设 ID 越小代表页码越前)
        sorted_batches = sorted(assignment.batches, key=lambda x: x.id)

        for batch in sorted_batches:
            # 获取图片绝对路径
            img_path = str(Path(batch.original_image_path))

            # 调用 OCR (假设输出目录为 ./output)
            # 注意：如果 deepseek_ocr 耗时较长，生产环境建议使用异步任务(Celery)或线程池
            time.sleep(3)
            # ocr_result = deepseek_ocr(img_path, './output')
            ocr_result = deepseek_ocr_split(img_path, './output')  # 图片切片识别

            # 更新子表 (AssignmentBatch) 状态
            if ocr_result:
                batch.status = "识别成功"
                batch.extracted_code = ocr_result
                full_code_parts.append(ocr_result)  # 收集代码
                is_success = True
            else:
                batch.status = "识别失败"
                is_success = False

            batch.updated_at = current_timestamp

            # 构建单个批次的响应数据
            batch_response_list.append({
                "assignmentBatchId": batch.id,
                "success": is_success,
                "recognizedCode": ocr_result
            })

        # 4. 更新主表 (Assignment) 状态
        # 将所有子图代码用换行符拼接
        combined_code = "\n\n".join(full_code_parts)

        assignment.extracted_code = combined_code
        assignment.status = "识别完成" if combined_code else "识别失败"
        assignment.processed_at = current_timestamp

        # 5. 提交事务
        db.commit()
        db.refresh(assignment)

        # 6. 返回结果
        return success_response(data={
            "assignmentId": assignment.id,
            "fullRecognizedCode": combined_code,
            "assignmentBatch": batch_response_list
        })

    except Exception as e:
        db.rollback()
        logger.error(f"批量OCR识别异常: {str(e)}", exc_info=True)
        return service_error_response(message=f"服务器内部错误: {str(e)}")
