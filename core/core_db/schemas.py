from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional, Dict, List, Any


class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "student"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssignmentBase(BaseModel):
    original_image_path: str
    page_count: int = 1


class AssignmentCreate(AssignmentBase):
    user_id: int


class AssignmentUpdate(BaseModel):
    status: Optional[str] = None
    processed_image_path: Optional[str] = None
    extracted_code: Optional[str] = None
    processed_at: Optional[datetime] = None


class AssignmentResponse(AssignmentBase):
    id: int
    user_id: int
    status: str
    uploaded_at: datetime
    processed_at: Optional[datetime]
    processed_image_path: Optional[str]
    extracted_code: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    task_type: str
    assignment_id: int


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    status: str
    result_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    processing_time: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class ScoreBase(BaseModel):
    assignment_id: int


class ScoreCreate(ScoreBase):
    rule_score: Optional[float] = None
    ai_score: Optional[float] = None
    final_score: Optional[float] = None
    score_details: Optional[Dict[str, Any]] = None
    improvement_suggestions: Optional[List[str]] = None


class ScoreUpdate(BaseModel):
    rule_score: Optional[float] = None
    ai_score: Optional[float] = None
    final_score: Optional[float] = None
    score_details: Optional[Dict[str, Any]] = None
    improvement_suggestions: Optional[List[str]] = None


class ScoreResponse(ScoreBase):
    id: int
    rule_score: Optional[float]
    ai_score: Optional[float]
    final_score: Optional[float]
    score_details: Optional[Dict[str, Any]]
    improvement_suggestions: Optional[List[str]]
    scored_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ImageProcessBase(BaseModel):
    assignment_id: int
    process_step: str


class ImageProcessCreate(ImageProcessBase):
    process_result: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None


class ImageProcessUpdate(BaseModel):
    process_result: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None


class ImageProcessResponse(ImageProcessBase):
    id: int
    process_result: Optional[Dict[str, Any]]
    confidence_score: Optional[float]
    processed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 复合响应模型
class AssignmentWithTasks(AssignmentResponse):
    tasks: List[TaskResponse] = []


class AssignmentWithDetails(AssignmentResponse):
    tasks: List[TaskResponse] = []
    score: Optional[ScoreResponse] = None
    image_processes: List[ImageProcessResponse] = []


class UserWithAssignments(UserResponse):
    assignments: List[AssignmentResponse] = []


# API响应包装器
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None


# 分页响应
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedUsers(PaginatedResponse):
    items: List[UserResponse]


class PaginatedAssignments(PaginatedResponse):
    items: List[AssignmentResponse]