from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.core.database import get_db
from app.services.dashboard_service import DashboardService
from app.api.deps import viewer_or_above, analyst_or_above
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    summary="Get overall financial summary [All roles]",
)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(viewer_or_above),
):
    """
    Returns total income, total expenses, net balance,
    and a financial health indicator.
    Accessible by all authenticated roles including Viewer.
    """
    return DashboardService(db).get_summary()


@router.get(
    "/categories",
    summary="Get category-wise breakdown [All roles]",
)
def get_category_breakdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(viewer_or_above),
):
    """
    Returns income and expense totals grouped by category.
    """
    return DashboardService(db).get_category_breakdown()


@router.get(
    "/trends/monthly",
    summary="Get monthly income vs expense trends [Analyst, Admin]",
)
def get_monthly_trends(
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db),
    current_user: User = Depends(analyst_or_above),
):
    """
    Returns 12-month income/expense/net breakdown for a given year.
    Defaults to the current year if no year is provided.
    """
    return DashboardService(db).get_monthly_trends(year)


@router.get(
    "/trends/weekly",
    summary="Get weekly income vs expense trends [Analyst, Admin]",
)
def get_weekly_trends(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(analyst_or_above),
):
    """
    Returns week-by-week income/expense breakdown for a date range.
    Maximum range is 90 days.
    """
    try:
        return DashboardService(db).get_weekly_trends(date_from, date_to)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/recent",
    summary="Get recent financial activity [All roles]",
)
def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(viewer_or_above),
):
    """
    Returns the most recent financial records across all categories.
    """
    return {"recent_activity": DashboardService(db).get_recent_activity(limit)}