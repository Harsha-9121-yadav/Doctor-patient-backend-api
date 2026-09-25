from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import DoctorCreate, DoctorUpdate, DoctorResponse

from auth.security import get_current_user

from services.doctor_service import (
    create_doctor,
    get_doctors,
    get_doctor,
    update_doctor,
    delete_doctor,
)

from services.patient_service import (
    assign_patient,
    get_doctor_patients,
)


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


# =========================
# ADMIN AUTHORIZATION
# =========================

def require_admin(current_user: User):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


# =========================
# CREATE DOCTOR
# =========================

@router.post(
    "",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED
)
def create_doctor_api(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_admin(current_user)

    return create_doctor(
        db,
        current_user.id,
        doctor_data
    )


# =========================
# GET ALL DOCTORS
# =========================

@router.get(
    "",
    response_model=list[DoctorResponse]
)
def list_doctors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_doctors(db)


# =========================
# GET DOCTOR BY ID
# =========================

@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def get_doctor_api(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doctor = get_doctor(
        db,
        doctor_id
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    return doctor


# =========================
# UPDATE DOCTOR
# =========================

@router.put(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def update_doctor_api(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_admin(current_user)

    doctor = update_doctor(
        db,
        doctor_id,
        doctor_data
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    return doctor


# =========================
# DELETE DOCTOR
# =========================

@router.delete(
    "/{doctor_id}"
)
def delete_doctor_api(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_admin(current_user)

    doctor = delete_doctor(
        db,
        doctor_id
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    return {
        "message": "Doctor deleted successfully"
    }


# =========================
# ASSIGN PATIENT TO DOCTOR
# =========================

@router.post(
    "/{doctor_id}/patients/{patient_id}"
)
def assign_patient_to_doctor(
    doctor_id: int,
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_admin(current_user)

    return assign_patient(
        db,
        doctor_id,
        patient_id
    )


# =========================
# GET DOCTOR'S PATIENTS
# =========================

@router.get(
    "/{doctor_id}/patients"
)
def get_patients_for_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_doctor_patients(
        db,
        doctor_id
    )