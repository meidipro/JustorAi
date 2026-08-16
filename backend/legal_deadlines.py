from __future__ import annotations

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


def calculate_deadline(event_date: date, amount: int, unit: str) -> date:
    unit = unit.lower().strip()

    if unit in {"day", "days"}:
        return event_date + timedelta(days=amount)

    if unit in {"month", "months"}:
        return event_date + relativedelta(months=amount)

    if unit in {"year", "years"}:
        return event_date + relativedelta(years=amount)

    raise ValueError(f"Unsupported unit: {unit}")


def evaluate_deadline(
    event_date: date,
    action_date: date,
    amount: int,
    unit: str,
) -> dict:
    deadline = calculate_deadline(event_date, amount, unit)
    return {
        "event_date": event_date.isoformat(),
        "deadline": deadline.isoformat(),
        "action_date": action_date.isoformat(),
        "within_period": action_date <= deadline,
        "days_remaining": max(0, (deadline - action_date).days),
        "days_after_deadline": max(0, (action_date - deadline).days),
    }
