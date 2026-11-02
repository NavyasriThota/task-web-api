from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    course: str
    batch: str
    address: Optional[str] = None

    @field_validator("first_name", "last_name", "course", "batch")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if value is None or not value.strip():
            raise ValueError("This field is required.")
        return value.strip()

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 7:
            raise ValueError("Phone number must contain at least 7 digits.")
        return cleaned

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    course: Optional[str] = None
    batch: Optional[str] = None
    address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("first_name", "last_name", "course", "batch")
    @classmethod
    def validate_required_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("This field is required.")
        return value.strip()

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if len(cleaned) < 7:
            raise ValueError("Phone number must contain at least 7 digits.")
        return cleaned

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        return cleaned or None


class StudentResponse(StudentBase):
    student_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentListResponse(BaseModel):
    total: int
    students: list[StudentResponse]
