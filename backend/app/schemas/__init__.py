"""Pydantic schemas for API request/response validation."""

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import JobStatus, PipelineStatus, UserRole, ValidationStatus


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: Optional[str] = None
    remember_me: bool = False


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=4, max_length=10)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: UserRole = UserRole.DEVELOPER


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime


class UserUpdateRoleRequest(BaseModel):
    role: UserRole
    is_active: Optional[bool] = None


class PipelineCreate(BaseModel):
    name: str
    path: str
    project: Optional[str] = None
    description: Optional[str] = None


class PipelineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    path: str
    project: Optional[str]
    description: Optional[str]
    status: PipelineStatus
    python_file_path: Optional[str]
    created_at: datetime
    updated_at: datetime


class PipelineDetailResponse(PipelineResponse):
    snaplogic_json_path: Optional[str] = None
    snaplogic_xml_path: Optional[str] = None
    upload_batch_id: Optional[str] = None
    python_code: Optional[str] = None
    snaplogic_json_content: Optional[str] = None
    snaplogic_output_sample: Optional[list[dict[str, Any]]] = None
    python_output_sample: Optional[list[dict[str, Any]]] = None
    validation_report: Optional[dict[str, Any]] = None


class ConversionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pipeline_id: uuid.UUID
    ai_model: str
    status: str
    output_file_path: Optional[str]
    conversion_time_ms: Optional[float]
    created_at: datetime


class ValidationReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pipeline_id: uuid.UUID
    status: ValidationStatus
    row_count_match: bool
    column_count_match: bool
    column_names_match: bool
    data_types_match: bool
    values_match: bool
    differences: Optional[dict]
    html_report_path: Optional[str]
    json_report_path: Optional[str]
    pdf_report_path: Optional[str]
    created_at: datetime


class DashboardResponse(BaseModel):
    total_pipelines: int
    converted_pipelines: int
    failed_pipelines: int
    running_jobs: int
    queued_jobs: int
    average_execution_time_ms: float
    success_rate: float
    failure_rate: float
    recent_activity: list[dict[str, Any]]
    pipeline_status: dict[str, int]
    daily_conversions: list[dict[str, Any]]
    monthly_conversions: list[dict[str, Any]]
    error_statistics: list[dict[str, Any]]
    top_failed_pipelines: list[dict[str, Any]]
    airflow_status: dict[str, Any]
    datadog_status: dict[str, Any]
    latest_reports: list[dict[str, Any]]
    latest_logs: list[dict[str, Any]]


class ExcelValidationError(BaseModel):
    row: Optional[int]
    column: Optional[str]
    error: str


class ExcelUploadResponse(BaseModel):
    batch_id: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    errors: list[ExcelValidationError]
    pipelines_created: int


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pipeline_id: Optional[uuid.UUID]
    job_type: str
    status: JobStatus
    progress: int
    error_message: Optional[str]
    created_at: datetime


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    message: str
    notification_type: str
    is_read: bool
    pipeline_id: Optional[uuid.UUID]
    created_at: datetime


class LogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    level: str
    module: str
    message: str
    pipeline_id: Optional[uuid.UUID]
    created_at: datetime


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str
