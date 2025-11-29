from router import enter as router
import uvicorn

from fastapi.staticfiles import StaticFiles
from core.core_db import init_db


# 启动服务（可通过uvicorn运行）
if __name__ == "__main__":
    # 初始化数据库
    init_db.main()

    # 创建FastAPI应用实例
    # 配置CORS，允许前端跨域访问（根据需要调整）
    # 包含路由模块
    app = router.router()
    # 在FastAPI应用中添加静态文件服务来映射uploads目录
    app.mount("/uploads", StaticFiles(directory=r"C:\IT\AI\OCR\two_ocr\uploads"), name="uploads")

    uvicorn.run(app, host="127.0.0.1", port=8000)
