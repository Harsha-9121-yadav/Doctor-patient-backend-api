from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


# =========================================================
# AUTHENTICATION SCHEMAS
# =========================================================

class UserRegister(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50
    )

    email: EmailStr

    password: str = Field(
        min_length=6
    )

    role: str = "doctor"

    @field_validator("role")
    @classmethod
    def validate_role(cls, value):

        if value not in ["admin", "doctor"]:
            raise ValueError(
                "Role must be admin or doctor"
            )

        return value


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# =========================================================
# DOCTOR SCHEMAS
# =========================================================

class DoctorCreate(BaseModel):

    # Username of the doctor login account
    username: str = Field(
        min_length=3,
        max_length=50
    )

    name: str = Field(
        min_length=2,
        max_length=100
    )

    specialization: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr


class DoctorUpdate(BaseModel):

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    specialization: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    email: Optional[EmailStr] = None


class DoctorResponse(BaseModel):

    id: int

    user_id: Optional[int]

    name: str

    specialization: str

    email: EmailStr

    is_active: bool

    class Config:
        from_attributes = True


# =========================================================
# PATIENT SCHEMAS
# =========================================================

class PatientCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    age: int = Field(
        gt=0
    )

    phone: str = Field(
        min_length=10,
        max_length=10
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):

        if not value.isdigit():
            raise ValueError(
                "Phone number must contain only digits"
            )

        if len(value) != 10:
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )

        return value


class PatientUpdate(BaseModel):

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    age: Optional[int] = Field(
        default=None,
        gt=0
    )

    phone: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=10
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):

        if value is not None:

            if not value.isdigit():
                raise ValueError(
                    "Phone number must contain only digits"
                )

            if len(value) != 10:
                raise ValueError(
                    "Phone number must contain exactly 10 digits"
                )

        return value


class PatientResponse(BaseModel):

    id: int

    name: str

    age: int

    phone: str

    class Config:
        from_attributes = True


# =========================================================
# APPOINTMENT SCHEMAS
# =========================================================

class AppointmentCreate(BaseModel):

    doctor_id: int = Field(
        gt=0
    )

    patient_id: int = Field(
        gt=0
    )

    appointment_date: datetime

    status: str = "scheduled"

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):

        allowed_statuses = [
            "scheduled",
            "completed",
            "cancelled"
        ]

        if value not in allowed_statuses:
            raise ValueError(
                "Status must be scheduled, completed, or cancelled"
            )

        return value


class AppointmentUpdate(BaseModel):

    doctor_id: Optional[int] = Field(
        default=None,
        gt=0
    )

    patient_id: Optional[int] = Field(
        default=None,
        gt=0
    )

    appointment_date: Optional[datetime] = None

    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):

        if value is not None:

            allowed_statuses = [
                "scheduled",
                "completed",
                "cancelled"
            ]

            if value not in allowed_statuses:
                raise ValueError(
                    "Status must be scheduled, completed, or cancelled"
                )

        return value


class AppointmentResponse(BaseModel):

    id: int

    doctor_id: int

    patient_id: int

    appointment_date: datetime

    status: str

    class Config:
        from_attributes = True