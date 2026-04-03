from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.record_repository import RecordRepository
from app.models.financial_record import RecordType
from app.schemas.financial_record import RecordRead


class DashboardService:

    def __init__(self, db: Session):
        self.record_repo = RecordRepository(db)

    def get_summary(self) -> dict:
        total_income = self.record_repo.get_total_by_type(RecordType.INCOME)
        total_expenses = self.record_repo.get_total_by_type(RecordType.EXPENSE)
        net_balance = total_income - total_expenses

        return {
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net_balance": round(net_balance, 2),
            "financial_health": self._health_indicator(net_balance, total_income),
        }

    def get_category_breakdown(self) -> dict:
        rows = self.record_repo.get_totals_by_category()

        income_breakdown = {}
        expense_breakdown = {}

        for row in rows:
            if row["type"] == RecordType.INCOME:
                income_breakdown[row["category"]] = round(row["total"], 2)
            else:
                expense_breakdown[row["category"]] = round(row["total"], 2)

        return {
            "income_by_category": income_breakdown,
            "expense_by_category": expense_breakdown,
        }

    def get_monthly_trends(self, year: int | None = None) -> dict:
        current_year = year or datetime.now(timezone.utc).year
        rows = self.record_repo.get_monthly_trends(current_year)

        # Build a full 12-month scaffold so missing months show as 0
        months = {i: {"income": 0.0, "expense": 0.0} for i in range(1, 13)}

        for row in rows:
            m = row["month"]
            if row["type"] == RecordType.INCOME:
                months[m]["income"] = round(row["total"], 2)
            else:
                months[m]["expense"] = round(row["total"], 2)

        return {
            "year": current_year,
            "monthly_trends": [
                {
                    "month": m,
                    "income": data["income"],
                    "expense": data["expense"],
                    "net": round(data["income"] - data["expense"], 2),
                }
                for m, data in months.items()
            ],
        }

    def get_weekly_trends(self, date_from: date, date_to: date) -> dict:
        if (date_to - date_from).days > 90:
            # Cap weekly range to 90 days to avoid heavy queries
            raise ValueError("Weekly trends range cannot exceed 90 days")

        rows = self.record_repo.get_weekly_totals(date_from, date_to)

        weekly: dict[int, dict] = {}
        for row in rows:
            w = row["week"]
            if w not in weekly:
                weekly[w] = {"week": w, "income": 0.0, "expense": 0.0}
            if row["type"] == RecordType.INCOME:
                weekly[w]["income"] = round(row["total"], 2)
            else:
                weekly[w]["expense"] = round(row["total"], 2)

        for w in weekly:
            weekly[w]["net"] = round(weekly[w]["income"] - weekly[w]["expense"], 2)

        return {
            "date_from": str(date_from),
            "date_to": str(date_to),
            "weekly_trends": list(weekly.values()),
        }

    def get_recent_activity(self, limit: int = 10) -> list[dict]:
        records = self.record_repo.get_recent(limit)
        return [RecordRead.model_validate(r).model_dump() for r in records]

    def _health_indicator(self, net_balance: float, total_income: float) -> str:
        """
        Simple financial health signal based on net balance ratio.
        Good  → net balance > 20% of income
        Fair  → net balance between 0% and 20% of income
        Poor  → net balance is negative
        """
        if total_income == 0:
            return "no_data"
        ratio = net_balance / total_income
        if ratio > 0.2:
            return "good"
        elif ratio >= 0:
            return "fair"
        else:
            return "poor"