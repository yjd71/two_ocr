from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
from enum import Enum
from fastapi import status
from fastapi.responses import JSONResponse  # 新增

# 泛型类型变量，用于data字段
T = TypeVar("T")


# 枚举，用于业务代码
class ResponseCode(Enum):
    SUCCESS = 0  # SuccessCode (成功)
    FAIL_VALID = 1001  # FailValidCode (参数校验失败)
    FAIL_SERVICE = 1002  # FailServiceCode (服务异常)


# 枚举，用于对应的消息（自动映射）
class ResponseMessage(Enum):
    SUCCESS = "成功"
    FAIL_VALID = "参数校验失败"
    FAIL_SERVICE = "服务异常"


# Pydantic模型，用于全局响应结构
class ApiResponse(BaseModel, Generic[T]):
    code: int
    message: str
    data: Optional[T] = None


# 工具函数，创建成功响应 —— 返回 JSONResponse（body 为对象）
def success_response(data: Optional[T] = None) -> JSONResponse:
    """
    创建一个成功响应，code=0，message="成功"，HTTP状态为200。
    返回 JSONResponse，body 是标准对象（非数组）。
    """
    resp = ApiResponse[T](
        code=ResponseCode.SUCCESS.value,
        message=ResponseMessage.SUCCESS.value,
        data=data
    )
    return JSONResponse(content=resp.dict(), status_code=status.HTTP_200_OK)


# 工具函数，创建参数校验失败响应 —— 返回 JSONResponse（body 为对象）
def validation_error_response(message: Optional[str] = None) -> JSONResponse:
    """
    创建参数校验失败响应，code=1001，HTTP状态为400。
    """
    msg = message if message else ResponseMessage.FAIL_VALID.value
    resp = ApiResponse[None](
        code=ResponseCode.FAIL_VALID.value,
        message=msg,
        data=None
    )
    return JSONResponse(content=resp.dict(), status_code=status.HTTP_400_BAD_REQUEST)


# 工具函数，创建服务异常响应 —— 返回 JSONResponse（body 为对象）
def service_error_response(message: Optional[str] = None) -> JSONResponse:
    """
    创建服务异常响应，code=1002，HTTP状态为500。
    """
    msg = message if message else ResponseMessage.FAIL_SERVICE.value
    resp = ApiResponse[None](
        code=ResponseCode.FAIL_SERVICE.value,
        message=msg,
        data=None
    )
    return JSONResponse(content=resp.dict(), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 通用工具函数，创建自定义错误响应 —— 返回 JSONResponse（body 为对象）
def error_response(code: int, message: Optional[str] = None) -> JSONResponse:
    """
    创建自定义错误响应并映射合适的 HTTP 状态码。
    """
    msg = message if message else f"错误代码: {code}"
    http_status = (
        status.HTTP_200_OK if code == ResponseCode.SUCCESS.value
        else status.HTTP_400_BAD_REQUEST if code == ResponseCode.FAIL_VALID.value
        else status.HTTP_500_INTERNAL_SERVER_ERROR if code == ResponseCode.FAIL_SERVICE.value
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    resp = ApiResponse[None](
        code=code,
        message=msg,
        data=None
    )
    return JSONResponse(content=resp.dict(), status_code=http_status)
