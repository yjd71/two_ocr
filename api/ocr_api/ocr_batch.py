import logging
import os
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

# 导入项目依赖
from src.PaddleOCR import ocr_v2
from common.res.response import success_response, validation_error_response, service_error_response
from core.core_db.database import get_db
from core.core_db.models import Assignment, AssignmentBatch
from config import image_processed_path  # 引用 ocr.py 中使用的配置

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/assignments_batches/{assignmentId}/ocr")
async def batch_paddle_ocr_api(
        assignmentId: int,
        db: Session = Depends(get_db)
):
    """
    PaddleOCR 批量识别接口：识别指定作业下的所有图片批次
    逻辑参考：deepseek_ocr_batch.py
    """
    try:
        # 1. 查询作业及其关联的批次图片
        # SQLAlchemy 默认懒加载，访问 assignment.batches 时会自动查询子表
        assignment = db.query(Assignment).filter(Assignment.id == assignmentId).first()

        if not assignment:
            return validation_error_response(message="未找到对应的作业数据")

        if not assignment.batches:
            return validation_error_response(message="该作业下没有可识别的图片批次")

        # 2. 初始化变量
        full_code_parts = []  # 用于拼接完整代码
        batch_response_list = []  # 用于返回前端的子项列表

        # 3. 遍历批次图片进行识别
        # 按 ID 排序确保代码拼接顺序正确
        sorted_batches = sorted(assignment.batches, key=lambda x: x.id)

        for batch in sorted_batches:
            # --- 路径处理 ---
            # 获取输入图片的绝对路径 (参考 deepseek_ocr_batch.py 使用 Path)
            img_input_path = str(Path(batch.original_image_path))

            # 构建输出图片路径 (参考 ocr.py 逻辑，用于保存 PaddleOCR 处理后的图片)
            filename = os.path.basename(img_input_path)
            os.makedirs(image_processed_path, exist_ok=True)

            # --- 调用 PaddleOCR ---
            # 复用 ocr.py 中的 ocr_v2 调用方式
            # 注意：这里假设 ocr_v2.paddle_ocr 第一个参数接受输入路径，第二个参数接受输出路径
            results = ocr_v2.paddle_ocr(img_input_path)

            # --- 结果处理 ---
            extracted_str = ""
            is_success = False

            if results:
                # 复用 ocr.py 中的字符串提取逻辑
                extracted_str = ocr_v2.ocr_recognition_return_string(results)
                if extracted_str:
                    full_code_parts.append(extracted_str)
                    is_success = True

            # --- 更新子表 (AssignmentBatch) ---
            batch.status = "识别成功" if is_success else "识别失败"
            batch.extracted_code = extracted_str
            # 如果需要记录最后更新时间，可以使用 func.now() 或者 Python 时间
            # batch.updated_at = func.now()

            # 构建单个批次的响应数据
            batch_response_list.append({
                "assignmentBatchId": batch.id,
                "success": is_success,
                "recognizedCode": extracted_str
            })

        # 4. 更新主表 (Assignment) 状态
        # 将所有子图代码用换行符拼接
        combined_code = "\n\n".join(full_code_parts)

        assignment.extracted_code = combined_code
        assignment.status = "识别完成" if combined_code else "识别失败"
        assignment.processed_at = func.now()

        # 5. 提交事务
        db.commit()
        db.refresh(assignment)

        # 6. 返回结果 (格式符合 api_assignments_batches.md)
        return success_response(data={
            "assignmentId": assignment.id,
            "fullRecognizedCode": combined_code,
            "assignmentBatch": batch_response_list
        })

    except Exception as e:
        db.rollback()
        logger.error(f"批量PaddleOCR识别异常: {str(e)}", exc_info=True)
        return service_error_response(message=f"服务器内部错误: {str(e)}")