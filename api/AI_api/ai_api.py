import time

from core.core_db.crud import score_crud, assignment_crud, image_process_crud
from core.core_db.database import get_db
from core.core_db.schemas import ScoreCreate, ScoreUpdate
from src.AI_report import ai_run_reult_no_jsonDecoder, ai_run_reult
from fastapi import FastAPI, HTTPException, APIRouter
from common.res.response import success_response, validation_error_response, service_error_response, ApiResponse

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session  # 导入 Session 类型
from core.core_db.database import get_db

# 创建路由实例，添加API前缀和标签
router = APIRouter()


@router.post("/api/assignments/{assignmentId}/report")
async def AI_api(assignmentId: int,
                 db: Session = Depends(get_db)  # ✅通过依赖注入获取每个请求独立的 db 会话
                 ):
    """ 进行HTTP参数绑定，前端 uri 请求数据 （作业ID）
                  根据 作业ID 查询数据库中的作业图片
              """
    """
  
        :param assignmentId: 作业ID，由前端提供
        :return: 包含OCR识别结果的响应
        """

    try:
        # 参数校验：确保assignmentId有效
        if not assignmentId or not isinstance(assignmentId, int):
            return validation_error_response(message="作业ID无效")

        """ 根据作业ID查找数据库中作业的识别代码 """
        assignment = assignment_crud.get_assignment(db, assignmentId)
        if assignment is None:
            return validation_error_response(message="未找到对应的作业图片")
        # 识别代码
        perfect_code = assignment.extracted_code
        """ 根据作业ID查找数据库中作业的编译运行的结果 """
        image_process = image_process_crud.get_image_process_by_assignment_id(db, assignmentId)
        if image_process is None:
            return validation_error_response(message="未找到对应的作业图片的编译运行的结果")
        # 编译运行的结果
        compile_run_result = image_process.process_result
        """
            预留，等待修改编译运行的返回
        """
        # compile_run_result = compile_run_result["data"]

        """ 调用大模型进行评分，返回评分结果 """
        results = ai_run_reult_no_jsonDecoder.ai(f"{perfect_code}", compile_run_result)
        # results = ai_run_reult.ai(f"{perfect_code}",f"{run_result}")
        if results is None:
            return service_error_response(message="AI调用失败")

        # """
        # 服务器在处理请求时发生内部错误，错误类型为：
        # 尝试将一个字典（dict）对象转换为浮点数（float）时失败。因为 float() 函数仅接受字符串或实数类型的参数，不能接收字典类型的数据，导致程序抛出异常。
        # """
        # compile_run_result["score"]
        # results["score"]

        # 最终分数(规则评分和AI评分的加权融合)  final_score = rule_score × 0.35 + ai_score × 0.65

        """ 将 ai 输出结果保存在数据库中 （根据uri传递的请求参数 作业ID 查询数据库，如果该ai报告存在，则更新ai报告，否则创建新ai报告）"""
        score = score_crud.get_score_by_assignment_id(db, assignmentId)

        if score is None:
            """ ai报告保存到数据库中"""
            score_data = ScoreCreate(
                assignment_id=assignmentId,
                rule_score=float(compile_run_result["score"]),  # rule_score:基于规则评分得到的分数。
                ai_score=float(results["score"]),  # ai score:基于AI(DeepSeek)评分得到的分数。
                final_score=0.35*float(compile_run_result["score"]) + 0.65*float(results["score"]),  # final_score:最终分数(规则评分和AI评分的加权融合)
                score_details=results,
                improvement_suggestions=results["suggestions"],
                scored_at=time.time(),
            )
            score_crud.create_score(db, score_data)
        else:
            """ 查询数据库，该作业的ai报告存在，则更新ai报告 """
            score_update_data = ScoreUpdate(
                rule_score=float(compile_run_result["score"]),  # rule_score:基于规则评分得到的分数。
                ai_score=float(results["score"]),    # ai score:基于AI(DeepSeek)评分得到的分数。
                final_score=0.35*float(compile_run_result["score"]) + 0.65*float(results["score"]),  # final_score:最终分数(规则评分和AI评分的加权融合)
                score_details=results,
                improvement_suggestions=results["suggestions"],
                scored_at=time.time(),
            )
            score_crud.update_score(db, assignmentId, score_update_data)

        # 返回成功响应
        return success_response(data={
            "score": results["score"],  # 得分
            "breakdown": {
                "correctness": results["breakdown"]["correctness"],
                "standardization": results["breakdown"]["standardization"],
                "efficiency": results["breakdown"]["efficiency"],
                "readability": results["breakdown"]["readability"],
            },  # 分项得分
            "reason": results["reason"],  # 评分建议
            "suggestions": results["suggestions"],  # 改进建议
            "strengths": results["strengths"],  # 优点
            "weaknesses": results["weaknesses"],  # 缺点
        })


    except ValueError as e:
        return validation_error_response(message=str(e))
    except Exception as e:
        return service_error_response(message="服务器内部错误: "+str(e))
