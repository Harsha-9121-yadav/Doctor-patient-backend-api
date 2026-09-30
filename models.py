from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Float,
    UniqueConstraint
)

from sqlalchemy.orm import relationship

from datetime import datetime

from database import Base


# =========================================================
# USER
# =========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        nullable=False,
        default="doctor"
    )

    # User -> Doctor
    doctor = relationship(
        "Doctor",
        back_populates="user",
        uselist=False,
        foreign_keys="Doctor.user_id"
    )


# =========================================================
# DOCTOR
# =========================================================

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    specialization = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    is_active = Column(
        Boolean,
        default=True
    )

    # =====================================================
    # AUDIT FIELDS
    # =====================================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # =====================================================
    # USER RELATIONSHIP
    # =====================================================

    user = relationship(
        "User",
        back_populates="doctor",
        foreign_keys=[user_id]
    )

    # =====================================================
    # PATIENT ASSIGNMENTS
    # =====================================================

    patient_assignments = relationship(
        "DoctorPatient",
        back_populates="doctor",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # APPOINTMENTS
    # =====================================================

    appointments = relationship(
        "Appointment",
        back_populates="doctor",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # BILLINGS
    # =====================================================

    billings = relationship(
        "Billing",
        back_populates="doctor"
    )


# =========================================================
# PATIENT
# =========================================================

class Patient(Base):
    __tablename__ = "patients"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    age = Column(
        Integer,
        nullable=False
    )

    phone = Column(
        String(15),
        nullable=False
    )

    # =====================================================
    # AUDIT FIELDS
    # =====================================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # =====================================================
    # DOCTOR ASSIGNMENTS
    # =====================================================

    doctor_assignments = relationship(
        "DoctorPatient",
        back_populates="patient",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # APPOINTMENTS
    # =====================================================

    appointments = relationship(
        "Appointment",
        back_populates="patient",
        cascade="all, delete-orphan"
    )

    # =====================================================
    # BILLINGS
    # =====================================================

    billings = relationship(
        "Billing",
        back_populates="patient"
    )


# =========================================================
# DOCTOR-PATIENT ASSIGNMENT
# =========================================================

class DoctorPatient(Base):
    __tablename__ = "doctor_patients"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=False
    )

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False
    )

    # =====================================================
    # DOCTOR RELATIONSHIP
    # =====================================================

    doctor = relationship(
        "Doctor",
        back_populates="patient_assignments"
    )

    # =====================================================
    # PATIENT RELATIONSHIP
    # =====================================================

    patient = relationship(
        "Patient",
        back_populates="doctor_assignments"
    )


# =========================================================
# APPOINTMENT
# =========================================================

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=False,
        index=True
    )

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False,
        index=True
    )

    appointment_date = Column(
        DateTime,
        nullable=False,
        index=True
    )

    status = Column(
        String(20),
        nullable=False,
        default="scheduled"
    )

    # =====================================================
    # AUDIT FIELDS
    # =====================================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    updated_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    # =====================================================
    # DOCTOR RELATIONSHIP
    # =====================================================

    doctor = relationship(
        "Doctor",
        back_populates="appointments"
    )

    # =====================================================
    # PATIENT RELATIONSHIP
    # =====================================================

    patient = relationship(
        "Patient",
        back_populates="appointments"
    )

    # =====================================================
    # BILLING RELATIONSHIP
    # =====================================================

    billing = relationship(
        "Billing",
        back_populates="appointment",
        uselist=False
    )


# =========================================================
# BILLING
# =========================================================

class Billing(Base):
    __tablename__ = "billings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # PATIENT
    # =====================================================

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # DOCTOR
    # =====================================================

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # APPOINTMENT
    # Optional relationship
    # =====================================================

    appointment_id = Column(
        Integer,
        ForeignKey("appointments.id"),
        nullable=True,
        unique=True,
        index=True
    )

    # =====================================================
    # AMOUNTS
    # =====================================================

    consultation_fee = Column(
        Float,
        nullable=False
    )

    additional_charges = Column(
        Float,
        nullable=False,
        default=0
    )

    total_amount = Column(
        Float,
        nullable=False
    )

    # =====================================================
    # PAYMENT INFORMATION
    # =====================================================

    payment_status = Column(
        String(20),
        nullable=False,
        default="pending"
    )

    payment_mode = Column(
        String(20),
        nullable=False,
        default="cash"
    )

    # =====================================================
    # SOFT DELETE
    # =====================================================

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    patient = relationship(
        "Patient",
        back_populates="billings"
    )

    doctor = relationship(
        "Doctor",
        back_populates="billings"
    )

    appointment = relationship(
        "Appointment",
        back_populates="billing"
    )

    # =====================================================
    # DATABASE CONSTRAINT
    # =====================================================

    __table_args__ = (
        UniqueConstraint(
            "appointment_id",
            name="uq_billing_appointment"
        ),
    )