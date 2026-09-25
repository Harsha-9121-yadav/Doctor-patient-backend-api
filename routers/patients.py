from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Patient, Doctor, DoctorPatient
from schemas import PatientCreate, PatientResponse


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


# -------------------------
# Create Patient
# -------------------------

@router.post("/", response_model=PatientResponse)
def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db)
):
    new_patient = Patient(
        name=patient.name,
        age=patient.age,
        phone=patient.phone
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


# -------------------------
# Get All Patients
# -------------------------

@router.get("/", response_model=list[PatientResponse])
def get_patients(
    db: Session = Depends(get_db)
):
    return db.query(Patient).all()


# -------------------------
# Get Patient By ID
# -------------------------

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient


# -------------------------
# Assign Patient to Doctor
# -------------------------

@router.post("/{patient_id}/assign/{doctor_id}")
def assign_patient(
    patient_id: int,
    doctor_id: int,
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    existing_assignment = db.query(DoctorPatient).filter(
        DoctorPatient.patient_id == patient_id,
        DoctorPatient.doctor_id == doctor_id
    ).first()

    if existing_assignment:
        raise HTTPException(
            status_code=400,
            detail="Patient is already assigned to this doctor"
        )

    assignment = DoctorPatient(
        patient_id=patient_id,
        doctor_id=doctor_id
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {
        "message": "Patient assigned to doctor successfully",
        "doctor_id": doctor_id,
        "patient_id": patient_id
    }


# -------------------------
# Get Patients of Doctor
# -------------------------

@router.get("/doctor/{doctor_id}", response_model=list[PatientResponse])
def get_doctor_patients(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    patients = (
        db.query(Patient)
        .join(
            DoctorPatient,
            Patient.id == DoctorPatient.patient_id
        )
        .filter(
            DoctorPatient.doctor_id == doctor_id
        )
        .all()
    )

    return patients