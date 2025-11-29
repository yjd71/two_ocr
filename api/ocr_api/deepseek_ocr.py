from src.DeepSeekOCR.deepseekOCR_1 import deepseek_ocr
import os
import time
import aiofiles
from core.core_db.crud import assignment_crud
from core.core_db.schemas import AssignmentCreate, AssignmentUpdate
from src.PaddleOCR import ocr_v2
from fastapi import FastAPI, HTTPException, APIRouter
from common.res.response import success_response, validation_error_response, service_error_response, ApiResponse
from core.core_db.database import get_db, test_engine, Base
from pathlib import Path
from config import image_processed_path, app

# 获取数据库会话
db_generator = get_db()
db = next(db_generator)

# 创建路由实例，添加API前缀和标签
router = APIRouter()


@router.post("/api/assignments/{assignmentId}/deepseek_ocr")
async def ocr_api(assignmentId: str):
    """ 进行HTTP参数绑定，前端 uri 请求数据 （作业ID）
                  根据 作业ID 查询数据库中的作业图片
              """
    """
        OCR图片识别接口，基于作业ID查询并处理图片。

        :param assignmentId: 作业ID，由前端提供
        :return: 包含OCR识别结果的响应
        """
    # print("ocr_api运行成功:",assignmentId)
    # return success_response(data={"recognizedCode":assignmentId})

    try:
        # 参数校验：确保assignmentId有效
        if not assignmentId or not isinstance(assignmentId, str):
            return validation_error_response(message="作业ID无效")

        """ 根据作业ID，查询数据库的作业地址，获取作业图片 （where file_path == original_image_path） """
        """ 先根据file_path查询数据库中是否存在该图片，（where file_path == original_image_path） """
        assignment = assignment_crud.get_assignment(db, assignmentId)
        if assignment is None:
            return validation_error_response(message="未找到对应的作业图片")

        # 拿到图片路径的中的图片名称
        image = f"{assignment.original_image_path}"
        filename = os.path.splitext(os.path.basename(assignment.original_image_path))
        filename = f"{filename[0]}{filename[1]}"
        save_dir = image_processed_path
        os.makedirs(save_dir, exist_ok=True)
        # 构建文件保存路径
        processed_image_path = save_dir + filename

        #  uploads 目录映射到一个静态 URL, http://127.0.0.1:8000/uploads/processed image.jpg
        if "uploads" in processed_image_path:
            res_img_path = "uploads" + processed_image_path.split("uploads")[1].replace("\\", "/")
        else:
            res_img_path = processed_image_path.replace("\\", "/")
        # print(filename)  # 输出：uploads/original_image/IMG_20250928_220327.jpg
        res_img_path = app['static_url_path'] + res_img_path

        output_path = './output'
        """ ocr识别 """
        res = deepseek_ocr(image, output_path)

        """ ocr识别结果的源代码字符串后处理后入库 （根据uri传递的请求参数 作业ID 查询数据库，如果该作业存在，则更新作业，否则创建新作业）"""
        assignment_data = AssignmentUpdate(
            status="ocr",
            processed_image_path="",
            extracted_code=res,
            processed_at=time.time(),
        )
        assignment_crud.update_assignment(db, assignmentId, assignment_data)
        """ 响应, OCR 识别到的源代码文本 """
        # 返回成功响应
        return success_response(data={"recognizedCode": f"{res}",
                                      "processed_image_path": "",
                                      "res_image_path": ""
                                      })

    except ValueError as e:
        return validation_error_response(message=str(e))
    except Exception as e:
        return service_error_response(message=str("请求服务器错误" + str(e)))

