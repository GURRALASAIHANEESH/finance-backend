from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import ValidationError
from typing import Optional
from datetime import date
from app.core.database import get_db
from app.services.record_service import RecordService
from app.schemas.financial_record import (
    RecordCreate, RecordUpdate, RecordRead,
    RecordFilter, RecordListResponse,
)
from app.api.deps import viewer_or_above, analyst_or_above, admin_only
from app.models.user import User
from app.models.financial_record import RecordType, RecordCategory

router = APIRouter(prefix="/records", tags=["Financial Records"])


@router.get(
    "/",
    response_model=RecordListResponse,
    summary="List financial records with filters [Analyst, Admin]",
)
def list_records(
    type: Optional[RecordType] = Query(None),
    category: Optional[RecordCategory] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(analyst_or_above),
):
    """
    Fetch financial records with optional filters.
    Viewers cannot access raw records — use /dashboard/summary instead.
    """
    try:
        filters = RecordFilter(
            type=type,
            category=category,
            date_from=date_from,
            date_to=date_to,
            page=page,
            page_size=page_size,
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.errors()[0]["msg"],
        )
    return RecordService(db).list_records(filters)


@router.get(
    "/{record_id}",
    response_model=RecordRead,
    summary="Get a single record by ID [Analyst, Admin]",
)
def get_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(analyst_or_above),
):
    return RecordService(db).get_record(record_id)


@router.post(
    "/",
    response_model=RecordRead,
    status_code=201,
    summary="Create a financial record [Admin only]",
)
def create_record(
    payload: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Create a new financial record.
    Category must match the record type (income vs expense).
    """
    return RecordService(db).create_record(payload, requesting_user=current_user)


@router.patch(
    "/{record_id}",
    response_model=RecordRead,
    summary="Update a financial record [Admin only]",
)
def update_record(
    record_id: str,
    payload: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Partial update of a financial record.
    Record type is intentionally locked after creation.
    """
    return RecordService(db).update_record(record_id, payload, requesting_user=current_user)


@router.delete(
    "/{record_id}",
    summary="Soft delete a financial record [Admin only]",
)
def delete_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    return RecordService(db).delete_record(record_id, requesting_user=current_user)