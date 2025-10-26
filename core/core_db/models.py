# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='student')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    assignments = relationship("Assignment", back_populates="user")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    original_image_path = Column(String(500), nullable=False)
    processed_image_path = Column(String(500))
    extracted_code = Column(Text)
    status = Column(String(50), default='uploaded')
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    page_count = Column(Integer, default=1)

    # 关系
    user = relationship("User", back_populates="assignments")
    tasks = relationship("Task", back_populates="assignment")
    score = relationship("Score", back_populates="assignment", uselist=False)
    image_processes = relationship("ImageProcess", back_populates="assignment")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"))
    task_type = Column(String(50), nullable=False)
    status = Column(String(50), default='pending')
    result_data = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    processing_time = Column(Integer)  # 毫秒

    # 关系
    assignment = relationship("Assignment", back_populates="tasks")


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"))
    rule_score = Column(Numeric(5, 2))
    ai_score = Column(Numeric(5, 2))
    final_score = Column(Numeric(5, 2))
    score_details = Column(JSON)
    improvement_suggestions = Column(JSON)
    scored_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    assignment = relationship("Assignment", back_populates="score")


class ImageProcess(Base):
    __tablename__ = "image_processes"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"))
    process_step = Column(String(100), nullable=False)
    process_result = Column(JSON)
    confidence_score = Column(Numeric(4, 3))
    processed_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    assignment = relationship("Assignment", back_populates="image_processes")