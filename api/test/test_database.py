import pytest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.core_db.database import get_test_db, test_engine, Base
from core.core_db.models import User
from core.core_db.crud import UserCRUD  # 只导入确定存在的类


@pytest.fixture(scope="function")
def test_db():
    """为每个测试函数创建新的数据库会话"""
    # 创建测试表
    Base.metadata.create_all(bind=test_engine)

    db_generator = get_test_db()
    db = next(db_generator)

    try:
        yield db
    finally:
        # 关闭会话
        try:
            next(db_generator)
        except StopIteration:
            pass
        # 测试结束后清空表
        Base.metadata.drop_all(bind=test_engine)


def test_user_creation(test_db):
    """测试用户创建"""
    user = UserCRUD.create_user(
        test_db,
        "test_user",
        "test@example.com",
        "testpassword",
        "student"
    )
    assert user.id is not None
    assert user.username == "test_user"
    assert user.role == "student"


def test_password_verification(test_db):
    """测试密码验证"""
    user = UserCRUD.create_user(
        test_db,
        "auth_user",
        "auth@example.com",
        "securepassword",
        "student"
    )

    # 验证正确密码
    assert UserCRUD.verify_password("securepassword", user.password_hash) == True
    # 验证错误密码
    assert UserCRUD.verify_password("wrongpassword", user.password_hash) == False


def test_simple():
    """简单测试确保pytest能发现测试用例"""
    assert 1 + 1 == 2