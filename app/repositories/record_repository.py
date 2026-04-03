from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from app.models.financial_record import FinancialRecord, RecordType, RecordCategory
from app.schemas.financial_record import RecordCreate, RecordUpdate, RecordFilter
from typing import Optional
from datetime import date


class RecordRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, record_id: str) -> Optional[FinancialRecord]:
        return self.db.scalar(
            select(FinancialRecord).where(
                FinancialRecord.id == record_id,
                FinancialRecord.is_deleted == False,
            )
        )

    def get_all_filtered(
        self, filters: RecordFilter
    ) -> tuple[list[FinancialRecord], int]:

        conditions = [FinancialRecord.is_deleted == False]

        if filters.type:
            conditions.append(FinancialRecord.type == filters.type)
        if filters.category:
            conditions.append(FinancialRecord.category == filters.category)
        if filters.date_from:
            conditions.append(FinancialRecord.record_date >= filters.date_from)
        if filters.date_to:
            conditions.append(FinancialRecord.record_date <= filters.date_to)

        base_query = select(FinancialRecord).where(and_(*conditions))

        total = self.db.scalar(
            select(func.count()).select_from(base_query.subquery())
        )

        records = self.db.scalars(
            base_query.order_by(FinancialRecord.record_date.desc())
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        ).all()

        return list(records), total

    def create(self, payload: RecordCreate, created_by: str) -> FinancialRecord:
        record = FinancialRecord(
            amount=payload.amount,
            type=payload.type,
            category=payload.category,
            record_date=payload.record_date,
            notes=payload.notes,
            created_by=created_by,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record: FinancialRecord, payload: RecordUpdate) -> FinancialRecord:
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)
        self.db.commit()
        self.db.refresh(record)
        return record

    def soft_delete(self, record: FinancialRecord) -> None:
        record.is_deleted = True
        self.db.commit()

    def get_total_by_type(self, type: RecordType) -> float:
        result = self.db.scalar(
            select(func.coalesce(func.sum(FinancialRecord.amount), 0)).where(
                FinancialRecord.type == type,
                FinancialRecord.is_deleted == False,
            )
        )
        return float(result)

    def get_totals_by_category(self) -> list[dict]:
        rows = self.db.execute(
            select(
                FinancialRecord.category,
                FinancialRecord.type,
                func.sum(FinancialRecord.amount).label("total"),
            )
            .where(FinancialRecord.is_deleted == False)
            .group_by(FinancialRecord.category, FinancialRecord.type)
            .order_by(func.sum(FinancialRecord.amount).desc())
        ).all()

        return [
            {"category": row.category, "type": row.type, "total": float(row.total)}
            for row in rows
        ]

    def get_monthly_trends(self, year: int) -> list[dict]:
        rows = self.db.execute(
            select(
                func.extract("month", FinancialRecord.record_date).label("month"),
                FinancialRecord.type,
                func.sum(FinancialRecord.amount).label("total"),
            )
            .where(
                func.extract("year", FinancialRecord.record_date) == year,
                FinancialRecord.is_deleted == False,
            )
            .group_by("month", FinancialRecord.type)
            .order_by("month")
        ).all()

        return [
            {"month": int(row.month), "type": row.type, "total": float(row.total)}
            for row in rows
        ]

    def get_recent(self, limit: int = 10) -> list[FinancialRecord]:
        return list(
            self.db.scalars(
                select(FinancialRecord)
                .where(FinancialRecord.is_deleted == False)
                .order_by(FinancialRecord.created_at.desc())
                .limit(limit)
            ).all()
        )

    def get_weekly_totals(
        self, date_from: date, date_to: date
    ) -> list[dict]:
        rows = self.db.execute(
            select(
                func.extract("week", FinancialRecord.record_date).label("week"),
                FinancialRecord.type,
                func.sum(FinancialRecord.amount).label("total"),
            )
            .where(
                FinancialRecord.record_date >= date_from,
                FinancialRecord.record_date <= date_to,
                FinancialRecord.is_deleted == False,
            )
            .group_by("week", FinancialRecord.type)
            .order_by("week")
        ).all()

        return [
            {"week": int(row.week), "type": row.type, "total": float(row.total)}
            for row in rows
        ]