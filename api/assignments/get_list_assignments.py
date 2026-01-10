import os
import math
from typing import Optional, List
from pathlib import Path
from sqlalchemy import desc, asc
import logging
from common.res.response import success_response, validation_error_response, service_error_response

from fastapi import Depends, APIRouter, Query
from sqlalchemy.orm import Session  # 导入 Session 类型
from core.core_db.database import get_db
import config

# 模型定义在 core.core_db.models
from core.core_db.models import Assignment, Score, ImageProcess

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由实例
router = APIRouter()


@router.get("/api/assignments")
async def get_assignment_list_api(
        page: int = Query(1, ge=1, description="页码"),
        pageSize: int = Query(10, ge=1, description="每页数量"),
        # 修改点 1: 参数变更为 likes，类型为 List[str]，支持多组条件
        likes: Optional[List[str]] = Query(None, description="模糊匹配条件列表，格式'字段:值'"),
        sortBy: str = Query("createdAt", description="排序字段: createdAt/score"),
        sortOrder: str = Query("desc", description="排序顺序: asc/desc"),
        db: Session = Depends(get_db)
):
    """
    批量查看作业列表接口
    支持：分页、模糊搜索（文件名）、排序（时间/分数）、状态计算
    """
    try:
        # 1. 参数业务校验 (对应 API 文档错误码 1004)
        if pageSize > 100:
            return validation_error_response(
                message="参数无效：pageSize 不能超过100",
            )

        # 2. 构建基础查询
        # 使用 outerjoin 关联 Score 表，以便获取分数用于排序或展示
        # 使用 outerjoin 关联 ImageProcess 表，用于判断状态
        '''query的sql语句：
            SELECT 
                -- 1. Assignment 表的所有字段 (通常用 A.* 表示)
                A.*, 
                -- 2. Score 表的 final_score 字段
                S.final_score, 
                -- 3. ImageProcess 表的 compile_success 字段
                IP.compile_success
            FROM 
                assignment AS A  -- 主表：作业表
            LEFT OUTER JOIN 
                score AS S  -- 左外连接分数表
            ON 
                A.id = S.assignment_id  -- 连接条件：作业ID = 分数表中的作业外键
            LEFT OUTER JOIN 
                image_process AS IP  -- 左外连接图像处理表
            ON 
                A.id = IP.assignment_id; -- 连接条件：作业ID = 处理表中的作业外键
        '''
        query = db.query(Assignment, Score.final_score, Assignment.status) \
            .outerjoin(Score, Assignment.id == Score.assignment_id) \
            .outerjoin(ImageProcess, Assignment.id == ImageProcess.assignment_id)

        # 3. 处理 likes 模糊匹配逻辑
        # API文档要求通用模糊匹配。
        # 优先匹配文件名和状态 (original_image_path和Assignment.status)。
        # 此处实现对文件名的数据库级模糊匹配，这是最高效的方式。
        if likes:
            for condition_str in likes:
                # 3.1 处理单个 like 参数内的 '&' (AND 关系)
                # 例如: "fileName:homework&status:已评分"
                sub_conditions = condition_str.split('&')
                for sub_condition in sub_conditions:
                    # 3.2 解析 "字段:值" 格式
                    if ':' not in sub_condition:
                        continue  # 格式错误忽略，或者可以选择报错
                    field, value = sub_condition.split(':', 1)  # 只分割第一个冒号
                    value = value.strip()
                    # 3.3 字段映射与过滤
                    # 使用 ilike 实现不区分大小写 + % 实现模糊匹配
                    if field == 'fileName':
                        # 匹配文件名 (original_image_path)
                        query = query.filter(Assignment.original_image_path.ilike(f"%{value}%"))
                    elif field == 'status':
                        # 匹配计算出的状态 (calculated_status)
                        # SQLAlchemy 允许直接对 case 表达式进行 filter
                        query = query.filter(Assignment.status.ilike(f"%{value}%"))
                    # 如果有其他字段需求，可在此扩展

        # 4. 排序逻辑
        # 确定排序方向
        sort_func = desc if sortOrder == "desc" else asc

        if sortBy == "score":
            # 按分数排序，空分数排在最后 (nullslast)
            query = query.order_by(sort_func(Score.final_score).nullslast())
        else:
            # 默认按创建时间排序
            query = query.order_by(sort_func(Assignment.uploaded_at))

        # 5. 执行分页
        total_count = query.count()
        total_pages = math.ceil(total_count / pageSize)

        # 防止页码越界
        if page > total_pages and total_count > 0:
            # 如果请求页码超出范围，可以选择返回空列表或最后一页，这里返回空列表符合常规逻辑
            records = []
        else:
            records = query.offset((page - 1) * pageSize).limit(pageSize).all()

        # 6. 数据处理与格式化
        assignments_data = []

        for record in records:
            assignment_obj = record[0]  # Assignment ORM 对象
            score_val = record[1]  # final_score 值
            status = record[2]  # 编译是否成功

            # 额外的模糊匹配：如果用户搜的是状态文本（例如"已评分"），
            # 而数据库层只过滤了文件名，这里可以做二次过滤。
            # 但为了分页准确性，通常建议仅在数据库层做过滤。
            # 此处若 key 存在且匹配到了 status 文本，则保留（如果DB层没过滤到）。
            # 鉴于性能，这里假定 DB 层过滤为主。

            # 提取文件名
            filename = os.path.basename(
                assignment_obj.original_image_path) if assignment_obj.original_image_path else "unknown"

            # 生成图片 URL 路径
            # 参考 upload_batch_api.py 的 URL 生成逻辑
            url_path = ""
            if assignment_obj.original_image_path:
                # 从配置中提取文件夹名称 "original_image"
                sub_dir_name = Path(config.img_upload_dir).name
                # 拼接 URL: /uploads/original_image/文件名
                url_path = f"/uploads/{sub_dir_name}/{filename}"

            # 处理分数类型 (Decimal -> float/int)
            final_score = float(score_val) if score_val is not None else None
            if final_score is not None and final_score.is_integer():
                final_score = int(final_score)

            assignments_data.append({
                "assignmentId": assignment_obj.id,
                "fileName": filename,
                "url": url_path,
                "status": status,
                "score": final_score,
                "createdAt": str(assignment_obj.uploaded_at),
                "updatedAt": str(assignment_obj.processed_at) if assignment_obj.processed_at else str(
                    assignment_obj.uploaded_at)
            })

        # 7. 构造响应
        return success_response(data={
            "assignments": assignments_data,
            "pagination": {
                "page": page,
                "pageSize": pageSize,
                "total": total_count,
                "totalPages": total_pages
            }
        })

    except Exception as e:
        # 捕获未知异常，返回 1002 服务异常
        return service_error_response(message=f"获取作业列表失败: {str(e)}")
