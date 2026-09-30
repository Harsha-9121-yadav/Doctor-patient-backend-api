from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User

from schemas import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse
)

from auth.security import get_current_user

from services.appointment_service import (
    create_appointment,
    get_appointments,
    get_appointment,
    update_appointment,
    delete_appointment,
    get_doctor_appointments,
    get_patient_appointments,
)


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


# =========================================================
# ADMIN CHECK
# =========================================================

def require_admin(current_user: User):

    if current_user.role != "admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


# =========================================================
# CREATE APPOINTMENT
# ADMIN ONLY
# =========================================================

@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_appointment_api(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    appointment, error = create_appointment(
        db,
        appointment_data,
        current_user.id
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

        if error == "Doctor already has an appointment at this time":
            raise HTTPException(
                status_code=409,
                detail=error
            )

        raise HTTPException(
            status_code=400,
            detail=error
        )

    return appointment


# =========================================================
# GET ALL APPOINTMENTS
# ADMIN ONLY
# =========================================================

@router.get(
    "",
    response_model=list[AppointmentResponse]
)
def list_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    return get_appointments(db)


# =========================================================
# GET APPOINTMENT BY ID
# ADMIN ONLY
# =========================================================

@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
def get_appointment_api(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    appointment = get_appointment(
        db,
        appointment_id
    )

    if not appointment:

        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return appointment


# =========================================================
# UPDATE APPOINTMENT - PUT
# ADMIN ONLY
# =========================================================

@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
def update_appointment_api(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    appointment, error = update_appointment(
        db,
        appointment_id,
        appointment_data,
        current_user.id
    )

    if error:

        if error == "Appointment not found":
            raise HTTPException(
                status_code=404,
                detail=error
            )

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

        if error == "Doctor already has an appointment at this time":
            raise HTTPException(
                status_code=409,
                detail=error
            )

        raise HTTPException(
            status_code=400,
            detail=error
        )

    return appointment


# =========================================================
# UPDATE APPOINTMENT - PATCH
# ADMIN ONLY
# =========================================================

@router.patch(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
def patch_appointment_api(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    appointment, error = update_appointment(
        db,
        appointment_id,
        appointment_data,
        current_user.id
    )

    if error:

        if error == "Appointment not found":
            raise HTTPException(
                status_code=404,
                detail=error
            )

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

        if error == "Doctor already has an appointment at this time":
            raise HTTPException(
                status_code=409,
                detail=error
            )

        raise HTTPException(
            status_code=400,
            detail=error
        )

    return appointment


# =========================================================
# DELETE APPOINTMENT
# ADMIN ONLY
# =========================================================

@router.delete(
    "/{appointment_id}"
)
def delete_appointment_api(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    appointment = delete_appointment(
        db,
        appointment_id
    )

    if not appointment:

        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return {
        "message": "Appointment deleted successfully"
    }


# =========================================================
# GET DOCTOR APPOINTMENTS
# =========================================================

@router.get(
    "/doctors/{doctor_id}",
    response_model=list[AppointmentResponse]
)
def doctor_appointments(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Admin can see any doctor's appointments
    if current_user.role == "admin":

        return get_doctor_appointments(
            db,
            doctor_id
        )

    # Doctor can see only their own appointments
    if current_user.role == "doctor":

        from models import Doctor

        doctor = db.query(Doctor).filter(
            Doctor.user_id == current_user.id
        ).first()

        if not doctor:

            raise HTTPException(
                status_code=404,
                detail="Doctor profile not found"
            )

        if doctor.id != doctor_id:

            raise HTTPException(
                status_code=403,
                detail="You can only view your own appointments"
            )

        return get_doctor_appointments(
            db,
            doctor_id
        )

    raise HTTPException(
        status_code=403,
        detail="Access denied"
    )


# =========================================================
# GET PATIENT APPOINTMENTS
# =========================================================

@router.get(
    "/patients/{patient_id}",
    response_model=list[AppointmentResponse]
)
def patient_appointments(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Admin can see any patient's appointments
    if current_user.role == "admin":

        return get_patient_appointments(
            db,
            patient_id
        )

    # Doctor can see appointments for assigned patients
    if current_user.role == "doctor":

        from services.patient_service import (
            is_patient_assigned_to_doctor
        )

        assigned = is_patient_assigned_to_doctor(
            db,
            current_user.id,
            patient_id
        )

        if not assigned:

            raise HTTPException(
                status_code=403,
                detail="You can only view appointments of your assigned patients"
            )

        return get_patient_appointments(
            db,
            patient_id
        )

    raise HTTPException(
        status_code=403,
        detail="Access denied"
    )