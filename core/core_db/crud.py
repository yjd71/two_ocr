from sqlalchemy.orm import Session
from typing import List, Optional
import bcrypt

from core.core_db.models import User, Assignment, Task, Score, ImageProcess
from core.core_db.schemas import (
    UserCreate, UserUpdate, AssignmentCreate, AssignmentUpdate,
    TaskCreate, TaskUpdate, ScoreCreate, ImageProcessCreate
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


# 实例化CRUD类
user_crud = UserCRUD()
assignment_crud = AssignmentCRUD()
task_crud = TaskCRUD()