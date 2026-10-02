# ============================================================
# FinSight-AI
# Financial AI Agent
# backend/financial_agent.py
# ============================================================

import json
import re
from typing import Any, Dict, Optional

import requests


DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "qwen3:4b"


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, bool):
            return float(value)
        return float(value)
    except (TypeError, ValueError):
        return default


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _money(value: Any) -> str:
    return f"₹{_safe_float(value):,.2f}"


def _percentage(value: Any) -> str:
    return f"{_safe_float(value):.1f}%"


def tool_get_financial_snapshot(
    monthly_income: float = 0.0,
    current_savings: float = 0.0,
    family_support: float = 0.0,
    total_expenses: float = 0.0,
    highest_category: str = "None",
    highest_category_amount: float = 0.0,
    budget_limits: Optional[Dict[str, float]] = None,
    category_spending: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:

    monthly_income = _safe_float(monthly_income)
    current_savings = _safe_float(current_savings)
    family_support = _safe_float(family_support)
    total_expenses = _safe_float(total_expenses)
    highest_category_amount = _safe_float(highest_category_amount)

    adjusted_income = max(monthly_income - family_support, 0.0)
    monthly_cash_flow = adjusted_income - total_expenses
    savings_capacity = max(monthly_cash_flow, 0.0)

    savings_capacity_rate = (
        savings_capacity / monthly_income * 100.0
        if monthly_income > 0
        else 0.0
    )

    return {
        "monthly_income": monthly_income,
        "current_savings": current_savings,
        "family_support": family_support,
        "adjusted_income": adjusted_income,
        "total_expenses": total_expenses,
        "monthly_cash_flow": monthly_cash_flow,
        "savings_capacity": savings_capacity,
        "savings_capacity_rate": savings_capacity_rate,
        "highest_category": highest_category,
        "highest_category_amount": highest_category_amount,
        "budget_limits": budget_limits or {},
        "category_spending": category_spending or {},
    }


def tool_get_emergency_fund(
    current_savings: float = 0.0,
    monthly_expenses: float = 0.0,
    target_months: float = 3.0,
) -> Dict[str, Any]:

    current_savings = _safe_float(current_savings)
    monthly_expenses = _safe_float(monthly_expenses)
    target_months = _safe_float(target_months, 3.0)

    if target_months <= 0:
        target_months = 3.0

    emergency_target = monthly_expenses * target_months
    emergency_gap = max(emergency_target - current_savings, 0.0)

    coverage_months = (
        current_savings / monthly_expenses
        if monthly_expenses > 0
        else 0.0
    )

    progress = (
        current_savings / emergency_target * 100.0
        if emergency_target > 0
        else 0.0
    )

    progress = max(0.0, min(progress, 100.0))

    return {
        "current_savings": current_savings,
        "monthly_expenses": monthly_expenses,
        "target_months": target_months,
        "emergency_target": emergency_target,
        "emergency_gap": emergency_gap,
        "coverage_months": coverage_months,
        "progress_percent": progress,
        "ready": emergency_gap <= 0,
    }


def tool_get_category_spending(
    category_spending: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:

    category_spending = category_spending or {}
    clean_categories = {}

    for category, amount in category_spending.items():
        label = _clean_text(category) or "Other"
        numeric_amount = max(_safe_float(amount), 0.0)
        clean_categories[label] = numeric_amount

    total = sum(clean_categories.values())

    ranked = sorted(
        clean_categories.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    top_category = ranked[0][0] if ranked else "None"
    top_amount = ranked[0][1] if ranked else 0.0

    top_share = top_amount / total * 100.0 if total > 0 else 0.0
    top_three_amount = sum(amount for _, amount in ranked[:3])
    top_three_share = (
        top_three_amount / total * 100.0
        if total > 0
        else 0.0
    )

    return {
        "categories": clean_categories,
        "total_spending": total,
        "ranked_categories": ranked,
        "top_category": top_category,
        "top_category_amount": top_amount,
        "top_category_share": top_share,
        "top_three_share": top_three_share,
    }


def tool_get_budget_status(
    budget_limits: Optional[Dict[str, float]] = None,
    category_spending: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:

    budget_limits = budget_limits or {}
    category_spending = category_spending or {}

    clean_limits = {}
    clean_spending = {}

    for category, limit in budget_limits.items():
        label = _clean_text(category) or "Other"
        clean_limits[label] = max(_safe_float(limit), 0.0)

    for category, amount in category_spending.items():
        label = _clean_text(category) or "Other"
        clean_spending[label] = max(_safe_float(amount), 0.0)

    total_budget = sum(clean_limits.values())
    total_spending = sum(clean_spending.values())
    remaining = total_budget - total_spending

    usage_percent = (
        total_spending / total_budget * 100.0
        if total_budget > 0
        else 0.0
    )

    over_budget = []
    within_budget = []
    unused = []

    for category, limit in clean_limits.items():
        actual = clean_spending.get(category, 0.0)
        difference = limit - actual

        item = {
            "category": category,
            "budget": limit,
            "spent": actual,
            "remaining": max(difference, 0.0),
            "overspent": max(-difference, 0.0),
        }

        if actual > limit:
            over_budget.append(item)
        else:
            within_budget.append(item)
            if limit > 0 and actual == 0:
                unused.append(category)

    over_budget.sort(
        key=lambda item: item["overspent"],
        reverse=True,
    )

    biggest = over_budget[0] if over_budget else None

    return {
        "has_budget": bool(clean_limits),
        "budget_limits": clean_limits,
        "category_spending": clean_spending,
        "total_budget": total_budget,
        "total_spending": total_spending,
        "remaining_budget": remaining,
        "usage_percent": usage_percent,
        "number_over_budget": len(over_budget),
        "over_budget_categories": over_budget,
        "within_budget_categories": within_budget,
        "unused_budget_categories": unused,
        "biggest_overspending": biggest,
        "status": (
            "No budget configured"
            if not clean_limits
            else "Over budget"
            if remaining < 0
            else "Within budget"
        ),
    }


def tool_get_savings_goal_status(
    savings_plan: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    savings_plan = dict(savings_plan or {})

    target_amount = _safe_float(savings_plan.get("target_amount"))
    target_months = _safe_float(savings_plan.get("target_months"))
    current_savings = _safe_float(savings_plan.get("current_savings"))

    desired_monthly = _safe_float(
        savings_plan.get("desired_monthly_saving")
    )

    feasible_monthly = _safe_float(
        savings_plan.get(
            "feasible_monthly_saving",
            savings_plan.get("potential_monthly_savings", 0.0),
        )
    )

    potential_monthly = _safe_float(
        savings_plan.get(
            "potential_monthly_savings",
            feasible_monthly,
        )
    )

    target_gap = max(target_amount - current_savings, 0.0)

    calculated_required = (
        target_gap / target_months
        if target_months > 0
        else 0.0
    )

    required_monthly = _safe_float(
        savings_plan.get(
            "required_monthly_saving",
            calculated_required,
        )
    )

    emergency_target = _safe_float(
        savings_plan.get("emergency_target")
    )

    emergency_gap = _safe_float(
        savings_plan.get(
            "emergency_gap",
            max(emergency_target - current_savings, 0.0),
        )
    )

    if target_amount <= 0:
        return {
            "configured": False,
            "status": "No savings target configured",
            "target_amount": 0.0,
            "target_months": target_months,
            "current_savings": current_savings,
            "target_gap": 0.0,
            "required_monthly_saving": 0.0,
            "desired_monthly_saving": desired_monthly,
            "feasible_monthly_saving": feasible_monthly,
            "potential_monthly_savings": potential_monthly,
            "goal_progress_percent": 0.0,
            "goal_feasible": False,
            "emergency_target": emergency_target,
            "emergency_gap": emergency_gap,
        }

    progress = (
        current_savings / target_amount * 100.0
        if target_amount > 0
        else 0.0
    )
    progress = max(0.0, min(progress, 100.0))

    if target_gap <= 0:
        status = "Goal achieved"
        feasible = True
    elif feasible_monthly >= required_monthly and required_monthly > 0:
        status = "On track"
        feasible = True
    elif target_months > 0 and feasible_monthly > 0:
        status = "Needs adjustment"
        feasible = False
    else:
        status = "Not currently feasible"
        feasible = False

    estimated_feasible = (
        target_gap / feasible_monthly
        if feasible_monthly > 0 and target_gap > 0
        else 0.0
    )

    estimated_desired = (
        target_gap / desired_monthly
        if desired_monthly > 0 and target_gap > 0
        else 0.0
    )

    return {
        "configured": True,
        "status": status,
        "target_amount": target_amount,
        "target_months": target_months,
        "current_savings": current_savings,
        "target_gap": target_gap,
        "required_monthly_saving": required_monthly,
        "desired_monthly_saving": desired_monthly,
        "feasible_monthly_saving": feasible_monthly,
        "potential_monthly_savings": potential_monthly,
        "goal_progress_percent": progress,
        "goal_feasible": feasible,
        "estimated_months_at_feasible_rate": estimated_feasible,
        "estimated_months_at_desired_rate": estimated_desired,
        "emergency_target": emergency_target,
        "emergency_gap": emergency_gap,
    }


def _budget_answer(budget_status: Dict[str, Any]) -> str:
    if not budget_status.get("has_budget", False):
        return "You do not currently have a configured monthly budget."

    total_budget = _safe_float(budget_status.get("total_budget"))
    total_spending = _safe_float(budget_status.get("total_spending"))
    remaining = _safe_float(budget_status.get("remaining_budget"))
    over = budget_status.get("over_budget_categories", [])

    if remaining < 0:
        text = (
            f"You are over your total monthly budget by "
            f"{_money(abs(remaining))}. You have spent "
            f"{_money(total_spending)} against a budget of "
            f"{_money(total_budget)}."
        )
    else:
        text = (
            f"Your total spending is within your monthly budget. "
            f"You have spent {_money(total_spending)} of "
            f"{_money(total_budget)}, leaving {_money(remaining)}."
        )

    if over:
        biggest = over[0]
        text += (
            f" However, {len(over)} individual "
            f"categor{'y' if len(over) == 1 else 'ies'} "
            f"{'is' if len(over) == 1 else 'are'} over their limits. "
            f"The largest overrun is {biggest['category']} by "
            f"{_money(biggest['overspent'])}."
        )

    return text


def _savings_answer(savings_goal: Dict[str, Any]) -> str:
    if not savings_goal.get("configured", False):
        return "You do not currently have a configured savings target."

    status = _clean_text(savings_goal.get("status"))
    target = _safe_float(savings_goal.get("target_amount"))
    months = _safe_float(savings_goal.get("target_months"))
    current = _safe_float(savings_goal.get("current_savings"))
    gap = _safe_float(savings_goal.get("target_gap"))
    required = _safe_float(savings_goal.get("required_monthly_saving"))
    feasible = _safe_float(savings_goal.get("feasible_monthly_saving"))
    progress = _safe_float(savings_goal.get("goal_progress_percent"))

    if status == "Goal achieved":
        return (
            f"Your {_money(target)} savings goal has already been achieved. "
            f"Your current savings are {_money(current)}."
        )

    if status == "On track":
        return (
            f"Your {_money(target)} savings goal is currently on track "
            f"for {months:.0f} months. You have {_money(current)} saved "
            f"({progress:.1f}% of the target). You need about "
            f"{_money(required)} per month, while your estimated feasible "
            f"capacity is {_money(feasible)} per month."
        )

    if status == "Needs adjustment":
        return (
            f"Your {_money(target)} savings goal needs some adjustment. "
            f"You need about {_money(required)} per month to reach it in "
            f"{months:.0f} months, but your estimated feasible capacity "
            f"is {_money(feasible)} per month. The current gap is "
            f"{_money(gap)}."
        )

    return (
        f"Your {_money(target)} savings goal is not currently feasible "
        f"at your estimated savings capacity. You still need "
        f"{_money(gap)}, with a required monthly saving of "
        f"{_money(required)}."
    )


def tool_answer_rule_based(
    question: str,
    snapshot: Dict[str, Any],
    emergency: Dict[str, Any],
    category_spending: Dict[str, Any],
    budget_status: Optional[Dict[str, Any]] = None,
    savings_goal: Optional[Dict[str, Any]] = None,
    recurring_bills: Optional[list] = None,
    financial_goals: Optional[list] = None,
) -> Optional[str]:

    q = _clean_text(question).lower()
    budget_status = budget_status or {}
    savings_goal = savings_goal or {}
    recurring_bills = list(recurring_bills or [])
    financial_goals = list(financial_goals or [])

    budget_topic = any(
        term in q
        for term in [
            "budget",
            "over budget",
            "within budget",
            "budget limit",
            "budget limits",
        ]
    )

    savings_topic = any(
        term in q
        for term in [
            "savings goal",
            "saving goal",
            "savings target",
            "saving target",
            "on track for my savings",
            "on track with my savings",
            "save enough",
            "savings plan",
        ]
    )

    # Combined questions must return BOTH verified results.
    if budget_topic and savings_topic:
        return (
            "Budget status\n\n"
            f"{_budget_answer(budget_status)}\n\n"
            "Savings goal status\n\n"
            f"{_savings_answer(savings_goal)}"
        )

    if budget_topic:
        return _budget_answer(budget_status)

    if savings_topic:
        return _savings_answer(savings_goal)

    if any(
        term in q
        for term in [
            "recurring bill",
            "recurring bills",
            "monthly bill",
            "monthly bills",
            "subscriptions",
            "subscription",
            "netflix",
        ]
    ):
        if not recurring_bills:
            return "No saved recurring bills were found for this account."

        total = sum(
            _safe_float(item.get("amount"))
            for item in recurring_bills
        )
        lines = [
            f"You have {len(recurring_bills)} saved recurring bill(s), totaling {_money(total)} per month."
        ]
        for item in recurring_bills:
            name = _clean_text(item.get("bill_name")) or "Unnamed bill"
            amount = _safe_float(item.get("amount"))
            category = _clean_text(item.get("category")) or "Other"
            due_day = item.get("due_day")
            frequency = _clean_text(item.get("frequency")) or "monthly"
            due_text = f" due on day {due_day}" if due_day not in (None, "") else ""
            lines.append(
                f"• {name}: {_money(amount)} ({category}, {frequency}{due_text})."
            )
        return "\n".join(lines)

    if any(
        term in q
        for term in [
            "financial goal",
            "financial goals",
            "my goals",
            "my goal",
            "goal status",
            "savings goal list",
        ]
    ):
        if not financial_goals:
            return "No saved financial goals were found for this account."

        lines = [f"You have {len(financial_goals)} saved financial goal(s):"]
        for item in financial_goals:
            name = _clean_text(item.get("goal_name")) or "Unnamed goal"
            target = _safe_float(item.get("target_amount"))
            current = _safe_float(item.get("current_amount"))
            contribution = _safe_float(item.get("monthly_contribution"))
            deadline = _clean_text(item.get("deadline"))
            progress = current / target * 100.0 if target > 0 else 0.0
            remaining = max(target - current, 0.0)
            deadline_text = f", deadline {deadline}" if deadline else ""
            lines.append(
                f"• {name}: {_money(current)} / {_money(target)} ({progress:.1f}%), "
                f"{_money(contribution)} monthly contribution, {_money(remaining)} remaining{deadline_text}."
            )
        return "\n".join(lines)

    if any(
        term in q
        for term in [
            "emergency fund",
            "emergency savings",
            "safety fund",
        ]
    ):
        target = _safe_float(emergency.get("emergency_target"))
        gap = _safe_float(emergency.get("emergency_gap"))
        coverage = _safe_float(emergency.get("coverage_months"))

        if gap <= 0:
            return (
                f"Your emergency fund target is {_money(target)}, "
                f"and your current savings cover approximately "
                f"{coverage:.1f} months of expenses."
            )

        return (
            f"Your emergency fund target is {_money(target)}. "
            f"You currently have {_money(emergency.get('current_savings', 0))}, "
            f"leaving an emergency-fund gap of {_money(gap)}. "
            f"Your current savings cover approximately "
            f"{coverage:.1f} months of expenses."
        )

    if any(
        term in q
        for term in [
            "how much can i save",
            "monthly savings",
            "savings capacity",
        ]
    ):
        capacity = _safe_float(snapshot.get("savings_capacity"))
        rate = _safe_float(snapshot.get("savings_capacity_rate"))

        return (
            f"Your estimated monthly savings capacity is {_money(capacity)}, "
            f"which is about {rate:.1f}% of your monthly income."
        )

    if any(
        term in q
        for term in [
            "highest category",
            "top category",
            "largest spending",
            "spending category",
        ]
    ):
        top = _clean_text(
            category_spending.get(
                "top_category",
                snapshot.get("highest_category", "None"),
            )
        )
        amount = _safe_float(
            category_spending.get(
                "top_category_amount",
                snapshot.get("highest_category_amount", 0.0),
            )
        )
        share = _safe_float(
            category_spending.get("top_category_share", 0.0)
        )

        return (
            f"Your highest spending category is {top} at "
            f"{_money(amount)}, representing about {share:.1f}% "
            f"of analyzed spending."
        )

    if any(
        term in q
        for term in [
            "financial summary",
            "financial situation",
            "how am i doing",
            "overall finances",
        ]
    ):
        return (
            f"Your monthly income is "
            f"{_money(snapshot.get('monthly_income'))}, while analyzed "
            f"expenses are {_money(snapshot.get('total_expenses'))}. "
            f"Your estimated monthly cash flow is "
            f"{_money(snapshot.get('monthly_cash_flow'))}."
        )

    return None


def _clean_ollama_response(response: Any) -> str:
    text = _clean_text(response)
    if not text:
        return ""

    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    text = re.sub(
        r"<analysis>.*?</analysis>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    text = re.sub(
        r"^```(?:text|markdown)?",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"```$", "", text)
    return text.strip()


def _ask_ollama(
    prompt: str,
    ollama_base_url: str,
    ollama_model: str,
) -> str:

    url = ollama_base_url.rstrip("/") + "/api/generate"

    payload = {
        "model": ollama_model,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.8,
        },
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=90,
        )
        response.raise_for_status()

        data = response.json()
        return _clean_ollama_response(
            data.get("response", "")
        )

    except (
        requests.exceptions.RequestException,
        ValueError,
        TypeError,
        KeyError,
    ):
        return ""


def _build_agent_prompt(
    question: str,
    snapshot: Dict[str, Any],
    emergency: Dict[str, Any],
    category_spending: Dict[str, Any],
    budget_status: Dict[str, Any],
    savings_goal: Dict[str, Any],
    recurring_bills: Optional[list] = None,
    financial_goals: Optional[list] = None,
) -> str:

    verified_data = {
        "financial_snapshot": snapshot,
        "emergency_fund": emergency,
        "category_spending": category_spending,
        "budget_status": budget_status,
        "savings_goal": savings_goal,
        "recurring_bills": recurring_bills or [],
        "financial_goals": financial_goals or [],
    }

    json_data = json.dumps(
        verified_data,
        indent=2,
        ensure_ascii=False,
        default=str,
    )

    return f"""
You are FinSight-AI's local financial decision assistant.

USER QUESTION:
{question}

VERIFIED FINANCIAL DATA:
{json_data}

Rules:
1. Use only the verified values above.
2. Never invent financial values.
3. Never change verified calculations.
4. Do not claim bank-account access.
5. Do not claim to execute transactions.
6. If the question combines budget and savings, answer BOTH topics.
7. For budget questions, mention both total-budget status and any
   individual categories that are over their limits.
8. For savings questions, use the verified Savings Goal Status.
9. Be concise and practical.
10. Never expose hidden reasoning.
11. Treat recurring bills and financial goals above as verified saved data.
12. Do not ask the user to re-enter information that is already present in the verified data.
13. If the user asks about recurring bills, answer from the saved recurring_bills list.
14. If the user asks about financial goals, answer from the saved financial_goals list.
15. If saved data is empty, clearly say that no saved item is available instead of inventing one.
""".strip()


def run_financial_agent(
    question: str,
    snapshot: Dict[str, Any],
    emergency: Dict[str, Any],
    category_spending: Optional[Dict[str, Any]] = None,
    budget_status: Optional[Dict[str, Any]] = None,
    savings_goal: Optional[Dict[str, Any]] = None,
    recurring_bills: Optional[list] = None,
    financial_goals: Optional[list] = None,
    ollama_base_url: str = DEFAULT_OLLAMA_BASE_URL,
    ollama_model: str = DEFAULT_OLLAMA_MODEL,
) -> Dict[str, Any]:

    question = _clean_text(question)

    snapshot = dict(snapshot or {})
    emergency = dict(emergency or {})
    category_spending = dict(category_spending or {})
    budget_status = dict(budget_status or {})
    savings_goal = dict(savings_goal or {})
    recurring_bills = list(recurring_bills or [])
    financial_goals = list(financial_goals or [])

    deterministic_answer = tool_answer_rule_based(
        question=question,
        snapshot=snapshot,
        emergency=emergency,
        category_spending=category_spending,
        budget_status=budget_status,
        savings_goal=savings_goal,
        recurring_bills=recurring_bills,
        financial_goals=financial_goals,
    )

    common_context = {
        "monthly_income": _safe_float(
            snapshot.get("monthly_income")
        ),
        "total_expenses": _safe_float(
            snapshot.get("total_expenses")
        ),
        "current_savings": _safe_float(
            snapshot.get("current_savings")
        ),
        "monthly_cash_flow": _safe_float(
            snapshot.get("monthly_cash_flow")
        ),
        "budget_status": budget_status,
        "savings_goal": savings_goal,
        "recurring_bills": recurring_bills,
        "financial_goals": financial_goals,
    }

    if deterministic_answer:
        return {
            "answer": deterministic_answer,
            "source": "Financial Agent → deterministic tools",
            "tools_used": [
                "Financial Snapshot",
                "Emergency Fund Calculator",
                "Category Spending",
                "Budget Status",
                "Savings Goal Status",
            ],
            "verified_context": common_context,
        }

    prompt = _build_agent_prompt(
        question=question,
        snapshot=snapshot,
        emergency=emergency,
        category_spending=category_spending,
        budget_status=budget_status,
        savings_goal=savings_goal,
    )

    llm_answer = _ask_ollama(
        prompt=prompt,
        ollama_base_url=ollama_base_url,
        ollama_model=ollama_model,
    )

    if llm_answer:
        answer = llm_answer
        source = "Financial Agent → Qwen3:4B"
    else:
        answer = (
            f"Your verified financial snapshot shows monthly income of "
            f"{_money(snapshot.get('monthly_income'))}, analyzed expenses "
            f"of {_money(snapshot.get('total_expenses'))}, current savings "
            f"of {_money(snapshot.get('current_savings'))}, and estimated "
            f"monthly cash flow of "
            f"{_money(snapshot.get('monthly_cash_flow'))}."
        )
        source = "Financial Agent → verified fallback"

    return {
        "answer": answer,
        "source": source,
        "tools_used": [
            "Financial Snapshot",
            "Emergency Fund Calculator",
            "Category Spending",
            "Budget Status",
            "Savings Goal Status",
        ],
        "verified_context": common_context,
    }
