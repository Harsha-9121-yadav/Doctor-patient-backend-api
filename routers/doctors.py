from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import (
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse
)

from auth.security import get_current_user

from services.doctor_service import (
    create_doctor,
    get_doctors,
    get_doctor_by_id,
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


# =========================================================
# ADMIN AUTHORIZATION
# =========================================================

def require_admin(
    current_user: User
):

    if current_user.role != "admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


# =========================================================
# CREATE DOCTOR
# ADMIN ONLY
# =========================================================

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

    doctor, error = create_doctor(
        db,
        doctor_data,
        current_user.id
    )

    if error:

        if error == "Doctor user not found":

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error
            )

        if error == "Selected user is not a doctor":

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )

        if error == "Doctor profile already exists for this user":

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error
            )

        if error == "Doctor email already exists":

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return doctor


# =========================================================
# LIST DOCTORS
# AUTHENTICATED USERS
# =========================================================

@router.get(
    "",
    response_model=list[DoctorResponse]
)
def list_doctors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_doctors(db)


# =========================================================
# GET DOCTOR BY ID
# AUTHENTICATED USERS
# =========================================================

@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse
)
def get_doctor_api(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    doctor = get_doctor_by_id(
        db,
        doctor_id
    )

    if not doctor:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    return doctor


# =========================================================
# UPDATE DOCTOR
# ADMIN ONLY
# =========================================================

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

    doctor, error = update_doctor(
        db,
        doctor_id,
        doctor_data,
        current_user.id
    )

    if error:

        if error == "Doctor email already exists":

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    if not doctor:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

    return doctor


# =========================================================
# DELETE DOCTOR
# ADMIN ONLY
# =========================================================

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
            detail="Doctor not found or doctor cannot be deleted"
        )

    return {
        "message": "Doctor deleted successfully"
    }


# =========================================================
# ASSIGN PATIENT TO DOCTOR
# ADMIN ONLY
# =========================================================

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

    assignment, error = assign_patient(
        db,
        doctor_id,
        patient_id
    )

    if error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return {
        "message": "Patient assigned to doctor successfully",
        "doctor_id": doctor_id,
        "patient_id": patient_id
    }


# =========================================================
# GET DOCTOR'S PATIENTS
# =========================================================

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