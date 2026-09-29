from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models import Doctor, User


# =========================================================
# CREATE DOCTOR
# =========================================================

def create_doctor(
    db: Session,
    doctor_data,
    user_id: int
):
    # Find the doctor login account
    doctor_user = db.query(User).filter(
        User.username == doctor_data.username
    ).first()

    if not doctor_user:
        return None, "Doctor user not found"

    # User must have doctor role
    if doctor_user.role != "doctor":
        return None, "Selected user is not a doctor"

    # Check whether this user already has a doctor profile
    existing_doctor = db.query(Doctor).filter(
        Doctor.user_id == doctor_user.id
    ).first()

    if existing_doctor:
        return None, "Doctor profile already exists for this user"

    doctor = Doctor(
        user_id=doctor_user.id,
        name=doctor_data.name,
        specialization=doctor_data.specialization,
        email=doctor_data.email,
        is_active=True,
        created_by=user_id,
        updated_by=user_id
    )

    db.add(doctor)

    try:
        db.commit()
        db.refresh(doctor)

    except IntegrityError:
        db.rollback()

        return None, "Doctor email already exists"

    return doctor, None


# =========================================================
# GET ALL DOCTORS
# =========================================================

def get_doctors(
    db: Session
):
    return db.query(Doctor).all()


# =========================================================
# GET DOCTOR BY ID
# =========================================================

def get_doctor_by_id(
    db: Session,
    doctor_id: int
):
    return db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()


# =========================================================
# UPDATE DOCTOR
# =========================================================

def update_doctor(
    db: Session,
    doctor_id: int,
    doctor_data,
    user_id: int
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        return None, None

    update_data = doctor_data.model_dump(
        exclude_unset=True
    )

    # Do not allow username to be updated
    # because username is used to link the doctor login
    update_data.pop("username", None)

    for key, value in update_data.items():
        setattr(
            doctor,
            key,
            value
        )

    # Track who updated the doctor
    doctor.updated_by = user_id

    try:
        db.commit()
        db.refresh(doctor)

    except IntegrityError:
        db.rollback()

        return None, "Doctor email already exists"

    return doctor, None


# =========================================================
# DELETE DOCTOR
# =========================================================

def delete_doctor(
    db: Session,
    doctor_id: int
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        return None

    try:
        db.delete(doctor)
        db.commit()

    except IntegrityError:
        db.rollback()

        return None

    return doctor