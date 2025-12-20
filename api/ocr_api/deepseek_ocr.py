import logging
import time
from pathlib import Path

from src.DeepSeekOCR.deepseekOCR_1 import deepseek_ocr
from src.DeepSeekOCR.deepseek_ocr_split import deepseek_ocr_split

from datetime import datetime, timezone  # 导入 datetime 和 timezone
from core.core_db.models import Assignment
from common.res.response import success_response, validation_error_response, service_error_response
from config import image_processed_path, app

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session  # 导入 SQLAlchemy 的 Session 类型，用于数据库会话管理
from core.core_db.database import get_db  # 导入获取数据库会话的依赖函数

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由实例
router = APIRouter()


@router.post("/api/assignments/{assignment_id}/deepseek_ocr")
async def ocr_api(
        assignment_id: int,  # 从路径中获取作业 ID
        # 依赖注入：每个请求都会通过 Depends(get_db) 获取一个独立的 Session 对象。
        # 这是一个 FastAPI/SQLAlchemy 的标准模式，确保每个请求都有一个隔离的数据库会话。
        db: Session = Depends(get_db)
):
    """
    OCR图片识别接口，处理特定作业ID的图片识别请求。
    """
    try:
        # 1. 数据库查询操作：根据 ID 查找作业记录
        # db.query(Assignment)：构建一个针对 Assignment 模型的操作查询。
        # .filter(Assignment.id == assignment_id)：添加过滤条件，匹配传入的作业 ID。
        # .first()：执行查询并返回找到的第一个结果（一个 Assignment ORM 对象）。
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()

        if not assignment:
            # 如果查询结果为空，返回验证错误响应
            return validation_error_response(message="未找到对应的作业数据")

        if not assignment.original_image_path:
            # 检查数据库记录中是否有图片路径
            return validation_error_response(message="该作业缺少原始图片路径")

        # 2. 路径处理
        original_path = Path(assignment.original_image_path)
        save_dir = Path(image_processed_path)
        save_dir.mkdir(parents=True, exist_ok=True)

        # 3. 执行 OCR 识别
        # time.sleep(3)
        # ocr_result = deepseek_ocr(str(original_path), './output')
        ocr_result = deepseek_ocr_split(str(original_path), './output')  # 图片切片识别

        # 4. 准备更新时间
        # 使用 datetime.now() 获取当前时间，这与数据库的 DateTime 类型匹配。
        # 注意：建议使用带时区的 datetime.now(timezone.utc) 来确保时间戳的准确性。
        current_timestamp = datetime.now(timezone.utc)

        if ocr_result is None:
            # --- 识别失败逻辑 ---
            # 直接修改 ORM 对象的属性，SQLAlchemy 会跟踪这些变更。
            assignment.status = "识别失败"
            assignment.processed_at = current_timestamp

            # 数据库事务操作：提交变更
            # db.commit()：将 ORM 对象上所有已修改的属性变更同步到数据库中，完成事务。
            db.commit()
            # db.refresh(assignment)：从数据库中重新加载 assignment 对象，确保其状态是最新的。
            db.refresh(assignment)
            return service_error_response(message="OCR处理失败: 未能识别到内容")

        else:
            # --- 识别成功逻辑 ---
            # 直接修改 ORM 对象的属性
            assignment.status = "识别成功"
            assignment.processed_image_path = ""  # 假设不需要保存处理后的图片路径
            assignment.extracted_code = ocr_result
            assignment.processed_at = current_timestamp

            # 数据库事务操作：提交变更
            db.commit()
            # 从数据库刷新对象状态
            db.refresh(assignment)

            # 5. 返回成功响应
            return success_response(data={
                "recognizedCode": ocr_result,
                "processed_image_path": "",
                "res_image_path": ""
            })

    except Exception as e:
        # 如果发生异常，应该回滚事务以防止数据库会话被污染。
        # db.rollback() # 生产环境中，如果异常发生在 db.commit() 之前，应添加 db.rollback()
        # 发生未知异常时，必须进行回滚操作，释放数据库锁并恢复会话状态
        db.rollback()
        logger.error(f"deepseek-ocr识别接口发生异常: {str(e)}", exc_info=True)
        return service_error_response(message=f"请求服务器错误: {str(e)}")
