from fastapi import FastAPI
from api.ocr_api.ocr import router as ocr_router
from api.upload_img.upload_api import router as upload_router
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
    app.include_router(ocr_router)
    app.include_router(upload_router)

    return app

