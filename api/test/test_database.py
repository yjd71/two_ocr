import pytest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.core_db.database import get_test_db, test_engine, Base
from core.core_db.models import User
from core.core_db.crud import user_crud
from core.core_db.schemas import UserCreate
import bcrypt


@pytest.fixture(scope="function")
def test_db():
    """为每个测试函数创建新的数据库会话"""
    # 创建测试表 - 这是关键步骤！
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
        # 测试结束后可以选择是否清空表
        # Base.metadata.drop_all(bind=test_engine)  # 注释掉这行，保留表结构


def test_user_creation(test_db):
    """测试用户创建"""
    # 使用唯一用户名避免冲突
    import random
    unique_id = random.randint(1000, 9999)

    user_data = UserCreate(
        username=f"test_user_{unique_id}",
        email=f"test_{unique_id}@example.com",
        password="testpassword",
        role="student"
    )

    user = user_crud.create_user(test_db, user_data)

    assert user.id is not None
    assert user.username == f"test_user_{unique_id}"
    assert user.email == f"test_{unique_id}@example.com"
    assert user.role == "student"
    # 验证密码已被哈希
    assert user.password_hash != "testpassword"
    assert bcrypt.checkpw("testpassword".encode('utf-8'), user.password_hash.encode('utf-8'))


def test_get_user_by_id(test_db):
    """测试根据ID获取用户"""
    # 先创建用户
    import random
    unique_id = random.randint(1000, 9999)

    user_data = UserCreate(
        username=f"test_user_{unique_id}",
        email=f"test_{unique_id}@example.com",
        password="password123",
        role="teacher"
    )
    created_user = user_crud.create_user(test_db, user_data)

    # 根据ID查询用户
    found_user = user_crud.get_user(test_db, created_user.id)

    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.username == f"test_user_{unique_id}"


def test_get_user_by_username(test_db):
    """测试根据用户名获取用户"""
    import random
    unique_id = random.randint(1000, 9999)

    # 先创建用户
    user_data = UserCreate(
        username=f"unique_user_{unique_id}",
        email=f"unique_{unique_id}@example.com",
        password="password123",
        role="student"
    )
    user_crud.create_user(test_db, user_data)

    # 根据用户名查询用户
    found_user = user_crud.get_user_by_username(test_db, f"unique_user_{unique_id}")

    assert found_user is not None
    assert found_user.username == f"unique_user_{unique_id}"
    assert found_user.email == f"unique_{unique_id}@example.com"


def test_get_users(test_db):
    """测试获取用户列表"""
    import random

    # 创建多个用户
    users_data = [
        UserCreate(
            username=f"list_user_{random.randint(10000, 99999)}",
            email=f"list_{random.randint(10000, 99999)}@example.com",
            password="pass",
            role="student"
        )
        for i in range(3)
    ]

    for user_data in users_data:
        user_crud.create_user(test_db, user_data)

    # 获取用户列表
    users = user_crud.get_users(test_db, skip=0, limit=100)

    assert len(users) >= 3


def test_update_user(test_db):
    """测试更新用户信息"""
    from core.core_db.schemas import UserUpdate
    import random
    unique_id = random.randint(1000, 9999)

    # 先创建用户
    user_data = UserCreate(
        username=f"update_test_{unique_id}",
        email=f"update_{unique_id}@example.com",
        password="oldpassword",
        role="student"
    )
    created_user = user_crud.create_user(test_db, user_data)

    # 更新用户信息
    update_data = UserUpdate(
        email=f"updated_{unique_id}@example.com",
        role="teacher"
    )

    updated_user = user_crud.update_user(test_db, created_user.id, update_data)

    assert updated_user is not None
    assert updated_user.email == f"updated_{unique_id}@example.com"
    assert updated_user.role == "teacher"
    assert updated_user.username == f"update_test_{unique_id}"  # 用户名应该保持不变


def test_delete_user(test_db):
    """测试删除用户"""
    import random
    unique_id = random.randint(1000, 9999)

    # 先创建用户
    user_data = UserCreate(
        username=f"delete_test_{unique_id}",
        email=f"delete_{unique_id}@example.com",
        password="password123",
        role="student"
    )
    created_user = user_crud.create_user(test_db, user_data)

    # 删除用户
    result = user_crud.delete_user(test_db, created_user.id)

    assert result is True

    # 验证用户已被删除
    deleted_user = user_crud.get_user(test_db, created_user.id)
    assert deleted_user is None


def test_password_hashing(test_db):
    """测试密码哈希功能"""
    import random
    unique_id = random.randint(1000, 9999)

    user_data = UserCreate(
        username=f"password_test_{unique_id}",
        email=f"pass_{unique_id}@example.com",
        password="my_secure_password",
        role="student"
    )

    user = user_crud.create_user(test_db, user_data)

    # 验证密码哈希正确
    assert bcrypt.checkpw("my_secure_password".encode('utf-8'), user.password_hash.encode('utf-8'))

    # 验证错误密码不匹配
    assert not bcrypt.checkpw("wrong_password".encode('utf-8'), user.password_hash.encode('utf-8'))


def test_simple():
    """简单测试确保pytest能发现测试用例"""
    assert 1 + 1 == 2


if __name__ == '__main__':
    pytest.main([__file__, "-v"])