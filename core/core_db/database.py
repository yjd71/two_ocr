import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# 从环境变量获取数据库配置，并提供默认值
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '123456')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'cpp_ocr')

# 构建数据库URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 测试数据库配置（可以使用不同的数据库或添加_test后缀）
TEST_DB_NAME = os.getenv('TEST_DB_NAME', f"{DB_NAME}_test")
TEST_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 创建数据库引擎
engine = create_engine(DATABASE_URL)
test_engine = create_engine(TEST_DATABASE_URL)

# 创建Session类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base = declarative_base()

# 获取数据库会话的函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_test_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()