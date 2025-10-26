# init_database.py
from database import engine, SessionLocal
from models import Base, User, Assignment, Task, Score, ImageProcess
import bcrypt


def init_database():
    """初始化数据库表结构"""
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成!")


def create_sample_data():
    """创建示例数据"""
    db = SessionLocal()

    try:
        # 创建示例用户
        hashed_password = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        users = [
            User(
                username="student_zhang",
                email="zhang@university.edu",
                password_hash=hashed_password,
                role="student"
            ),
            User(
                username="professor_li",
                email="li@university.edu",
                password_hash=hashed_password,
                role="teacher"
            )
        ]

        for user in users:
            db.add(user)

        db.commit()

        # 为第一个学生用户创建示例作业
        student = db.query(User).filter(User.username == "student_zhang").first()

        assignment = Assignment(
            user_id=student.id,
            original_image_path="/uploads/student_zhang/assignment1.jpg",
            status="completed",
            page_count=1
        )
        db.add(assignment)
        db.commit()

        # 创建相关任务记录
        tasks = [
            Task(
                assignment_id=assignment.id,
                task_type="image_processing",
                status="completed",
                processing_time=1500
            ),
            Task(
                assignment_id=assignment.id,
                task_type="ocr",
                status="completed",
                processing_time=3200,
                result_data={"confidence": 0.95, "char_count": 156}
            )
        ]

        for task in tasks:
            db.add(task)

        # 创建评分记录
        score = Score(
            assignment_id=assignment.id,
            rule_score=85.50,
            ai_score=82.00,
            final_score=84.50,
            score_details={
                "compile_score": 20,
                "logic_score": 65,
                "style_score": 15
            },
            improvement_suggestions=[
                "建议添加代码注释",
                "变量命名可以更具描述性"
            ]
        )
        db.add(score)

        db.commit()
        print("示例数据创建完成!")

    except Exception as e:
        db.rollback()
        print(f"创建示例数据时出错: {e}")
    finally:
        db.close()

def main():
    init_database()
    create_sample_data()

if __name__ == "__main__":
    init_database()
    create_sample_data()