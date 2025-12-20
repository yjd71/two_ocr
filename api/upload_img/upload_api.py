import logging

from common.res.response import success_response, validation_error_response, service_error_response, ApiResponse

from fastapi import UploadFile, File, Form
from pathlib import Path
from typing import Optional

import aiofiles

from core.core_db.crud import user_crud, assignment_crud

from core.core_db.schemas import AssignmentCreate, AssignmentBase
import config

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session  # 导入 Session 类型
from core.core_db.database import get_db

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由实例，添加API前缀和标签
router = APIRouter()

"""
    FastAPI 利用 Form 和 File 依赖解析 multipart/form-data 数据：
    file: Optional[UploadFile] = File(None)：从 form-data 中提取 file 字段，封装为 UploadFile 对象，包含文件内容、文件名、MIME 类型等。
"""


@router.post("/api/assignments")
async def ocr_api(file: Optional[UploadFile] = File(None),
                  db: Session = Depends(get_db)  # ✅通过依赖注入获取每个请求独立的 db 会话
                  ):
    """
    上传作业文件（支持图片或源码文件），从上传文件中提取文件名，服务端存储文件并返回唯一assignmentId。

    请求形式：multipart/form-data
    - file: 上传的文件内容，必填，文件名从 file.filename 提取

    响应：
    - 成功时返回 assignmentId 和 fileName（从 file.filename 获取）
    - 失败时返回错误码和错误信息

    响应示例：
    {
        "code": 0,
        "message": "成功",
        "data": {
            "assignmentId": "abcd1234",
            "fileName": "homework1.jpg"
        }
    }
    """
    try:
        # 参数校验：检查file是否提供（API文档中为必填字段）
        if file is None:
            raise validation_error_response("缺少必填字段：file")

        # 从UploadFile对象中提取文件名
        fileName = file.filename
        if not fileName or not fileName.strip():
            raise validation_error_response("文件名不能为空或仅包含空格")

        # 生成唯一的assignment_path_id
        assignment_path_id = str(Path(fileName).stem)
        # TODO: 待完成文件路径为：40_20251029092628_103_33.jpg，作业id加文图片名字
        # safe_filename = f"{assignment.id}_{assignment_path_id}"

        # 提取文件扩展名（如 '.jpg' 或 '.cpp'）
        ext = Path(fileName).suffix

        # 使用assignment_path_id + 扩展名作为存储文件名，避免冲突
        safe_name = f"{assignment_path_id}{ext}"

        # 定义初始图片上传目录
        upload_dir = Path(config.img_upload_dir)
        upload_dir.mkdir(exist_ok=True)

        # 构建文件保存路径
        file_path = upload_dir / safe_name
        # print("upload_dir:", upload_dir);print("safe_name:", safe_name);print("file_path:", file_path)

        # 异步写入文件内容
        async with aiofiles.open(file_path, 'wb') as out_file:
            # 读取前端上传的文件内容（二进制数据）
            content = await file.read()
            # 写入到本地文件
            await out_file.write(content)

        """ 先根据file_path查询数据库中是否存在该图片，（where file_path == original_image_path） """
        assignment = assignment_crud.get_assignment_by_file_path(db, f"{file_path}")
        if assignment is None:
            """ 存储图片到数据库中（ file_path -> original_image_path） """
            assignment_data = AssignmentCreate(
                original_image_path=f"{file_path}",
                status="上传成功",
                user_id=1,
            )
            created_assignment = assignment_crud.create_assignment(db, assignment_data)
            """ 查询数据库，找到上传图片的id """
            assignment_id = created_assignment.id
        else:
            """ 查询数据库，找到上传图片的id """
            assignment_id = assignment.id

        # 准备响应数据，回显从file.filename获取的fileName
        data = {
            "assignmentId": assignment_id,
            "fileName": fileName,  # 回显从file.filename获取的文件名
        }

        # 返回成功响应
        return success_response(data=data)

    except ValueError as e:
        # 参数校验错误
        return validation_error_response(message=str(e))

    except Exception as e:
        # 如果发生异常，应该回滚事务以防止数据库会话被污染。
        # db.rollback() # 生产环境中，如果异常发生在 db.commit() 之前，应添加 db.rollback()
        # 发生未知异常时，必须进行回滚操作，释放数据库锁并恢复会话状态
        db.rollback()
        logger.error(f"上传接口发生异常: {str(e)}", exc_info=True)
        return service_error_response(message=str("请求服务器错误" + str(e)))
