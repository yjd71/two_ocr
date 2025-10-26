from router import enter as router
import uvicorn

from core.core_db import init_db



# 启动服务（可通过uvicorn运行）
if __name__ == "__main__":
    # 初始化数据库
    init_db.main()

    # 创建FastAPI应用实例
    # 配置CORS，允许前端跨域访问（根据需要调整）
    # 包含路由模块
    app = router.router()

    uvicorn.run(app, host="127.0.0.1", port=8000)