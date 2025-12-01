from fastapi import FastAPI

from api.AI_api.ai_api import router as ai_router
from api.ocr_api.ocr import router as ocr_router
from api.Compile_run.run_api import router as compile_run_router
from api.upload_img.upload_api import router as upload_router
from api.ocr_api.deepseek_ocr import router as deepseek_ocr_router

from api.assignments.get_assignments import router as get_assignments_router
from api.assignments.get_list_assignments import router as get_list_assignments_router
from api.assignments.delete_list_assignments import router as delete_list_assignments_router


from fastapi.middleware.cors import CORSMiddleware


def router():
    # 创建FastAPI应用实例
    app = FastAPI(
        title="OCR Service API",
        description="API for OCR recognition and related operations",
        version="1.0.0"
    )

    # 配置CORS，允许前端跨域访问（根据需要调整）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境建议限制特定域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 包含路由模块
    #  上传路由
    app.include_router(upload_router)
    #  ocr路由
    app.include_router(ocr_router)
    #  编译运行路由
    app.include_router(compile_run_router)
    #  ai报告路由
    app.include_router(ai_router)
    #  deepseek-ocr路由
    app.include_router(deepseek_ocr_router)

    #  获取单个作业路由
    app.include_router(get_assignments_router)
    # #  批量获取作业路由
    app.include_router(get_list_assignments_router)
    # #  删除单个作业路由
    # app.include_router(get_assignments_router)
    # #  批量删除作业路由
    app.include_router(delete_list_assignments_router)

    return app
