from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import PatientCreate, PatientUpdate, PatientResponse

from auth.security import get_current_user

from services.patient_service import (
    create_patient,
    get_patients,
    get_patient,
    update_patient,
    delete_patient,
    assign_patient,
    get_doctor_patients,
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


# =========================
# CREATE PATIENT
# =========================

@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED
)
def create_patient_api(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_patient(
        db,
        patient_data
    )


# =========================
# GET PATIENTS
# FILTERING + PAGINATION
# =========================

@router.get("/")
def list_patients(
    age_gt: int = Query(
        default=None,
        gt=0
    ),
    page: int = Query(
        default=1,
        ge=1
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_patients(
        db,
        age_gt,
        page,
        limit
    )


# =========================
# GET PATIENT BY ID
# =========================

@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
def get_patient_api(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = get_patient(
        db,
        patient_id
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    return patient


# =========================
# PUT PATIENT
# =========================

@router.put(
    "/{patient_id}",
    response_model=PatientResponse
)
def update_patient_api(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = update_patient(
        db,
        patient_id,
        patient_data
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    return patient


# =========================
# PATCH PATIENT
# =========================

@router.patch(
    "/{patient_id}",
    response_model=PatientResponse
)
def patch_patient_api(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = update_patient(
        db,
        patient_id,
        patient_data
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    return patient


# =========================
# DELETE PATIENT
# =========================

@router.delete(
    "/{patient_id}"
)
def delete_patient_api(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = delete_patient(
        db,
        patient_id
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    return {
        "message": "Patient deleted successfully"
    }


# =========================
# ASSIGN PATIENT TO DOCTOR
# =========================

@router.post(
    "/{patient_id}/assign/{doctor_id}"
)
def assign_patient_api(
    patient_id: int,
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assignment, error = assign_patient(
        db,
        doctor_id,
        patient_id
    )

    if error:
        if error == "Doctor not found":
            raise HTTPException(
                status_code=404,
                detail=error
            )

        if error == "Patient not found":
            raise HTTPException(
                status_code=404,
                detail=error
            )

        if error == "Doctor is inactive":
            raise HTTPException(
                status_code=400,
                detail=error
            )

        if error == "Patient is already assigned to this doctor":
            raise HTTPException(
                status_code=400,
                detail=error
            )

    return {
        "message": "Patient assigned to doctor successfully",
        "doctor_id": doctor_id,
        "patient_id": patient_id
    }


# =========================
# GET PATIENTS OF DOCTOR
# =========================

@router.get(
    "/doctor/{doctor_id}",
    response_model=list[PatientResponse]
)
def get_doctor_patients_api(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_doctor_patients(
        db,
        doctor_id
    )