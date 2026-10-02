from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

_STORE_PATH = Path(__file__).resolve().parent.parent / "data" / "savings_plans.json"


def _ensure_store() -> None:
    _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not _STORE_PATH.exists():
        _STORE_PATH.write_text("{}", encoding="utf-8")


def _load_all() -> Dict[str, Any]:
    _ensure_store()
    try:
        return json.loads(_STORE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def load_savings_plan(user_id: Any) -> Dict[str, Any]:
    if user_id is None:
        return {}
    data = _load_all()
    value = data.get(str(user_id), {})
    return dict(value) if isinstance(value, dict) else {}


def save_savings_plan(user_id: Any, plan: Dict[str, Any]) -> None:
    if user_id is None:
        return
    data = _load_all()
    data[str(user_id)] = {
        "target_amount": float(plan.get("target_amount", 0.0) or 0.0),
        "target_months": float(plan.get("target_months", 0.0) or 0.0),
        "desired_monthly_saving": float(
            plan.get("desired_monthly_saving", 0.0) or 0.0
        ),
        "emergency_months": float(plan.get("emergency_months", 3.0) or 3.0),
    }
    _STORE_PATH.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )
