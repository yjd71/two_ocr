import time

from core.core_db.crud import assignment_crud, image_process_crud
from core.core_db.database import get_db
from core.core_db.schemas import ImageProcessCreate, ImageProcessUpdate
from src.Compile_run import run_api
from fastapi import FastAPI, HTTPException, APIRouter
from common.res.response import success_response, validation_error_response, service_error_response, ApiResponse

# 获取数据库会话
db_generator = get_db()
db = next(db_generator)

# 创建路由实例，添加API前缀和标签
router = APIRouter()


@router.post("/api/assignments/{assignmentId}/Compile_run")
async def compile_run(assignmentId: int):
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
        assignment = assignment_crud.get_assignment(db, assignmentId)
        if assignment is None:
            return validation_error_response(message="未找到对应的作业图片")

        """ Compile编译 """
        """ 根据输入，判断文本是否符合规则，符合则true，不符合则false """
        success_code = assignment.extracted_code
        # success_code = """#include <iostream>
        #   using namespace std;
        #   int main() {
        #       cout << "Hello, World!" << endl;
        #       return 0;
        #   }
        #   """
        results = run_api.compile_run(success_code)
        if results is None:
            return service_error_response(message="代码编译运行失败")

        """ 编译运行结果的入库 （根据uri传递的请求参数 作业ID 查询数据库，如果该作业存在，则更新作业，否则创建新作业）"""
        image_process = image_process_crud.get_image_process_by_assignment_id(db, assignmentId)
        if image_process is None:
            """ 存储编译结果到数据库中 """
            image_process_data = ImageProcessCreate(
                assignment_id=assignmentId,
                process_step="compile_run",
                process_result=results,
                processed_at=time.time()
            )
            image_process_crud.create_image_process(db, image_process_data)
        else:
            """ 查询数据库，该作业的编译结果存在，则更新编译结果 """
            image_process_update_data = ImageProcessUpdate(
                process_step="compile_run",
                process_result=results,
            )
            image_process_crud.update_image_process(db, assignmentId, image_process_update_data)

        """ 响应, OCR 识别到的源代码文本 """
        # 返回成功响应
        return success_response(data={"language": results["data"]["language"],
                                      "codeLengthBytes": results["data"]["codeLengthBytes"],
                                      "submitTime": results["data"]["submitTime"],
                                      "evalTime": results["data"]["evalTime"],
                                      "compileSuccess": results["data"]["compileSuccess"],
                                      "output": results["data"]["output"],
                                      "error": results["data"]["error"],
                                      "score": results["data"]["score"],
                                      })

    except ValueError as e:
        return validation_error_response(message=str(e))
    except Exception as e:
        return service_error_response(message=str("请求服务器错误" + str(e)))
