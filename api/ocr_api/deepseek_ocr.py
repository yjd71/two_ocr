import os
import time

import aiofiles
from src.DeepSeekOCR.deepseekOCR_1 import deepseek_ocr
from core.core_db.crud import assignment_crud
from core.core_db.schemas import AssignmentCreate, AssignmentUpdate
from src.PaddleOCR import ocr_v2
from fastapi import FastAPI, HTTPException, APIRouter
from common.res.response import success_response, validation_error_response, service_error_response, ApiResponse
from core.core_db.database import get_db, test_engine, Base
from pathlib import Path

# 获取数据库会话
db_generator = get_db()
db = next(db_generator)

# 创建路由实例，添加API前缀和标签
router = APIRouter()


@router.post("/api/assignments/{assignmentId}/deepseek_ocr")
async def ocr_api(assignmentId: str):
    deepseek_ocr()
    return success_response(data="ok")
