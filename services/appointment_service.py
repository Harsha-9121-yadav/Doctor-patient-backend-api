from sqlalchemy.orm import Session

from models import Appointment, Doctor, Patient
from schemas import AppointmentCreate, AppointmentUpdate


# =========================================================
# CHECK OVERLAPPING APPOINTMENT
# =========================================================

def check_overlap(
    db: Session,
    doctor_id: int,
    appointment_date,
    appointment_id: int = None
):
    query = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.status == "scheduled"
    )

    if appointment_id is not None:
        query = query.filter(
            Appointment.id != appointment_id
        )

    return query.first()


# =========================================================
# CREATE APPOINTMENT
# =========================================================

def create_appointment(
    db: Session,
    appointment_data: AppointmentCreate,
    user_id: int
):
    doctor = db.query(Doctor).filter(
        Doctor.id == appointment_data.doctor_id
    ).first()

    if not doctor:
        return None, "Doctor not found"

    if not doctor.is_active:
        return None, "Doctor is inactive"

    patient = db.query(Patient).filter(
        Patient.id == appointment_data.patient_id
    ).first()

    if not patient:
        return None, "Patient not found"

    overlapping = check_overlap(
        db,
        appointment_data.doctor_id,
        appointment_data.appointment_date
    )

    if overlapping:
        return None, "Doctor already has an appointment at this time"

    appointment = Appointment(
        doctor_id=appointment_data.doctor_id,
        patient_id=appointment_data.patient_id,
        appointment_date=appointment_data.appointment_date,
        status=appointment_data.status,
        created_by=user_id,
        updated_by=user_id
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment, None


# =========================================================
# GET ALL APPOINTMENTS
# =========================================================

def get_appointments(
    db: Session
):
    return db.query(Appointment).all()


# =========================================================
# GET APPOINTMENT BY ID
# =========================================================

def get_appointment(
    db: Session,
    appointment_id: int
):
    return db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()


# =========================================================
# UPDATE APPOINTMENT
# =========================================================

def update_appointment(
    db: Session,
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    user_id: int
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:
        return None, "Appointment not found"

    update_data = appointment_data.model_dump(
        exclude_unset=True
    )

    doctor_id = update_data.get(
        "doctor_id",
        appointment.doctor_id
    )

    patient_id = update_data.get(
        "patient_id",
        appointment.patient_id
    )

    appointment_date = update_data.get(
        "appointment_date",
        appointment.appointment_date
    )

    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        return None, "Doctor not found"

    if not doctor.is_active:
        return None, "Doctor is inactive"

    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:
        return None, "Patient not found"

    overlapping = check_overlap(
        db,
        doctor_id,
        appointment_date,
        appointment.id
    )

    if overlapping:
        return None, "Doctor already has an appointment at this time"

    for key, value in update_data.items():
        setattr(
            appointment,
            key,
            value
        )

    # Track user who updated the appointment
    appointment.updated_by = user_id

    db.commit()
    db.refresh(appointment)

    return appointment, None


# =========================================================
# DELETE APPOINTMENT
# =========================================================

def delete_appointment(
    db: Session,
    appointment_id: int
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:
        return None

    db.delete(appointment)
    db.commit()

    return appointment


# =========================================================
# GET DOCTOR APPOINTMENTS
# =========================================================

def get_doctor_appointments(
    db: Session,
    doctor_id: int
):
    return db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id
    ).all()


# =========================================================
# GET PATIENT APPOINTMENTS
# =========================================================

def get_patient_appointments(
    db: Session,
    patient_id: int
):
    return db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).all()