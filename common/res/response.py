from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
from enum import Enum
from fastapi import status

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


# 工具函数，创建成功响应
def success_response(data: Optional[T] = None) -> tuple[ApiResponse[T], int]:
    """
    创建一个成功响应，代码为0，消息为"成功"，HTTP状态为200 OK。

    :param data: 可选的数据载荷
    :return: ApiResponse实例和HTTP状态码的元组
    """
    return (
        ApiResponse[T](
            code=ResponseCode.SUCCESS.value,
            message=ResponseMessage.SUCCESS.value,
            data=data
        ),
        status.HTTP_200_OK
    )


# 工具函数，创建参数校验失败响应
def validation_error_response(message: Optional[str] = None) -> tuple[ApiResponse[None], int]:
    """
    创建参数校验失败响应，代码为1001，自定义或默认消息，HTTP状态为400 Bad Request。

    :param message: 可选的自定义消息；默认为"参数校验失败"
    :return: ApiResponse实例和HTTP状态码的元组
    """
    msg = message if message else ResponseMessage.FAIL_VALID.value
    return (
        ApiResponse[None](
            code=ResponseCode.FAIL_VALID.value,
            message=msg,
            data=None
        ),
        status.HTTP_400_BAD_REQUEST
    )


# 工具函数，创建服务异常响应
def service_error_response(message: Optional[str] = None) -> tuple[ApiResponse[None], int]:
    """
    创建服务异常响应，代码为1002，自定义或默认消息，HTTP状态为500 Internal Server Error。

    :param message: 可选的自定义消息；默认为"服务异常"
    :return: ApiResponse实例和HTTP状态码的元组
    """
    msg = message if message else ResponseMessage.FAIL_SERVICE.value
    return (
        ApiResponse[None](
            code=ResponseCode.FAIL_SERVICE.value,
            message=msg,
            data=None
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )


# 通用工具函数，创建自定义错误响应
def error_response(code: int, message: Optional[str] = None) -> tuple[ApiResponse[None], int]:
    """
    创建自定义错误响应，指定代码，自定义或默认消息，以及适当的HTTP状态。

    :param code: 错误代码
    :param message: 可选的自定义消息；默认为"错误代码: {code}"
    :return: ApiResponse实例和HTTP状态码的元组
    """
    msg = message if message else f"错误代码: {code}"
    http_status = (
        status.HTTP_200_OK if code == ResponseCode.SUCCESS.value
        else status.HTTP_400_BAD_REQUEST if code == ResponseCode.FAIL_VALID.value
        else status.HTTP_500_INTERNAL_SERVER_ERROR if code == ResponseCode.FAIL_SERVICE.value
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return (
        ApiResponse[None](
            code=code,
            message=msg,
            data=None
        ),
        http_status
    )