from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import User

from schemas import (
    BillingCreate,
    BillingUpdate,
    BillingResponse
)

from auth.security import get_current_user

from services.billing_service import (
    create_billing,
    get_billing_by_id,
    get_billings,
    get_patient_billings,
    get_doctor_billings,
    update_billing,
    delete_billing
)


router = APIRouter(
    prefix="/billings",
    tags=["Billings"]
)


# =========================================================
# ADMIN AUTHORIZATION
# =========================================================

def require_admin(current_user: User):

    if current_user.role != "admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


# =========================================================
# CREATE BILLING
# =========================================================

@router.post(
    "",
    response_model=BillingResponse,
    status_code=status.HTTP_201_CREATED
)
def create_billing_api(
    billing_data: BillingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    billing, error = create_billing(
        db,
        billing_data,
        current_user.id
    )

    if error:

        if "already exists" in error:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error
            )

        if "not found" in error:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return billing


# =========================================================
# GET ALL BILLINGS
# LEVEL 28 - FILTERING + PAGINATION
# =========================================================

@router.get(
    "",
    response_model=list[BillingResponse]
)
def get_all_billings_api(
    payment_status: str | None = Query(
        default=None
    ),

    doctor_id: int | None = Query(
        default=None,
        gt=0
    ),

    patient_id: int | None = Query(
        default=None,
        gt=0
    ),

    from_date: datetime | None = Query(
        default=None
    ),

    to_date: datetime | None = Query(
        default=None
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

    # -----------------------------------------------------
    # ADMIN CAN VIEW ALL BILLINGS
    # -----------------------------------------------------

    if current_user.role == "admin":

        return get_billings(
            db=db,
            payment_status=payment_status,
            doctor_id=doctor_id,
            patient_id=patient_id,
            from_date=from_date,
            to_date=to_date,
            page=page,
            limit=limit
        )


    # -----------------------------------------------------
    # DOCTOR CAN VIEW ONLY THEIR OWN BILLINGS
    # -----------------------------------------------------

    if current_user.role == "doctor":

        if not current_user.doctor:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor profile not found"
            )

        # Force doctor_id to logged-in doctor's ID
        doctor_id = current_user.doctor.id

        return get_billings(
            db=db,
            payment_status=payment_status,
            doctor_id=doctor_id,
            patient_id=patient_id,
            from_date=from_date,
            to_date=to_date,
            page=page,
            limit=limit
        )


    # -----------------------------------------------------
    # OTHER ROLES
    # -----------------------------------------------------

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )


# =========================================================
# GET BILLING BY ID
# =========================================================

@router.get(
    "/{billing_id}",
    response_model=BillingResponse
)
def get_billing_api(
    billing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    billing = get_billing_by_id(
        db,
        billing_id
    )

    if not billing:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing not found"
        )


    # -----------------------------------------------------
    # ADMIN CAN VIEW
    # -----------------------------------------------------

    if current_user.role == "admin":

        return billing


    # -----------------------------------------------------
    # DOCTOR CAN VIEW THEIR BILLING
    # -----------------------------------------------------

    if current_user.role == "doctor":

        if not current_user.doctor:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor profile not found"
            )

        if billing.doctor_id != current_user.doctor.id:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view this billing"
            )

        return billing


    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )


# =========================================================
# GET PATIENT BILLINGS
# =========================================================

@router.get(
    "/patients/{patient_id}/billings",
    response_model=list[BillingResponse]
)
def get_patient_billings_api(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    billings = get_patient_billings(
        db,
        patient_id
    )

    return billings


# =========================================================
# GET DOCTOR BILLINGS
# =========================================================

@router.get(
    "/doctors/{doctor_id}/billings",
    response_model=list[BillingResponse]
)
def get_doctor_billings_api(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------------------------------
    # ADMIN CAN VIEW ANY DOCTOR BILLINGS
    # -----------------------------------------------------

    if current_user.role == "admin":

        return get_doctor_billings(
            db,
            doctor_id
        )


    # -----------------------------------------------------
    # DOCTOR CAN VIEW ONLY THEIR OWN BILLINGS
    # -----------------------------------------------------

    if current_user.role == "doctor":

        if not current_user.doctor:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctor profile not found"
            )

        if current_user.doctor.id != doctor_id:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view these billings"
            )

        return get_doctor_billings(
            db,
            doctor_id
        )


    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )


# =========================================================
# UPDATE BILLING - PUT
# =========================================================

@router.put(
    "/{billing_id}",
    response_model=BillingResponse
)
def update_billing_api(
    billing_id: int,
    billing_data: BillingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    billing, error = update_billing(
        db,
        billing_id,
        billing_data,
        current_user.id
    )

    if error:

        if "not found" in error:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error
            )

        if "already exists" in error:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return billing


# =========================================================
# UPDATE BILLING - PATCH
# =========================================================

@router.patch(
    "/{billing_id}",
    response_model=BillingResponse
)
def patch_billing_api(
    billing_id: int,
    billing_data: BillingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    billing, error = update_billing(
        db,
        billing_id,
        billing_data,
        current_user.id
    )

    if error:

        if "not found" in error:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error
            )

        if "already exists" in error:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return billing


# =========================================================
# DELETE BILLING - SOFT DELETE
# =========================================================

@router.delete(
    "/{billing_id}"
)
def delete_billing_api(
    billing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    billing = delete_billing(
        db,
        billing_id
    )

    if not billing:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing not found"
        )

    return {
        "message": "Billing deleted successfully"
    }