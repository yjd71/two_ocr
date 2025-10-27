# manual_test_crud.py
import sys
import os
import random
import string

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.core_db.database import get_test_db, test_engine, Base
from core.core_db.crud import user_crud, assignment_crud, task_crud
from core.core_db.schemas import (
    UserCreate, UserUpdate, AssignmentCreate, AssignmentUpdate,
    TaskCreate, TaskUpdate
)
from core.core_db.models import User, Assignment, Task
import bcrypt


def generate_random_string(length=8):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def test_user_crud_operations(db, delete_after_test=False):
    """测试用户CRUD操作"""
    print("=" * 50)
    print("测试用户CRUD操作")
    print("=" * 50)

    try:
        # 1. 创建用户
        random_suffix = generate_random_string()
        user_data = UserCreate(
            username=f"test_user_{random_suffix}",
            email=f"test_{random_suffix}@example.com",
            password="testpassword123",
            role="student"
        )

        print("1. 创建用户:")
        print(f"   输入数据: {user_data.dict()}")
        created_user = user_crud.create_user(db, user_data)
        print(f"   创建成功: ID={created_user.id}, 用户名={created_user.username}, 邮箱={created_user.email}")
        print(f"   密码已哈希: {created_user.password_hash != 'testpassword123'}")
        print()

        # 2. 根据ID查询用户
        print("2. 根据ID查询用户:")
        found_user = user_crud.get_user(db, created_user.id)
        if found_user:
            print(f"   查询成功: ID={found_user.id}, 用户名={found_user.username}")
        else:
            print("   查询失败: 用户未找到")
        print()

        # 3. 根据用户名查询用户
        print("3. 根据用户名查询用户:")
        found_by_username = user_crud.get_user_by_username(db, created_user.username)
        if found_by_username:
            print(f"   查询成功: ID={found_by_username.id}, 用户名={found_by_username.username}")
        else:
            print("   查询失败: 用户未找到")
        print()

        # 4. 查询用户列表
        print("4. 查询用户列表:")
        users = user_crud.get_users(db, limit=5)
        print(f"   找到 {len(users)} 个用户")
        for i, user in enumerate(users[:3]):  # 只显示前3个
            print(f"     {i + 1}. ID={user.id}, 用户名={user.username}")
        if len(users) > 3:
            print(f"     ... 还有 {len(users) - 3} 个用户")
        print()

        # 5. 更新用户
        print("5. 更新用户:")
        update_data = UserUpdate(
            email=f"updated_{random_suffix}@example.com",
            role="teacher"
        )
        print(f"   更新数据: {update_data.dict(exclude_unset=True)}")
        updated_user = user_crud.update_user(db, created_user.id, update_data)
        if updated_user:
            print(f"   更新成功: 邮箱={updated_user.email}, 角色={updated_user.role}")
        else:
            print("   更新失败: 用户未找到")
        print()

        # 6. 验证密码
        print("6. 验证密码:")
        password_correct = bcrypt.checkpw(
            "testpassword123".encode('utf-8'),
            created_user.password_hash.encode('utf-8')
        )
        print(f"   正确密码验证: {'成功' if password_correct else '失败'}")

        password_wrong = bcrypt.checkpw(
            "wrongpassword".encode('utf-8'),
            created_user.password_hash.encode('utf-8')
        )
        print(f"   错误密码验证: {'失败' if not password_wrong else '意外成功'}")
        print()

        # 7. 删除用户（可选）
        if delete_after_test:
            print("7. 删除用户:")
            delete_result = user_crud.delete_user(db, created_user.id)
            print(f"   删除操作: {'成功' if delete_result else '失败'}")

            # 验证删除
            deleted_user = user_crud.get_user(db, created_user.id)
            print(f"   验证删除: {'用户已删除' if deleted_user is None else '用户仍然存在'}")
            print()
            return None
        else:
            print("7. 用户保留（供后续测试使用）")
            print()
            return created_user.id  # 返回用户ID供后续测试使用

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_assignment_crud_operations(db, user_id, delete_after_test=False):
    """测试作业CRUD操作"""
    if user_id is None:
        print("用户ID为空，跳过作业测试")
        return None

    print("=" * 50)
    print("测试作业CRUD操作")
    print("=" * 50)

    try:
        # 1. 创建作业
        assignment_data = AssignmentCreate(
            original_image_path=f"/images/test_{generate_random_string()}.jpg",
            page_count=3,
            user_id=user_id
        )

        print("1. 创建作业:")
        print(f"   输入数据: {assignment_data.dict()}")
        created_assignment = assignment_crud.create_assignment(db, assignment_data)
        print(f"   创建成功: ID={created_assignment.id}, 图片路径={created_assignment.original_image_path}")
        print()

        # 2. 根据ID查询作业
        print("2. 根据ID查询作业:")
        found_assignment = assignment_crud.get_assignment(db, created_assignment.id)
        if found_assignment:
            print(f"   查询成功: ID={found_assignment.id}, 状态={found_assignment.status}")
        else:
            print("   查询失败: 作业未找到")
        print()

        # 3. 根据用户ID查询作业
        print("3. 根据用户ID查询作业:")
        user_assignments = assignment_crud.get_assignments_by_user(db, user_id)
        print(f"   用户 {user_id} 的作业数量: {len(user_assignments)}")
        for i, assignment in enumerate(user_assignments):
            print(f"     {i + 1}. ID={assignment.id}, 图片路径={assignment.original_image_path}")
        print()

        # 4. 更新作业
        print("4. 更新作业:")
        update_data = AssignmentUpdate(
            status="processed",
            processed_image_path=f"/processed/images/test_{generate_random_string()}.jpg",
            extracted_code="print('Hello World')"
        )
        print(f"   更新数据: {update_data.dict(exclude_unset=True)}")
        updated_assignment = assignment_crud.update_assignment(db, created_assignment.id, update_data)
        if updated_assignment:
            print(f"   更新成功: 状态={updated_assignment.status}, 处理图片={updated_assignment.processed_image_path}")
        else:
            print("   更新失败: 作业未找到")
        print()

        # 5. 删除作业（可选）
        if delete_after_test:
            print("5. 删除作业:")
            # 注意：由于外键约束，需要先删除相关的任务
            assignment_tasks = task_crud.get_tasks_by_assignment(db, created_assignment.id)
            for task in assignment_tasks:
                db.delete(task)
            db.commit()

            # 现在可以删除作业
            db.delete(created_assignment)
            db.commit()
            print("   删除成功")
            print()
            return None
        else:
            print("5. 作业保留（供后续测试使用）")
            print()
            return created_assignment.id  # 返回作业ID供后续测试使用

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_task_crud_operations(db, assignment_id, delete_after_test=False):
    """测试任务CRUD操作"""
    if assignment_id is None:
        print("作业ID为空，跳过任务测试")
        return None

    print("=" * 50)
    print("测试任务CRUD操作")
    print("=" * 50)

    try:
        # 1. 创建任务
        task_data = TaskCreate(
            task_type="ocr",
            assignment_id=assignment_id
        )

        print("1. 创建任务:")
        print(f"   输入数据: {task_data.dict()}")
        created_task = task_crud.create_task(db, task_data)
        print(f"   创建成功: ID={created_task.id}, 任务类型={created_task.task_type}")
        print()

        # 2. 根据ID查询任务
        print("2. 根据ID查询任务:")
        found_task = task_crud.get_task(db, created_task.id)
        if found_task:
            print(f"   查询成功: ID={found_task.id}, 状态={found_task.status}")
        else:
            print("   查询失败: 任务未找到")
        print()

        # 3. 根据作业ID查询任务
        print("3. 根据作业ID查询任务:")
        assignment_tasks = task_crud.get_tasks_by_assignment(db, assignment_id)
        print(f"   作业 {assignment_id} 的任务数量: {len(assignment_tasks)}")
        for i, task in enumerate(assignment_tasks):
            print(f"     {i + 1}. ID={task.id}, 类型={task.task_type}, 状态={task.status}")
        print()

        # 4. 更新任务
        print("4. 更新任务:")
        update_data = TaskUpdate(
            status="completed",
            result_data={"text": "识别出的文本内容", "confidence": 0.95},
            processing_time=1500
        )
        print(f"   更新数据: {update_data.dict(exclude_unset=True)}")
        updated_task = task_crud.update_task(db, created_task.id, update_data)
        if updated_task:
            print(f"   更新成功: 状态={updated_task.status}, 处理时间={updated_task.processing_time}ms")
        else:
            print("   更新失败: 任务未找到")
        print()

        # 5. 创建初始任务组
        print("5. 为作业创建初始任务组:")
        task_crud.create_initial_tasks(db, assignment_id)
        all_tasks = task_crud.get_tasks_by_assignment(db, assignment_id)
        print(f"   作业 {assignment_id} 现在有 {len(all_tasks)} 个任务:")
        for i, task in enumerate(all_tasks):
            print(f"     {i + 1}. ID={task.id}, 类型={task.task_type}, 状态={task.status}")
        print()

        # 6. 删除任务（可选）
        if delete_after_test:
            print("6. 删除任务:")
            # 删除所有相关任务
            for task in all_tasks:
                db.delete(task)
            db.commit()
            print("   删除成功")
            print()
            return None
        else:
            print("6. 任务保留")
            print()
            return created_task.id

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_all_crud_operations(cleanup_after_test=True):
    """测试所有CRUD操作"""
    print("开始测试所有CRUD操作...")
    print()

    # 确保数据库表存在
    try:
        Base.metadata.create_all(bind=test_engine)
        print("✅ 数据库表已创建/存在")
    except Exception as e:
        print(f"❌ 数据库表创建失败: {e}")
        return

    print()

    # 获取数据库会话
    db_generator = get_test_db()
    db = next(db_generator)

    try:
        # 测试用户CRUD（不删除用户，供后续测试使用）
        user_id = test_user_crud_operations(db, delete_after_test=False)

        # 测试作业CRUD（需要用户ID）
        assignment_id = test_assignment_crud_operations(db, user_id, delete_after_test=False)

        # 测试任务CRUD（需要作业ID）
        task_id = test_task_crud_operations(db, assignment_id, delete_after_test=False)

        # 如果需要清理，按正确顺序删除数据
        if cleanup_after_test:
            print("=" * 50)
            print("清理测试数据")
            print("=" * 50)

            # 按正确顺序删除：任务 → 作业 → 用户
            if assignment_id:
                # 删除所有相关任务
                assignment_tasks = task_crud.get_tasks_by_assignment(db, assignment_id)
                for task in assignment_tasks:
                    db.delete(task)
                db.commit()
                print(f"✅ 删除了 {len(assignment_tasks)} 个任务")

                # 删除作业
                assignment_to_delete = assignment_crud.get_assignment(db, assignment_id)
                if assignment_to_delete:
                    db.delete(assignment_to_delete)
                    db.commit()
                    print(f"✅ 删除了作业 ID={assignment_id}")

            # 删除用户
            if user_id:
                user_to_delete = user_crud.get_user(db, user_id)
                if user_to_delete:
                    db.delete(user_to_delete)
                    db.commit()
                    print(f"✅ 删除了用户 ID={user_id}")

            print("✅ 所有测试数据已清理")

        print("=" * 50)
        print("测试总结")
        print("=" * 50)
        print(f"用户测试: {'完成' if user_id else '失败'}")
        print(f"作业测试: {'完成' if assignment_id else '失败'}")
        print(f"任务测试: {'完成' if task_id else '失败'}")

        if user_id and assignment_id and task_id:
            print("🎉 所有CRUD操作测试成功!")
            if not cleanup_after_test:
                print(f"📝 测试数据保留 - 用户ID: {user_id}, 作业ID: {assignment_id}")
        else:
            print("❌ 部分测试失败，请检查错误信息")

    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            next(db_generator)
        except StopIteration:
            pass


def test_without_cleanup():
    """运行测试但不清理数据，用于检查数据库中的实际数据"""
    print("运行测试（不清理数据）...")
    print("测试数据将保留在数据库中供检查")
    print()
    test_all_crud_operations(cleanup_after_test=False)


if __name__ == "__main__":
    # 默认运行测试并清理数据
    test_all_crud_operations(cleanup_after_test=True)

    print("\n" + "=" * 60)
    print("如需查看数据库中的实际数据，请取消下面一行的注释:")
    print("# test_without_cleanup()")
    print("=" * 60)