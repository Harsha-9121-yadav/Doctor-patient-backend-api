from sqlalchemy.orm import Session

from models import Doctor


# =========================
# CREATE DOCTOR
# =========================

def create_doctor(
    db: Session,
    user_id: int,
    doctor_data
):
    doctor = Doctor(
        user_id=user_id,
        name=doctor_data.name,
        specialization=doctor_data.specialization,
        email=doctor_data.email
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


# =========================
# GET DOCTORS
# FILTERING + PAGINATION
# =========================

def get_doctors(
    db: Session,
    specialization: str = None,
    is_active: bool = None,
    page: int = 1,
    limit: int = 10
):
    query = db.query(Doctor)

    # Filtering
    if specialization:
        query = query.filter(
            Doctor.specialization == specialization
        )

    if is_active is not None:
        query = query.filter(
            Doctor.is_active == is_active
        )

    # Total records after filtering
    total = query.count()

    # Pagination
    offset = (page - 1) * limit

    doctors = query.offset(
        offset
    ).limit(
        limit
    ).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": doctors
    }


# =========================
# GET DOCTOR BY ID
# =========================

def get_doctor(
    db: Session,
    doctor_id: int
):
    return db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()


# =========================
# UPDATE DOCTOR
# =========================

def update_doctor(
    db: Session,
    doctor_id: int,
    doctor_data
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        return None

    update_data = doctor_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(doctor, key, value)

    db.commit()
    db.refresh(doctor)

    return doctor


# =========================
# DELETE DOCTOR - SOFT DELETE
# =========================

def delete_doctor(
    db: Session,
    doctor_id: int
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        return None

    doctor.is_active = False

    db.commit()
    db.refresh(doctor)

    return doctor