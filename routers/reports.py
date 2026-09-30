from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import User, Billing
from auth.security import get_current_user


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
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
# REVENUE REPORT
# =========================================================

@router.get("/revenue")
def revenue_report(
    doctor_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    query = db.query(
        func.coalesce(
            func.sum(Billing.total_amount),
            0
        ).label("total_revenue")
    ).filter(
        Billing.is_active == True
    )

    # -----------------------------------------------------
    # DOCTOR FILTER
    # -----------------------------------------------------

    if doctor_id is not None:

        query = query.filter(
            Billing.doctor_id == doctor_id
        )

    # -----------------------------------------------------
    # FROM DATE
    # -----------------------------------------------------

    if from_date is not None:

        query = query.filter(
            Billing.created_at >= from_date
        )

    # -----------------------------------------------------
    # TO DATE
    # -----------------------------------------------------

    if to_date is not None:

        query = query.filter(
            Billing.created_at <= to_date
        )

    result = query.first()

    total_revenue = result.total_revenue if result else 0

    return {
        "total_revenue": total_revenue,
        "doctor_id": doctor_id,
        "from_date": from_date,
        "to_date": to_date
    }


# =========================================================
# REVENUE BY DOCTOR
# =========================================================

@router.get("/revenue/by-doctor")
def revenue_by_doctor(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    query = db.query(
        Billing.doctor_id,
        func.coalesce(
            func.sum(Billing.total_amount),
            0
        ).label("total_revenue")
    ).filter(
        Billing.is_active == True
    )

    if from_date is not None:

        query = query.filter(
            Billing.created_at >= from_date
        )

    if to_date is not None:

        query = query.filter(
            Billing.created_at <= to_date
        )

    results = query.group_by(
        Billing.doctor_id
    ).all()

    return [
        {
            "doctor_id": row.doctor_id,
            "total_revenue": row.total_revenue
        }
        for row in results
    ]


# =========================================================
# REVENUE BY DAY
# =========================================================

@router.get("/revenue/by-day")
def revenue_by_day(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    require_admin(current_user)

    query = db.query(
        func.date(Billing.created_at).label("date"),
        func.coalesce(
            func.sum(Billing.total_amount),
            0
        ).label("total_revenue")
    ).filter(
        Billing.is_active == True
    )

    if from_date is not None:

        query = query.filter(
            Billing.created_at >= from_date
        )

    if to_date is not None:

        query = query.filter(
            Billing.created_at <= to_date
        )

    results = query.group_by(
        func.date(Billing.created_at)
    ).order_by(
        func.date(Billing.created_at)
    ).all()

    return [
        {
            "date": str(row.date),
            "total_revenue": row.total_revenue
        }
        for row in results
    ]