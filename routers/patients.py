from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models import User, Doctor, Patient
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
# ADMIN CHECK
# =========================

def require_admin(current_user: User):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


# =========================
# GET LOGGED-IN DOCTOR
# =========================

def get_logged_in_doctor(
    db: Session,
    current_user: User
):

    doctor = db.query(Doctor).filter(
        Doctor.user_id == current_user.id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor profile not found"
        )

    return doctor


# =========================
# CREATE PATIENT
# ADMIN ONLY
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

    require_admin(current_user)

    return create_patient(
        db,
        patient_data,
        current_user.id
    )


# =========================
# GET PATIENTS
# ADMIN = ALL
# DOCTOR = ASSIGNED ONLY
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

    # ADMIN
    if current_user.role == "admin":

        return get_patients(
            db,
            age_gt,
            page,
            limit
        )

    # DOCTOR
    if current_user.role == "doctor":

        doctor = get_logged_in_doctor(
            db,
            current_user
        )

        patients = get_doctor_patients(
            db,
            doctor.id
        )

        if age_gt is not None:

            patients = [
                patient
                for patient in patients
                if patient.age > age_gt
            ]

        total = len(patients)

        start = (page - 1) * limit
        end = start + limit

        patients = patients[start:end]

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "data": patients
        }

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
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

    # ADMIN
    if current_user.role == "admin":
        return patient

    # DOCTOR
    if current_user.role == "doctor":

        doctor = get_logged_in_doctor(
            db,
            current_user
        )

        assigned_patient = db.query(Patient).filter(
            Patient.id == patient_id,
            Patient.doctor_assignments.any(
                Doctor.id == doctor.id
            )
        ).first()

        if not assigned_patient:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your assigned patients"
            )

        return patient

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )


# =========================
# UPDATE PATIENT
# ADMIN ONLY
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

    require_admin(current_user)

    patient = update_patient(
        db,
        patient_id,
        patient_data,
        current_user.id
    )

    if not patient:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    return patient


# =========================
# PATCH PATIENT
# ADMIN ONLY
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

    require_admin(current_user)

    patient = update_patient(
        db,
        patient_id,
        patient_data,
        current_user.id
    )

    if not patient:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    return patient


# =========================
# DELETE PATIENT
# ADMIN ONLY
# =========================

@router.delete(
    "/{patient_id}"
)
def delete_patient_api(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

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
# ADMIN ONLY
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

    require_admin(current_user)

    assignment, error = assign_patient(
        db,
        doctor_id,
        patient_id
    )

    if error:

        if error in [
            "Doctor not found",
            "Patient not found"
        ]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error
            )

        if error == "Doctor is inactive":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )

        if error == "Patient is already assigned to this doctor":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return {
        "message": "Patient assigned to doctor successfully",
        "doctor_id": doctor_id,
        "patient_id": patient_id
    }


# =========================
# GET PATIENTS OF DOCTOR
# ADMIN OR SAME DOCTOR
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

    # ADMIN
    if current_user.role == "admin":

        return get_doctor_patients(
            db,
            doctor_id
        )

    # DOCTOR
    if current_user.role == "doctor":

        doctor = get_logged_in_doctor(
            db,
            current_user
        )

        if doctor.id != doctor_id:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own patients"
            )

        return get_doctor_patients(
            db,
            doctor_id
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )