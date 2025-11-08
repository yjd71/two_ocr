from sqlalchemy.orm import Session
from typing import List, Optional
import bcrypt

from core.core_db.models import User, Assignment, Task, Score, ImageProcess
from core.core_db.schemas import (
    UserCreate, UserUpdate, AssignmentCreate, AssignmentUpdate,
    TaskCreate, TaskUpdate, ScoreCreate, ImageProcessCreate, ImageProcessUpdate
)


class UserCRUD:
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db_user = User(
            username=user.username,
            email=user.email,
            password_hash=hashed_password,
            role=user.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            update_data = user_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_user, field, value)
            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False


class AssignmentCRUD:
    @staticmethod
    def get_assignment(db: Session, assignment_id: int) -> Optional[Assignment]:
        return db.query(Assignment).filter(Assignment.id == assignment_id).first()

    @staticmethod
    def get_assignment_by_file_path(db: Session, file_path: str) -> Optional[Assignment]:
        return db.query(Assignment).filter(Assignment.original_image_path == file_path).first()

    @staticmethod
    def get_assignments_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Assignment]:
        return db.query(Assignment).filter(Assignment.user_id == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def create_assignment(db: Session, assignment: AssignmentCreate) -> Assignment:
        db_assignment = Assignment(**assignment.dict())
        db.add(db_assignment)
        db.commit()
        db.refresh(db_assignment)
        return db_assignment

    @staticmethod
    def update_assignment(db: Session, assignment_id: int, assignment_update: AssignmentUpdate) -> Optional[Assignment]:
        db_assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if db_assignment:
            update_data = assignment_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_assignment, field, value)
            db.commit()
            db.refresh(db_assignment)
        return db_assignment


class TaskCRUD:
    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[Task]:
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_tasks_by_assignment(db: Session, assignment_id: int) -> List[Task]:
        return db.query(Task).filter(Task.assignment_id == assignment_id).all()

    @staticmethod
    def create_task(db: Session, task: TaskCreate) -> Task:
        db_task = Task(**task.dict())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def create_initial_tasks(db: Session, assignment_id: int):
        """为作业创建初始处理任务"""
        task_types = ["image_processing", "ocr", "code_correction", "compilation", "scoring"]
        for task_type in task_types:
            task = TaskCreate(task_type=task_type, assignment_id=assignment_id)
            TaskCRUD.create_task(db, task)

    @staticmethod
    def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
        db_task = db.query(Task).filter(Task.id == task_id).first()
        if db_task:
            update_data = task_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_task, field, value)
            db.commit()
            db.refresh(db_task)
        return db_task


class ImageProcessCRUD:
    @staticmethod
    def get_image_process(db: Session, process_id: int) -> Optional[ImageProcess]:
        """根据ID获取图像处理记录"""
        return db.query(ImageProcess).filter(ImageProcess.id == process_id).first()

    @staticmethod
    def get_image_process_by_assignment_id(db: Session, assignment_id: int) -> Optional[ImageProcess]:
        """根据ID获取图像处理记录"""
        return db.query(ImageProcess).filter(ImageProcess.assignment_id == assignment_id).first()
    @staticmethod
    def get_image_processes_by_task(db: Session, task_id: int, skip: int = 0, limit: int = 100) -> List[ImageProcess]:
        """根据任务ID获取所有相关的图像处理记录"""
        return db.query(ImageProcess).filter(ImageProcess.task_id == task_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_image_processes_by_assignment(db: Session, assignment_id: int, skip: int = 0, limit: int = 100) -> List[
        ImageProcess]:
        """根据作业ID获取所有相关的图像处理记录"""
        return db.query(ImageProcess).filter(ImageProcess.assignment_id == assignment_id).offset(skip).limit(
            limit).all()

    @staticmethod
    def create_image_process(db: Session, image_process: ImageProcessCreate) -> ImageProcess:
        """创建新的图像处理记录"""
        db_image_process = ImageProcess(**image_process.dict())
        db.add(db_image_process)
        db.commit()
        db.refresh(db_image_process)
        return db_image_process

    @staticmethod
    def update_image_process(db: Session, process_id: int, image_process_update: ImageProcessUpdate) -> Optional[
        ImageProcess]:
        """更新图像处理记录"""
        db_image_process = db.query(ImageProcess).filter(ImageProcess.id == process_id).first()
        if db_image_process:
            update_data = image_process_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_image_process, field, value)
            db.commit()
            db.refresh(db_image_process)
        return db_image_process

    @staticmethod
    def delete_image_process(db: Session, process_id: int) -> bool:
        """删除图像处理记录"""
        db_image_process = db.query(ImageProcess).filter(ImageProcess.id == process_id).first()
        if db_image_process:
            db.delete(db_image_process)
            db.commit()
            return True
        return False

    @staticmethod
    def get_image_processes_by_status(db: Session, status: str, skip: int = 0, limit: int = 100) -> List[ImageProcess]:
        """根据状态获取图像处理记录"""
        return db.query(ImageProcess).filter(ImageProcess.status == status).offset(skip).limit(limit).all()

    @staticmethod
    def update_process_status(db: Session, process_id: int, status: str, result_path: str = None) -> Optional[
        ImageProcess]:
        """更新图像处理状态和结果路径"""
        db_image_process = db.query(ImageProcess).filter(ImageProcess.id == process_id).first()
        if db_image_process:
            db_image_process.status = status
            if result_path:
                db_image_process.result_path = result_path
            db.commit()
            db.refresh(db_image_process)
        return db_image_process


class ScoreCRUD:
    @staticmethod
    def get_score(db: Session, score_id: int) -> Optional[Score]:
        """根据ID获取评分记录"""
        return db.query(Score).filter(Score.id == score_id).first()

    @staticmethod
    def get_score_by_assignment_id(db: Session, assignment_id: int) -> Optional[Score]:
        """根据ID获取评分记录"""
        return db.query(Score).filter(Score.assignment_id == assignment_id).first()

    @staticmethod
    def get_scores_by_task(db: Session, task_id: int, skip: int = 0, limit: int = 100) -> List[Score]:
        """根据任务ID获取所有相关的评分记录"""
        return db.query(Score).filter(Score.task_id == task_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_scores_by_assignment(db: Session, assignment_id: int, skip: int = 0, limit: int = 100) -> List[Score]:
        """根据作业ID获取所有相关的评分记录"""
        return db.query(Score).filter(Score.assignment_id == assignment_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_scores_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Score]:
        """根据用户ID获取所有相关的评分记录"""
        return db.query(Score).filter(Score.user_id == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def create_score(db: Session, score: ScoreCreate) -> Score:
        """创建新的评分记录"""
        db_score = Score(**score.dict())
        db.add(db_score)
        db.commit()
        db.refresh(db_score)
        return db_score

    @staticmethod
    def update_score(db: Session, score_id: int, score_update: ScoreCreate) -> Optional[Score]:
        """更新评分记录"""
        db_score = db.query(Score).filter(Score.id == score_id).first()
        if db_score:
            update_data = score_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_score, field, value)
            db.commit()
            db.refresh(db_score)
        return db_score

    @staticmethod
    def delete_score(db: Session, score_id: int) -> bool:
        """删除评分记录"""
        db_score = db.query(Score).filter(Score.id == score_id).first()
        if db_score:
            db.delete(db_score)
            db.commit()
            return True
        return False

    @staticmethod
    def get_average_score_by_assignment(db: Session, assignment_id: int) -> Optional[float]:
        """计算作业的平均分数"""
        result = db.query(db.func.avg(Score.score)).filter(Score.assignment_id == assignment_id).scalar()
        return float(result) if result else None

    @staticmethod
    def get_average_score_by_user(db: Session, user_id: int) -> Optional[float]:
        """计算用户的平均分数"""
        result = db.query(db.func.avg(Score.score)).filter(Score.user_id == user_id).scalar()
        return float(result) if result else None

    @staticmethod
    def get_scores_by_criteria(db: Session, min_score: float = None, max_score: float = None,
                               assignment_id: int = None, user_id: int = None) -> List[Score]:
        """根据多种条件查询评分记录"""
        query = db.query(Score)

        if min_score is not None:
            query = query.filter(Score.score >= min_score)
        if max_score is not None:
            query = query.filter(Score.score <= max_score)
        if assignment_id is not None:
            query = query.filter(Score.assignment_id == assignment_id)
        if user_id is not None:
            query = query.filter(Score.user_id == user_id)

        return query.all()


# 实例化CRUD类
user_crud = UserCRUD()
assignment_crud = AssignmentCRUD()
task_crud = TaskCRUD()
image_process_crud = ImageProcessCRUD()
score_crud = ScoreCRUD()