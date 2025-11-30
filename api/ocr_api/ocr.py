import os
import time

from core.core_db.crud import assignment_crud
from core.core_db.schemas import AssignmentCreate, AssignmentUpdate
from src.PaddleOCR import ocr_v2
from common.res.response import success_response, validation_error_response, service_error_response, ApiResponse
from config import image_processed_path, app

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session  # 导入 Session 类型
from core.core_db.database import get_db

# 创建路由实例，添加API前缀和标签
router = APIRouter()


@router.post("/api/assignments/{assignmentId}/ocr")
async def ocr_api(assignmentId: int,
                  db: Session = Depends(get_db)  # ✅通过依赖注入获取每个请求独立的 db 会话
                  ):
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
        if not assignmentId or not isinstance(assignmentId, int):
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
        # print("res_img_path: ", res_img_path)

        """ ocr识别 """
        # 使用PaddleOCR识别 的结果
        results = ocr_v2.paddle_ocr(image, processed_image_path)
        if results is None:
            return service_error_response(message="OCR处理失败")

        """ ocr识别结果的图片入库（根据uri传递的请求参数 作业ID 查询数据库，如果该作业存在，则更新作业，否则创建新作业） """

        # 把 OCR 的 rec_texts（字符串列表）拼成一个包含换行符的源代码字符串。在内存中执行 OCR 并直接返回拼接好的源代码字符串（不写文件）。
        code_str = ocr_v2.ocr_recognition_return_string(results)

        # 合并为 string（和之前给的合并函数等价）
        # print("=== 原始 OCR 字符串 ===")
        # print(code_str)
        """ ocr识别结果的源代码字符串入库 （根据uri传递的请求参数 作业ID 查询数据库，如果该作业存在，则更新作业，否则创建新作业）"""

        # 后处理 OCR 识别出来的代码字符串，返回修正后的代码字符串。
        corrected = ocr_v2.postprocess_code(code_str, verbose=True)
        # print("\n=== 后处理后 ===")
        # print(corrected)

        """ ocr识别结果的源代码字符串后处理后入库 （根据uri传递的请求参数 作业ID 查询数据库，如果该作业存在，则更新作业，否则创建新作业）"""
        assignment_data = AssignmentUpdate(
            status="ocr",
            processed_image_path=f"{processed_image_path}",
            extracted_code=corrected,
            processed_at=time.time(),
        )
        assignment_crud.update_assignment(db, assignmentId, assignment_data)
        """ 响应, OCR 识别到的源代码文本 """
        # 返回成功响应
        return success_response(data={"recognizedCode": f"{corrected}",
                                      "processed_image_path": f"{res_img_path}",
                                      "res_image_path": f"{res_img_path}"
                                      })

    except ValueError as e:
        return validation_error_response(message=str(e))
    except Exception as e:
        return service_error_response(message=str("请求服务器错误" + str(e)))
