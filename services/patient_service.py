from sqlalchemy.orm import Session

from models import Patient, DoctorPatient
from schemas import PatientCreate


def create_patient(db: Session, patient_data: PatientCreate):
    patient = Patient(
        name=patient_data.name,
        age=patient_data.age,
        phone=patient_data.phone,
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


def get_patients(db: Session):
    return db.query(Patient).all()


def get_patient(db: Session, patient_id: int):
    return db.query(Patient).filter(
        Patient.id == patient_id
    ).first()


def assign_patient(
    db: Session,
    doctor_id: int,
    patient_id: int
):
    assignment = DoctorPatient(
        doctor_id=doctor_id,
        patient_id=patient_id
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment


def get_doctor_patients(
    db: Session,
    doctor_id: int
):
    assignments = db.query(DoctorPatient).filter(
        DoctorPatient.doctor_id == doctor_id
    ).all()

    return [assignment.patient for assignment in assignments]