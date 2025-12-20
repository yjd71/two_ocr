import time
import logging
from datetime import datetime, timezone
# [Modified] Removed crud imports, added Model imports for direct DB access
# from core.core_db.crud import assignment_crud, image_process_crud
from core.core_db.models import Assignment, ImageProcess  # Assuming models are defined here
from core.core_db.schemas import ImageProcessCreate, ImageProcessUpdate, AssignmentUpdate
from src.Compile_run import run_code_wandbox_api
from common.res.response import success_response, validation_error_response, service_error_response, ApiResponse

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session  # 导入 Session 类型
from core.core_db.database import get_db

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由实例，添加API前缀和标签
router = APIRouter()


@router.post("/api/assignments/{assignmentId}/Compile_run")
async def compile_run(assignmentId: int,
                      db: Session = Depends(get_db)  # ✅通过依赖注入获取每个请求独立的 db 会话
                      ):
    """ 进行HTTP参数绑定，前端 uri 请求数据 （作业ID）
                  根据 作业ID 查询数据库中的作业图片
              """
    """
        :param assignmentId: 作业ID，由前端提供
        :return: 包含结果的响应
        """

    try:
        # 参数校验：确保assignmentId有效
        if not assignmentId or not isinstance(assignmentId, int):
            return validation_error_response(message="作业ID无效")

        """ 根据作业ID，查询数据库的作业的识别代码 assignment.extracted_code  """
        """ 根据作业ID，查询数据库的作业地址，获取作业图片 （where file_path == original_image_path） """
        """ 先根据file_path查询数据库中是否存在该图片，（where file_path == original_image_path） """

        # [Modified] Use direct DB query instead of crud.get_assignment
        assignment = db.query(Assignment).filter(Assignment.id == assignmentId).first()

        if assignment is None:
            return validation_error_response(message="未找到对应的作业图片")

        """ Compile编译 """
        success_code = assignment.extracted_code
        """
            参数：
              - code: 要执行的 C++ 源代码（字符串）
              - compiler: 要使用的编译器标识（例如 "gcc-head", "clang-head" 等）
              - timeout: 网络请求超时时间（秒）
            返回：
              - dict: Wandbox 返回的 JSON（已解析）
        """
        current_timestamp = datetime.now(timezone.utc)
        results = run_code_wandbox_api.compile_run(success_code, compiler="gcc-head", timeout=100)
        if results is None:
            """ 更新状态 """
            # [Modified] Update assignment status directly
            assignment.status = "编译失败"
            assignment.processed_at = current_timestamp
            db.commit()
            db.refresh(assignment)

            return service_error_response(message="代码编译运行失败")

        """
        预留，等待修改编译运行的返回
        """
        results_data = results
        # results_data = results_data["data"]

        """ 编译运行结果的入库 （根据uri传递的请求参数 作业ID 查询数据库，如果该作业存在，则更新作业，否则创建新作业）"""

        # [Modified] Query ImageProcess directly
        image_process = db.query(ImageProcess).filter(ImageProcess.assignment_id == assignmentId).first()

        if image_process is None:
            """ 存储编译结果到数据库中 """
            # [Modified] Create new ImageProcess object and add to DB
            new_image_process = ImageProcess(
                assignment_id=assignmentId,
                process_step="compile_run",
                confidence_score=results_data["score"],
                process_result=results,
                processed_at= current_timestamp
            )
            db.add(new_image_process)
            db.commit()
            db.refresh(new_image_process)
        else:
            """ 查询数据库，该作业的编译结果存在，则更新编译结果 """
            # [Modified] Update existing ImageProcess object
            image_process.confidence_score = float(results_data["score"])
            image_process.process_result = results
            image_process.processed_at = current_timestamp

            db.commit()
            db.refresh(image_process)

        """ 更新状态 """
        # [Modified] Update assignment status directly
        assignment.status = "编译成功"
        assignment.processed_at = current_timestamp
        db.commit()
        db.refresh(assignment)

        """ 响应, OCR 识别到的源代码文本 """
        # 返回成功响应
        return success_response(data={"language": results_data["language"],
                                      "codeLengthBytes": results_data["codeLengthBytes"],
                                      "submitTime": results_data["submitTime"],
                                      "evalTime": results_data["evalTime"],
                                      "compileSuccess": results_data["compileSuccess"],
                                      "output": results_data["output"],
                                      "error": results_data["error"],
                                      "score": results_data["score"],
                                      })

    except ValueError as e:
        return validation_error_response(message=str(e))
    except Exception as e:
        # 如果发生异常，应该回滚事务以防止数据库会话被污染。
        # db.rollback() # 生产环境中，如果异常发生在 db.commit() 之前，应添加 db.rollback()
        # 发生未知异常时，必须进行回滚操作，释放数据库锁并恢复会话状态
        db.rollback()
        logger.error(f"deepseek-ocr识别接口发生异常: {str(e)}", exc_info=True)
        return service_error_response(message=str("请求服务器错误" + str(e)))