from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from models import (
    Billing,
    Patient,
    Doctor,
    Appointment
)


# =========================================================
# CREATE BILLING
# =========================================================

def create_billing(
    db: Session,
    billing_data,
    user_id: int
):
    # -----------------------------------------------------
    # 1. CHECK PATIENT
    # -----------------------------------------------------

    patient = db.query(Patient).filter(
        Patient.id == billing_data.patient_id
    ).first()

    if not patient:
        return None, "Patient not found"


    # -----------------------------------------------------
    # 2. CHECK DOCTOR
    # -----------------------------------------------------

    doctor = db.query(Doctor).filter(
        Doctor.id == billing_data.doctor_id
    ).first()

    if not doctor:
        return None, "Doctor not found"


    # -----------------------------------------------------
    # 3. CHECK DOCTOR ACTIVE
    # -----------------------------------------------------

    if not doctor.is_active:
        return None, "Doctor is inactive"


    # -----------------------------------------------------
    # 4. CHECK APPOINTMENT
    # -----------------------------------------------------

    appointment = None

    if billing_data.appointment_id is not None:

        appointment = db.query(Appointment).filter(
            Appointment.id == billing_data.appointment_id
        ).first()

        if not appointment:
            return None, "Appointment not found"


        # -------------------------------------------------
        # 5. CHECK APPOINTMENT BELONGS TO PATIENT
        # -------------------------------------------------

        if appointment.patient_id != billing_data.patient_id:

            return None, (
                "Appointment does not belong to this patient"
            )


        # -------------------------------------------------
        # 6. CHECK APPOINTMENT BELONGS TO DOCTOR
        # -------------------------------------------------

        if appointment.doctor_id != billing_data.doctor_id:

            return None, (
                "Appointment does not belong to this doctor"
            )


        # -------------------------------------------------
        # 7. PREVENT BILLING FOR CANCELLED APPOINTMENT
        # -------------------------------------------------

        if appointment.status == "cancelled":

            return None, (
                "Cannot create billing for cancelled appointment"
            )


        # -------------------------------------------------
        # 8. PREVENT DUPLICATE BILLING
        # -------------------------------------------------

        existing_billing = db.query(Billing).filter(
            Billing.appointment_id == billing_data.appointment_id,
            Billing.is_active == True
        ).first()

        if existing_billing:

            return None, (
                "Billing already exists for this appointment"
            )


    # -----------------------------------------------------
    # 9. CALCULATE TOTAL
    # -----------------------------------------------------

    total_amount = (
        billing_data.consultation_fee
        + billing_data.additional_charges
    )


    # -----------------------------------------------------
    # 10. CREATE BILLING OBJECT
    # -----------------------------------------------------

    billing = Billing(
        patient_id=billing_data.patient_id,
        doctor_id=billing_data.doctor_id,
        appointment_id=billing_data.appointment_id,
        consultation_fee=billing_data.consultation_fee,
        additional_charges=billing_data.additional_charges,
        total_amount=total_amount,
        payment_status=billing_data.payment_status,
        payment_mode=billing_data.payment_mode,
        is_active=True
    )


    # -----------------------------------------------------
    # 11. SAVE BILLING
    # -----------------------------------------------------

    db.add(billing)

    try:

        db.commit()

        db.refresh(billing)

    except IntegrityError:

        db.rollback()

        return None, (
            "Billing could not be created because "
            "the appointment already has a billing record"
        )


    return billing, None


# =========================================================
# GET BILLING BY ID
# =========================================================

def get_billing_by_id(
    db: Session,
    billing_id: int
):

    return db.query(Billing).filter(
        Billing.id == billing_id,
        Billing.is_active == True
    ).first()


# =========================================================
# GET ALL BILLINGS - LEVEL 28
# FILTERING + PAGINATION
# =========================================================

def get_billings(
    db: Session,
    payment_status: str = None,
    doctor_id: int = None,
    patient_id: int = None,
    from_date: datetime = None,
    to_date: datetime = None,
    page: int = 1,
    limit: int = 10
):

    query = db.query(Billing).filter(
        Billing.is_active == True
    )


    # -----------------------------------------------------
    # PAYMENT STATUS FILTER
    # -----------------------------------------------------

    if payment_status is not None:

        query = query.filter(
            Billing.payment_status == payment_status
        )


    # -----------------------------------------------------
    # DOCTOR FILTER
    # -----------------------------------------------------

    if doctor_id is not None:

        query = query.filter(
            Billing.doctor_id == doctor_id
        )


    # -----------------------------------------------------
    # PATIENT FILTER
    # -----------------------------------------------------

    if patient_id is not None:

        query = query.filter(
            Billing.patient_id == patient_id
        )


    # -----------------------------------------------------
    # FROM DATE FILTER
    # -----------------------------------------------------

    if from_date is not None:

        query = query.filter(
            Billing.created_at >= from_date
        )


    # -----------------------------------------------------
    # TO DATE FILTER
    # -----------------------------------------------------

    if to_date is not None:

        query = query.filter(
            Billing.created_at <= to_date
        )


    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    offset = (page - 1) * limit

    billings = query.offset(
        offset
    ).limit(
        limit
    ).all()


    return billings


# =========================================================
# GET PATIENT BILLINGS
# =========================================================

def get_patient_billings(
    db: Session,
    patient_id: int
):

    return db.query(Billing).filter(
        Billing.patient_id == patient_id,
        Billing.is_active == True
    ).all()


# =========================================================
# GET DOCTOR BILLINGS
# =========================================================

def get_doctor_billings(
    db: Session,
    doctor_id: int
):

    return db.query(Billing).filter(
        Billing.doctor_id == doctor_id,
        Billing.is_active == True
    ).all()


# =========================================================
# UPDATE BILLING
# =========================================================

def update_billing(
    db: Session,
    billing_id: int,
    billing_data,
    user_id: int
):

    billing = db.query(Billing).filter(
        Billing.id == billing_id,
        Billing.is_active == True
    ).first()

    if not billing:

        return None, "Billing not found"


    update_data = billing_data.model_dump(
        exclude_unset=True
    )


    # -----------------------------------------------------
    # CHECK PATIENT IF UPDATED
    # -----------------------------------------------------

    if "patient_id" in update_data:

        patient = db.query(Patient).filter(
            Patient.id == update_data["patient_id"]
        ).first()

        if not patient:

            return None, "Patient not found"


    # -----------------------------------------------------
    # CHECK DOCTOR IF UPDATED
    # -----------------------------------------------------

    if "doctor_id" in update_data:

        doctor = db.query(Doctor).filter(
            Doctor.id == update_data["doctor_id"]
        ).first()

        if not doctor:

            return None, "Doctor not found"

        if not doctor.is_active:

            return None, "Doctor is inactive"


    # -----------------------------------------------------
    # DETERMINE FINAL VALUES
    # -----------------------------------------------------

    final_patient_id = update_data.get(
        "patient_id",
        billing.patient_id
    )

    final_doctor_id = update_data.get(
        "doctor_id",
        billing.doctor_id
    )

    final_appointment_id = update_data.get(
        "appointment_id",
        billing.appointment_id
    )


    # -----------------------------------------------------
    # CHECK APPOINTMENT
    # -----------------------------------------------------

    if final_appointment_id is not None:

        appointment = db.query(Appointment).filter(
            Appointment.id == final_appointment_id
        ).first()

        if not appointment:

            return None, "Appointment not found"


        if appointment.patient_id != final_patient_id:

            return None, (
                "Appointment does not belong to this patient"
            )


        if appointment.doctor_id != final_doctor_id:

            return None, (
                "Appointment does not belong to this doctor"
            )


        if appointment.status == "cancelled":

            return None, (
                "Cannot use a cancelled appointment"
            )


        existing_billing = db.query(Billing).filter(
            Billing.appointment_id == final_appointment_id,
            Billing.id != billing_id,
            Billing.is_active == True
        ).first()

        if existing_billing:

            return None, (
                "Billing already exists for this appointment"
            )


    # -----------------------------------------------------
    # UPDATE FIELDS
    # -----------------------------------------------------

    for key, value in update_data.items():

        setattr(
            billing,
            key,
            value
        )


    # -----------------------------------------------------
    # RECALCULATE TOTAL
    # -----------------------------------------------------

    billing.total_amount = (
        billing.consultation_fee
        + billing.additional_charges
    )


    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    try:

        db.commit()

        db.refresh(billing)

    except IntegrityError:

        db.rollback()

        return None, "Billing update failed"


    return billing, None


# =========================================================
# DELETE BILLING - SOFT DELETE
# =========================================================

def delete_billing(
    db: Session,
    billing_id: int
):

    billing = db.query(Billing).filter(
        Billing.id == billing_id,
        Billing.is_active == True
    ).first()

    if not billing:

        return None


    billing.is_active = False

    db.commit()

    db.refresh(billing)

    return billing