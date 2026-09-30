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


# =========================================================
# BILLING SCHEMAS
# =========================================================

class BillingCreate(BaseModel):

    patient_id: int = Field(
        gt=0
    )

    doctor_id: int = Field(
        gt=0
    )

    appointment_id: Optional[int] = Field(
        default=None,
        gt=0
    )

    consultation_fee: float = Field(
        gt=0
    )

    additional_charges: float = Field(
        default=0,
        ge=0
    )

    payment_status: str = "pending"

    payment_mode: str = "cash"

    # -----------------------------------------------------
    # PAYMENT STATUS VALIDATION
    # -----------------------------------------------------

    @field_validator("payment_status")
    @classmethod
    def validate_payment_status(cls, value):

        allowed_statuses = [
            "pending",
            "paid",
            "cancelled"
        ]

        if value not in allowed_statuses:
            raise ValueError(
                "Payment status must be pending, paid, or cancelled"
            )

        return value

    # -----------------------------------------------------
    # PAYMENT MODE VALIDATION
    # -----------------------------------------------------

    @field_validator("payment_mode")
    @classmethod
    def validate_payment_mode(cls, value):

        allowed_modes = [
            "cash",
            "card",
            "upi"
        ]

        if value not in allowed_modes:
            raise ValueError(
                "Payment mode must be cash, card, or upi"
            )

        return value


# =========================================================
# BILLING UPDATE SCHEMA
# =========================================================

class BillingUpdate(BaseModel):

    patient_id: Optional[int] = Field(
        default=None,
        gt=0
    )

    doctor_id: Optional[int] = Field(
        default=None,
        gt=0
    )

    appointment_id: Optional[int] = Field(
        default=None,
        gt=0
    )

    consultation_fee: Optional[float] = Field(
        default=None,
        gt=0
    )

    additional_charges: Optional[float] = Field(
        default=None,
        ge=0
    )

    payment_status: Optional[str] = None

    payment_mode: Optional[str] = None

    # -----------------------------------------------------
    # PAYMENT STATUS VALIDATION
    # -----------------------------------------------------

    @field_validator("payment_status")
    @classmethod
    def validate_payment_status(cls, value):

        if value is not None:

            allowed_statuses = [
                "pending",
                "paid",
                "cancelled"
            ]

            if value not in allowed_statuses:
                raise ValueError(
                    "Payment status must be pending, paid, or cancelled"
                )

        return value

    # -----------------------------------------------------
    # PAYMENT MODE VALIDATION
    # -----------------------------------------------------

    @field_validator("payment_mode")
    @classmethod
    def validate_payment_mode(cls, value):

        if value is not None:

            allowed_modes = [
                "cash",
                "card",
                "upi"
            ]

            if value not in allowed_modes:
                raise ValueError(
                    "Payment mode must be cash, card, or upi"
                )

        return value


# =========================================================
# BILLING RESPONSE
# =========================================================

class BillingResponse(BaseModel):

    id: int

    patient_id: int

    doctor_id: int

    appointment_id: Optional[int]

    consultation_fee: float

    additional_charges: float

    total_amount: float

    payment_status: str

    payment_mode: str

    is_active: bool

    created_at: datetime

    updated_at: datetime

    class Config:
        from_attributes = True