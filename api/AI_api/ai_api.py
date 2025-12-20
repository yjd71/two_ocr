import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session  # 导入 SQLAlchemy 的 Session，用于数据库会话管理

from common.res.response import success_response, validation_error_response, service_error_response
from core.core_db.database import get_db  # 导入获取数据库 Session 的依赖函数
from core.core_db.models import Assignment, Score, ImageProcess  # 导入 ORM 模型
from src.AI_report import ai_run_result_

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter()

# 定义评分权重常量
WEIGHT_RULE = 0.15  # 规则评分权重
WEIGHT_AI = 0.85  # AI评分权重


@router.post("/api/assignments/{assignment_id}/report")
async def generate_ai_report(
        assignment_id: int = Path(..., description="作业ID"),
        # 依赖注入：获取独立的数据库 Session 对象
        db: Session = Depends(get_db)
):
    """
    生成AI评分报告接口。

    该接口负责协调数据获取、AI服务调用、分数计算以及数据库的存取和更新。
    """
    try:
        # =======================
        # 1. 数据准备与校验
        # =======================

        # 1.1 查询作业信息
        # db.query(Assignment)：构建针对 Assignment 表的查询
        # .filter(Assignment.id == assignment_id)：添加过滤条件
        # .first()：执行查询并获取第一条匹配记录（一个 ORM 对象）
        assignment: Optional[Assignment] = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment:
            return validation_error_response(message="未找到对应的作业数据")

        if not assignment.extracted_code:
            return validation_error_response(message="该作业尚未完成OCR识别，无法评分")

        # 1.2 查询编译运行结果 (ImageProcess 表)
        # 查找与当前 Assignment 关联的 ImageProcess 记录
        image_process: Optional[ImageProcess] = db.query(ImageProcess).filter(
            ImageProcess.assignment_id == assignment_id).first()
        if not image_process:
            return validation_error_response(message="未找到编译运行结果，请先进行编译检查")

        # 1.3 解析编译结果
        compile_result_data = _parse_compile_result(image_process.process_result)

        # 获取规则评分
        rule_score = float(compile_result_data.get("score", 0))

        # =======================
        # 2. 调用 AI 服务
        # =======================
        logger.info(f"开始调用AI服务，AssignmentID: {assignment_id}")

        # 调用外部 AI 模块进行分析
        ai_result = ai_run_reult_no_jsonDecoder.ai(
            perfect_code=assignment.extracted_code,
            run_result=compile_result_data
        )

        # 2.1 AI 调用失败处理
        if not ai_result or ai_result.get("score") is None:
            # AI 调用失败，更新 Assignment 状态为“评分失败”
            assignment.status = "评分失败"
            assignment.processed_at = datetime.now()
            # 提交事务：将 Assignment 状态的变更持久化到数据库
            db.commit()
            return service_error_response(message="AI服务调用失败或返回数据异常")

        # =======================
        # 3. 分数计算与数据处理
        # =======================
        try:
            ai_score_val = float(ai_result["score"])

            # 计算加权总分
            final_score = (rule_score * WEIGHT_RULE) + (ai_score_val * WEIGHT_AI)
            final_score = round(final_score, 1)

            # 提取 AI 结果中的详情和建议
            breakdown = ai_result.get("breakdown", {})
            suggestions = ai_result.get("suggestions", [])

        except (ValueError, TypeError) as e:
            logger.error(f"分数计算数据类型错误: {e}")
            return service_error_response(message="评分数据解析错误")

        # =======================
        # 4. 数据库更新 (事务处理)
        # =======================

        # 4.1 查询是否已存在评分记录 (用于判断是创建还是更新)
        # 查询 Score 表中是否存在与该作业关联的记录
        existing_score: Optional[Score] = db.query(Score).filter(Score.assignment_id == assignment_id).first()

        current_time = datetime.now()

        if existing_score:
            # --- 更新现有记录 (UPDATE) ---
            # 如果存在，直接修改 Score ORM 对象的属性
            existing_score.rule_score = rule_score
            existing_score.ai_score = ai_score_val
            existing_score.final_score = final_score
            existing_score.score_details = ai_result  # 存储完整的 AI 返回数据
            existing_score.improvement_suggestions = suggestions
            existing_score.scored_at = current_time
        else:
            # --- 创建新记录 (INSERT) ---
            # 如果不存在，创建新的 Score ORM 实例
            new_score = Score(
                assignment_id=assignment_id,
                rule_score=rule_score,
                ai_score=ai_score_val,
                final_score=final_score,
                score_details=ai_result,
                improvement_suggestions=suggestions,
                scored_at=current_time
            )
            # db.add()：将新创建的 ORM 对象添加到 Session 中，标记为待插入
            db.add(new_score)

        # 4.2 更新作业主表状态
        # 无论 Score 是新增还是更新，都更新 Assignment 表的状态
        assignment.status = "已评分"
        assignment.processed_at = current_time

        # 4.3 提交事务
        # db.commit()：执行 Session 中所有挂起的 INSERT 和 UPDATE 操作，完成整个事务
        db.commit()
        # db.refresh(assignment)：可选操作，确保 Assignment 对象的状态是最新提交后的状态
        db.refresh(assignment)

        # =======================
        # 5. 返回响应
        # =======================
        return success_response(data={
            "score": final_score,
            "rule_score": rule_score,
            "ai_score": ai_score_val,
            "breakdown": {
                "correctness": breakdown.get("correctness", 0),
                "standardization": breakdown.get("standardization", 0),
                "efficiency": breakdown.get("efficiency", 0),
                "readability": breakdown.get("readability", 0),
            },
            "reason": ai_result.get("reason", ""),
            "suggestions": suggestions,
            "strengths": ai_result.get("strengths", []),
            "weaknesses": ai_result.get("weaknesses", []),
            "generatedAt": str(current_time)
        })

    except Exception as e:
        # 发生未知异常时，必须进行回滚操作，释放数据库锁并恢复会话状态
        db.rollback()
        logger.error(f"评分接口发生异常: {str(e)}", exc_info=True)
        return service_error_response(message=f"服务器内部错误: {str(e)}")


def _parse_compile_result(process_result: Any) -> Dict:
    """
    辅助函数：安全解析 ImageProcess 中的 process_result 字段
    处理该字段可能是 JSON 字符串或 Python 字典的情况
    """
    if process_result is None:
        return {}

    if isinstance(process_result, dict):
        return process_result

    if isinstance(process_result, str):
        try:
            return json.loads(process_result)
        except json.JSONDecodeError:
            logger.warning("编译结果字符串无法解析为 JSON")
            return {}

    return {}
