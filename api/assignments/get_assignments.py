import os

from core.core_db.crud import score_crud, assignment_crud, image_process_crud
from common.res.response import success_response, validation_error_response, service_error_response, ApiResponse

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session  # 导入 Session 类型
from core.core_db.database import get_db

# 创建路由实例，添加API前缀和标签
router = APIRouter()


@router.get("/api/assignments/{assignmentId}")
async def get_assignments_api(assignmentId: int,
                              db: Session = Depends(get_db)  # ✅通过依赖注入获取每个请求独立的 db 会话
                              ):
    """ 进行HTTP参数绑定，前端 uri 请求数据 （作业ID）
                  根据 作业ID 查询数据库中的作业图片
              """
    """
        :param assignmentId: 作业ID，由前端提供
        :return: 包含作业结果的响应
    """

    try:
        # 参数校验：确保assignmentId有效
        if not assignmentId or not isinstance(assignmentId, int):
            return validation_error_response(message="作业ID无效")

        """ 根据作业ID查找数据库中作业的识别代码 """
        assignment = assignment_crud.get_assignment(db, assignmentId)
        if assignment is None:
            return validation_error_response(message="未找到对应的作业图片")

        # 拿到图片路径的中的图片名称
        filename = os.path.splitext(os.path.basename(assignment.original_image_path))
        filename = f"{filename[0]}{filename[1]}"

        """ 根据作业ID查找数据库中编译运行的结果 """
        compile_run_result = image_process_crud.get_image_process_by_assignment_id(db, assignmentId)
        if compile_run_result is None:
            return validation_error_response(message="未找到对应的作业的编译运行的结果")

        # ✅ 修正 1：提取 ORM 属性
        """
         Decimal 类型来源： Python 数据库ORM中，用于存储精确浮点数的字段，会被映射为 Python 标准库中的 decimal.Decimal 类型，
         而不是内置的 float 类型。标准的 JSON 库 不支持 Decimal 对象, 将其显式地转换为 JSON 兼容的类型，即 float（浮点数）或 str（字符串）。
        """
        compile_score = float(compile_run_result.confidence_score)
        compile_processed_at = compile_run_result.processed_at
        compile_run_result = compile_run_result.process_result
        """
            预留，等待修改编译运行的返回
        """
        # compile_run_result = compile_run_result["data"]


        """ 根据作业ID查找数据库中AI报告的结果 """
        ai_report_result = score_crud.get_score_by_assignment_id(db, assignmentId)
        if ai_report_result is None:
            return validation_error_response(message="未找到对应的作业图片的AI报告的结果")
        """
                Decimal 类型来源： Python 数据库ORM中，用于存储精确浮点数的字段，会被映射为 Python 标准库中的 decimal.Decimal 类型，
                而不是内置的 float 类型。标准的 JSON 库 不支持 Decimal 对象, 将其显式地转换为 JSON 兼容的类型，即 float（浮点数）或 str（字符串）。
               """
        final_score = float(ai_report_result.final_score)
        scored_at = ai_report_result.scored_at
        ai_report_result = ai_report_result.score_details

        # 响应
        return success_response(data={
            "assignmentId": assignment.id,
            "fileName": filename,
            "storedAt": assignment.original_image_path,
            "createdAt": f'{assignment.uploaded_at}',
            "updatedAt": f'{assignment.processed_at}',
            "ocrResult": {
                "recognizedCode": assignment.extracted_code
            },
            "compileResult": {
                "language": compile_run_result["language"],
                "codeLengthBytes": compile_run_result["codeLengthBytes"],
                "submitTime": f'{compile_run_result["submitTime"]}',
                "evalTime": f'{compile_run_result["evalTime"]}',
                "compileSuccess": compile_run_result["compileSuccess"],
                "output": f'{compile_run_result["output"]}',
                "error": f'{compile_run_result["error"]}',
                "score": compile_score,
                "createdAt": f'{compile_processed_at}'
            },
            "report": {
                "assignmentId": assignment.id,
                "score": final_score,  # 得分
                "breakdown": {
                    "correctness": float(ai_report_result["breakdown"]["correctness"]),
                    "standardization": float(ai_report_result["breakdown"]["standardization"]),
                    "efficiency": float(ai_report_result["breakdown"]["efficiency"]),
                    "readability": float(ai_report_result["breakdown"]["readability"]),
                },  # 分项得分
                "reason": ai_report_result["reason"],  # 评分建议
                "suggestions": ai_report_result["suggestions"],  # 改进建议
                "strengths": ai_report_result["strengths"],  # 优点
                "weaknesses": ai_report_result["weaknesses"],  # 缺点
                "generatedAt": f'{scored_at}'
            }
        })



    except ValueError as e:
        return validation_error_response(message=str(e))
    except Exception as e:
        return service_error_response(message="服务器内部错误: " + str(e))
