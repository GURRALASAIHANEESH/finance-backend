from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.record_repository import RecordRepository
from app.schemas.financial_record import (
    RecordCreate, RecordUpdate, RecordRead,
    RecordFilter, RecordListResponse,
)
from app.models.user import User, UserRole


class RecordService:

    def __init__(self, db: Session):
        self.record_repo = RecordRepository(db)

    def create_record(self, payload: RecordCreate, requesting_user: User) -> RecordRead:
        record = self.record_repo.create(payload, created_by=requesting_user.id)
        return RecordRead.model_validate(record)

    def get_record(self, record_id: str) -> RecordRead:
        record = self.record_repo.get_by_id(record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Financial record with id '{record_id}' not found",
            )
        return RecordRead.model_validate(record)

    def list_records(self, filters: RecordFilter) -> RecordListResponse:
        records, total = self.record_repo.get_all_filtered(filters)
        return RecordListResponse(
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            results=[RecordRead.model_validate(r) for r in records],
        )

    def update_record(self, record_id: str, payload: RecordUpdate, requesting_user: User) -> RecordRead:
        record = self.record_repo.get_by_id(record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Financial record with id '{record_id}' not found",
            )

        # Analysts can read but only Admins can mutate records
        if requesting_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can update financial records",
            )

        updated = self.record_repo.update(record, payload)
        return RecordRead.model_validate(updated)

    def delete_record(self, record_id: str, requesting_user: User) -> dict:
        record = self.record_repo.get_by_id(record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Financial record with id '{record_id}' not found",
            )

        if requesting_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete financial records",
            )

        self.record_repo.soft_delete(record)
        return {"message": f"Record '{record_id}' has been deleted"}