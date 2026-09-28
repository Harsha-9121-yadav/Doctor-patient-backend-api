from sqlalchemy.orm import Session

from models import Patient, Doctor, DoctorPatient
from schemas import PatientCreate, PatientUpdate


# =========================
# CREATE PATIENT
# =========================

def create_patient(
    db: Session,
    patient_data: PatientCreate
):
    patient = Patient(
        name=patient_data.name,
        age=patient_data.age,
        phone=patient_data.phone
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


# =========================
# GET PATIENTS
# FILTERING + PAGINATION
# =========================

def get_patients(
    db: Session,
    age_gt: int = None,
    page: int = 1,
    limit: int = 10
):
    query = db.query(Patient)

    # Age filtering
    if age_gt is not None:
        query = query.filter(
            Patient.age > age_gt
        )

    # Total records after filtering
    total = query.count()

    # Pagination
    offset = (page - 1) * limit

    patients = query.offset(
        offset
    ).limit(
        limit
    ).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": patients
    }


# =========================
# GET PATIENT BY ID
# =========================

def get_patient(
    db: Session,
    patient_id: int
):
    return db.query(Patient).filter(
        Patient.id == patient_id
    ).first()


# =========================
# UPDATE PATIENT
# =========================

def update_patient(
    db: Session,
    patient_id: int,
    patient_data: PatientUpdate
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:
        return None

    update_data = patient_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)

    return patient


# =========================
# DELETE PATIENT
# =========================

def delete_patient(
    db: Session,
    patient_id: int
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:
        return None

    db.delete(patient)
    db.commit()

    return patient


# =========================
# ASSIGN PATIENT TO DOCTOR
# =========================

def assign_patient(
    db: Session,
    doctor_id: int,
    patient_id: int
):
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

    existing_assignment = db.query(DoctorPatient).filter(
        DoctorPatient.doctor_id == doctor_id,
        DoctorPatient.patient_id == patient_id
    ).first()

    if existing_assignment:
        return None, "Patient is already assigned to this doctor"

    assignment = DoctorPatient(
        doctor_id=doctor_id,
        patient_id=patient_id
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment, None


# =========================
# GET DOCTOR'S PATIENTS
# =========================

def get_doctor_patients(
    db: Session,
    doctor_id: int
):
    assignments = db.query(DoctorPatient).filter(
        DoctorPatient.doctor_id == doctor_id
    ).all()

    return [
        assignment.patient
        for assignment in assignments
    ]