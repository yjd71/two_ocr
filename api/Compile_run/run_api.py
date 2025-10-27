from src.Compile_run import run_api
from fastapi import FastAPI, HTTPException,APIRouter
from common.res.response import success_response, validation_error_response, service_error_response, ApiResponse

# 创建路由实例，添加API前缀和标签
router = APIRouter()




@router.post("/api/assignments/{assignmentId}/Compile_run")
async def ocr_api(assignmentId: str):
    """ 进行HTTP参数绑定，前端 uri 请求数据 （作业ID）
                  根据 作业ID 查询数据库中的作业图片
              """
    """
        OCR图片识别接口，基于作业ID查询并处理图片。

        :param assignmentId: 作业ID，由前端提供
        :return: 包含OCR识别结果的响应
        """

    try:
        # 参数校验：确保assignmentId有效
        if not assignmentId or not isinstance(assignmentId, str):
            return validation_error_response(message="作业ID无效")


        # 查询数据库获取作业图片


        """ Compile编译 """
        """ 根据输入，判断文本是否符合规则，符合则true，不符合则false """

        success_code = """#include <iostream>
          using namespace std;
          int main() {
              cout << "Hello, World!" << endl;
              return 0;
          }
          """
        results = run_api.compile_run(success_code)
        if results is None:
            return service_error_response(message="OCR处理失败")


        """ 响应, OCR 识别到的源代码文本 """
        # 返回成功响应
        return success_response(data={"language": results["data"]["language"],
                                      "codeLengthBytes":results["data"]["codeLengthBytes"],
                                      "submitTime": results["data"]["submitTime"],
                                      "evalTime": results["data"]["evalTime"],
                                      "compileSuccess": results["data"]["compileSuccess"],
                                      "output": results["data"]["output"],
                                      "error": results["data"]["error"],
                                      })

    except ValueError as e:
        return validation_error_response(message=str(e))
    except Exception as e:
        return service_error_response(message="服务器内部错误")



