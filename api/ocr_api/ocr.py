from src.PaddleOCR import ocr_v2
from fastapi import FastAPI, HTTPException, APIRouter
from common.res.response import success_response, validation_error_response, service_error_response, ApiResponse

# 创建路由实例，添加API前缀和标签
router = APIRouter()


# 查询数据库获取作业图片
def get_assignment_image(assignmentId):
    pass


@router.post("/api/assignments/{assignmentId}/ocr")
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


        # 查询数据库获取作业图片
        image_data = get_assignment_image(assignmentId)
        image = '../../Data/zhangqikui/test1/IMG_20250928_222538.jpg'
        if image_data is None:
            return validation_error_response(message="未找到对应的作业图片")

        """ ocr识别 """
        # 使用PaddleOCR识别 的结果
        results = ocr_v2.paddle_ocr(image)
        # for res in result:
        #     res.save_to_img("output")

        if results is None:
            return service_error_response(message="OCR处理失败")

        """ ocr识别结果的图片入库（根据uri传递的请求参数 作业ID 查询数据库，如果该作业存在，则更新作业，否则创建新作业） """

        # 把 OCR 的 rec_texts（字符串列表）拼成一个包含换行符的源代码字符串。在内存中执行 OCR 并直接返回拼接好的源代码字符串（不写文件）。
        code_str = ocr_v2.ocr_recognition_return_string(results)

        # 合并为 string（和之前给的合并函数等价）
        print("=== 原始 OCR 字符串 ===")
        print(code_str)
        """ ocr识别结果的源代码字符串入库 （根据uri传递的请求参数 作业ID 查询数据库，如果该作业存在，则更新作业，否则创建新作业）"""

        # 后处理 OCR 识别出来的代码字符串，返回修正后的代码字符串。
        corrected = ocr_v2.postprocess_code(code_str, verbose=True)
        print("\n=== 后处理后 ===")
        print(corrected)
        """ ocr识别结果的源代码字符串后处理后入库 （根据uri传递的请求参数 作业ID 查询数据库，如果该作业存在，则更新作业，否则创建新作业）"""


        """ 响应, OCR 识别到的源代码文本 """
        # 返回成功响应
        return success_response(data={"recognizedCode": corrected})

    except ValueError as e:
        return validation_error_response(message=str(e))
    except Exception as e:
        return service_error_response(message="服务器内部错误")
