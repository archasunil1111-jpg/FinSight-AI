"""Persistent per-user storage for FinSight-AI monthly budget limits."""

import json
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
STORE_FILE = DATA_DIR / "budget_limits.json"


def _load_all() -> Dict[str, Dict[str, float]]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STORE_FILE.exists():
        return {}

    try:
        data = json.loads(STORE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_all(data: Dict[str, Dict[str, float]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    STORE_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _user_key(user_id: Any) -> str:
    return str(user_id or "default")


def load_budget_limits(user_id: Any) -> Dict[str, float]:
    """Return saved budget limits for one user."""
    data = _load_all()
    saved = data.get(_user_key(user_id), {})
    if not isinstance(saved, dict):
        return {}

    result: Dict[str, float] = {}
    for category, value in saved.items():
        try:
            result[str(category)] = max(float(value), 0.0)
        except (TypeError, ValueError):
            continue
    return result


def save_budget_limits(user_id: Any, budget_limits: Dict[str, Any]) -> None:
    """Persist monthly budget limits for one user."""
    data = _load_all()
    cleaned: Dict[str, float] = {}

    for category, value in (budget_limits or {}).items():
        try:
            cleaned[str(category)] = max(float(value), 0.0)
        except (TypeError, ValueError):
            continue

    data[_user_key(user_id)] = cleaned
    _save_all(data)
