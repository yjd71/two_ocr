import logging
import concurrent.futures
import time
from pathlib import Path
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

# 导入项目依赖
from src.DeepSeekOCR.deepseekOCR_1 import deepseek_ocr
from common.res.response import success_response, validation_error_response
from core.core_db.database import get_db, SessionLocal
from core.core_db.models import Assignment

logger = logging.getLogger(__name__)
router = APIRouter()


# --- 1. 定义带超时的 OCR 执行器 (Windows 兼容版) ---
def run_ocr_with_timeout(img_path: str, output_dir: str, timeout_seconds: int = 120) -> str:
    """
    在线程池中运行 OCR，并设置超时等待。
    注意：在 Windows 下无法强制杀死正在运行 GPU 计算的线程，
    但这能防止主逻辑无限期等待。
    """
    # 使用 ThreadPoolExecutor (线程池) 而不是 ProcessPoolExecutor (进程池)
    # 这样可以共享主进程已经加载的模型显存，避免 Windows 下的 OOM 崩溃。
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        # 提交任务
        future = executor.submit(deepseek_ocr, img_path, output_dir)

        try:
            # 等待结果，如果超过 timeout_seconds 秒还没返回，抛出 TimeoutError
            result = future.result(timeout=timeout_seconds)
            return result
        except concurrent.futures.TimeoutError:
            logger.error(f"OCR 任务执行超时 ({timeout_seconds}s)，放弃等待: {img_path}")
            # 注意：线程实际上还在后台运行，直到完成，但我们不再关心其结果
            return None
        except Exception as e:
            logger.error(f"OCR 任务执行出错: {e}")
            return None


# --- 2. 后台任务逻辑 (串行调度) ---
def background_ocr_process(assignment_id: int):
    logger.info(f"开始后台执行作业 {assignment_id} 的OCR任务")
    db: Session = SessionLocal()
    try:
        assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment or not assignment.batches:
            return

        assignment.status = "识别中..."
        db.commit()

        full_code_parts = []
        has_error = False
        sorted_batches = sorted(assignment.batches, key=lambda x: x.id)

        for batch in sorted_batches:
            try:
                img_path = str(Path(batch.original_image_path))

                # 【关键调用】使用带超时的函数
                # 这里设置超时时间，例如 120 秒
                time.sleep(3)
                ocr_result = run_ocr_with_timeout(img_path, './output', timeout_seconds=120)

                if ocr_result:
                    batch.status = "识别成功"
                    batch.extracted_code = ocr_result
                    full_code_parts.append(ocr_result)
                else:
                    batch.status = "识别超时或失败"  # 更新状态为失败
                    has_error = True
            except Exception as e:
                logger.error(f"批次处理异常: {e}")
                batch.status = "系统错误"
                has_error = True

            # 无论成功失败，都更新时间并保存
            batch.updated_at = datetime.now(timezone.utc)
            db.commit()

        # 汇总结果
        combined_code = "\n\n".join(full_code_parts)
        assignment.extracted_code = combined_code

        if not combined_code:
            assignment.status = "识别失败"
        elif has_error:
            assignment.status = "部分完成"  # 提示用户有部分图片超时了
        else:
            assignment.status = "识别完成"

        assignment.processed_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        logger.error(f"后台任务异常: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


# --- 3. API 接口 (保持不变) ---
@router.post("/api/assignments_batches/{assignment_id}/deepseek_ocr")
async def batch_ocr_api(
        assignment_id: int,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        return validation_error_response(message="未找到对应的作业数据")

    if not assignment.batches:
        return validation_error_response(message="该作业下没有可识别的图片批次")

    # 添加到 FastAPI 后台任务队列
    background_tasks.add_task(background_ocr_process, assignment_id)

    return success_response(data={
        "assignmentId": assignment_id,
        "message": "识别请求已提交，系统正在后台处理中。",
        "status": "processing"
    })