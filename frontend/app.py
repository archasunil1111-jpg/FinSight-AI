# ============================================================
#  FinSight-AI
# Personal Financial Analysis Assistant
# frontend/app.py
# ============================================================

import os
import sys
import re
from datetime import date
import textwrap
from html import escape

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="FinSight-AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PROJECT PATH
# ============================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_ROOT = os.path.dirname(
    CURRENT_DIR
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# BACKEND IMPORTS
# ============================================================

BACKEND_READY = False
BACKEND_ERROR = None

AI_MODULE_READY = False
AI_MODULE_ERROR = None

try:

    from backend.database import (
        create_tables,
        register_user,
        login_user,
        get_user,
        save_financial_profile,
        get_financial_profile,
        add_transaction,
        get_transactions,
        delete_transaction,
        add_recurring_bill,
        get_recurring_bills,
        deactivate_recurring_bill,
        add_financial_goal,
        get_financial_goals,
        update_financial_goal,
        delete_financial_goal,
    )

    from backend.analysis import (
        analyze_transactions,
    )

    # --------------------------------------------------------
    # AI ADVICE
    # --------------------------------------------------------

    try:

        from backend.ai_advice import (
            generate_financial_advice,
        )

        AI_MODULE_READY = True
        AI_MODULE_ERROR = None

    except Exception as e:

        AI_MODULE_READY = False
        AI_MODULE_ERROR = str(e)

        # Fallback if ai_advice.py is elsewhere
        try:

            from ai_advice import (
                generate_financial_advice,
            )

            AI_MODULE_READY = True
            AI_MODULE_ERROR = None

        except Exception as inner_error:

            AI_MODULE_READY = False
            AI_MODULE_ERROR = str(inner_error)

    # --------------------------------------------------------
    # AI FINANCIAL AGENT
    # --------------------------------------------------------

    AGENT_MODULE_READY = False
    AGENT_MODULE_ERROR = None

    try:
        from backend.financial_agent import (
            run_financial_agent,
            tool_get_financial_snapshot,
            tool_get_emergency_fund,
            tool_get_category_spending,
            tool_get_budget_status,
            tool_get_savings_goal_status,
        )

        AGENT_MODULE_READY = True
        AGENT_MODULE_ERROR = None

    except Exception as e:
        AGENT_MODULE_READY = False
        AGENT_MODULE_ERROR = str(e)

    BACKEND_READY = True

except Exception as e:

    BACKEND_READY = False
    BACKEND_ERROR = str(e)

    AGENT_MODULE_READY = False
    AGENT_MODULE_ERROR = str(e)

    AI_MODULE_READY = False
    AI_MODULE_ERROR = None


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

if BACKEND_READY:

    try:

        create_tables()

    except Exception as e:

        st.error(
            f"Database initialization failed: {e}"
        )


# ============================================================
# OLLAMA SETTINGS
# ============================================================

OLLAMA_BASE_URL = (
    "http://127.0.0.1:11434"
)

OLLAMA_MODEL = "qwen3:4b"


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_SESSION = {

    "logged_in": False,

    "user_id": None,

    "user_name": None,

    "user_email": None,

    "analysis_df": None,

    "anomaly_df": None,

    "insights": None,

    "uploaded_file_name": None,

    "ai_advice": None,

    "budget_limits": {},

    "savings_plan": {},

    "page": "Dashboard",

}


for key, value in DEFAULT_SESSION.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #777;
        margin-bottom: 1.5rem;
    }

    .metric-card {
        padding: 1rem;
        border-radius: 14px;
        border: 1px solid rgba(128,128,128,0.2);
        background: rgba(128,128,128,0.05);
        min-height: 110px;
    }

    .metric-title {
        font-size: 0.9rem;
        color: #777;
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: 750;
    }

    .success-box {
        padding: 1rem;
        border-radius: 12px;
        background: rgba(0, 180, 80, 0.10);
        border: 1px solid rgba(0, 180, 80, 0.25);
    }

    .warning-box {
        padding: 1rem;
        border-radius: 12px;
        background: rgba(255, 170, 0, 0.10);
        border: 1px solid rgba(255, 170, 0, 0.25);
    }

    .danger-box {
        padding: 1rem;
        border-radius: 12px;
        background: rgba(255, 60, 60, 0.10);
        border: 1px solid rgba(255, 60, 60, 0.25);
    }


    /* =========================================================
       FinSight-AI visual system
       ========================================================= */

    :root {
        --fs-green: #16966f;
        --fs-green-dark: #08745f;
        --fs-teal: #087f78;
        --fs-ink: #123b39;
        --fs-muted: #6d807e;
        --fs-bg: #f3faf7;
        --fs-border: #d9ebe5;
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 8%, rgba(22,150,111,0.10), transparent 30%),
            radial-gradient(circle at 88% 18%, rgba(8,127,120,0.08), transparent 28%),
            linear-gradient(180deg, #f7fcfa 0%, #eef8f4 100%);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Login */
    .auth-brand {
        text-align: center;
        margin: 2.5rem auto 1.8rem auto;
    }

    .auth-brand-name {
        color: var(--fs-ink);
        font-size: 2.35rem;
        font-weight: 800;
        letter-spacing: -0.045em;
    }

    .auth-brand-subtitle {
        color: var(--fs-muted);
        font-size: 0.92rem;
        margin-top: 0.35rem;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid var(--fs-border) !important;
        border-radius: 22px !important;
        background: rgba(255,255,255,0.92) !important;
        box-shadow: 0 18px 50px rgba(18,59,57,0.10) !important;
    }

    .auth-card-header {
        text-align: center;
        padding: 0.5rem 0 1.1rem 0;
    }

    .auth-eyebrow {
        color: var(--fs-green-dark);
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.13em;
        margin-bottom: 0.45rem;
    }

    .auth-title {
        color: var(--fs-ink);
        font-size: 1.65rem;
        font-weight: 800;
        letter-spacing: -0.025em;
    }

    .auth-description {
        color: var(--fs-muted);
        font-size: 0.86rem;
        line-height: 1.5;
        margin: 0.4rem auto 0;
        max-width: 330px;
    }

    .form-section-title {
        color: var(--fs-ink);
        font-size: 0.95rem;
        font-weight: 700;
        margin: 0.2rem 0 0.75rem;
    }

    .auth-divider {
        height: 1px;
        background: var(--fs-border);
        margin: 1rem 0 1.15rem;
    }

    .auth-helper {
        color: var(--fs-muted);
        text-align: center;
        font-size: 0.72rem;
        margin-top: 0.8rem;
        line-height: 1.45;
    }

    .auth-security {
        display: flex;
        justify-content: center;
        gap: 0.45rem;
        color: #82918f;
        font-size: 0.67rem;
        padding-top: 1rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f7fcfa 0%, #edf8f4 100%) !important;
        border-right: 1px solid var(--fs-border);
    }

    section[data-testid="stSidebar"] > div {
        padding: 1.2rem 1rem 1rem;
    }

    .sidebar-brand {
        padding: 0.35rem 0.35rem 1.15rem;
        border-bottom: 1px solid var(--fs-border);
    }

    .sidebar-brand-name {
        color: var(--fs-ink);
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.035em;
    }

    .sidebar-brand-subtitle {
        color: var(--fs-muted);
        font-size: 0.7rem;
        margin-top: 0.2rem;
    }

    .sidebar-user-card {
        background: rgba(255,255,255,0.75);
        border: 1px solid var(--fs-border);
        border-radius: 14px;
        padding: 0.8rem 0.85rem;
        margin: 1rem 0 1.2rem;
    }

    .sidebar-user-label,
    .sidebar-section-label {
        color: #78908c;
        font-size: 0.65rem;
        font-weight: 800;
        letter-spacing: 0.10em;
        text-transform: uppercase;
    }

    .sidebar-user-name {
        color: var(--fs-ink);
        font-size: 0.98rem;
        font-weight: 750;
        margin-top: 0.25rem;
    }

    .sidebar-user-email {
        color: var(--fs-muted);
        font-size: 0.68rem;
        margin-top: 0.12rem;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .sidebar-section-label {
        margin: 0.2rem 0 0.5rem 0.25rem;
    }

    .status-label {
        margin-top: 1.2rem;
    }

    div[data-testid="stRadio"] > label {
        display: none;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 0.28rem;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label {
        border-radius: 10px;
        padding: 0.58rem 0.62rem;
        color: #365b57;
        font-size: 0.84rem;
        transition: all 0.15s ease;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background: rgba(22,150,111,0.08);
        color: var(--fs-green-dark);
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
        background: rgba(22,150,111,0.12);
        color: var(--fs-green-dark);
        font-weight: 750;
    }

    input[type="radio"] {
        accent-color: var(--fs-green) !important;
    }

    .ollama-status {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        border-radius: 13px;
        padding: 0.72rem 0.78rem;
        border: 1px solid var(--fs-border);
        background: rgba(255,255,255,0.72);
    }

    .ollama-status.online {
        background: rgba(22,150,111,0.07);
    }

    .ollama-status.offline {
        background: rgba(255,190,70,0.08);
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--fs-green);
        flex: 0 0 auto;
    }

    .offline .status-dot {
        background: #c58a20;
    }

    .status-title {
        color: var(--fs-ink);
        font-size: 0.75rem;
        font-weight: 750;
    }

    .status-detail {
        color: var(--fs-muted);
        font-size: 0.65rem;
        margin-top: 0.1rem;
    }

    .sidebar-spacer {
        min-height: 4rem;
    }

    section[data-testid="stSidebar"] button[kind="secondary"] {
        border-color: var(--fs-border) !important;
        color: #365b57 !important;
        background: rgba(255,255,255,0.78) !important;
    }

    section[data-testid="stSidebar"] button[kind="secondary"]:hover {
        border-color: var(--fs-green) !important;
        color: var(--fs-green-dark) !important;
    }

    /* Financial chart renderer */
    .fs-chart-wrapper {
        margin: 0.35rem 0 1rem 0;
        padding: 1rem 1rem 0.85rem 1rem;
        border: 1px solid var(--fs-border);
        border-radius: 16px;
        background: rgba(255,255,255,0.72);
        overflow-x: auto;
    }

    .fs-chart-axis-label {
        color: var(--fs-muted);
        font-size: 0.68rem;
        font-weight: 700;
        margin-bottom: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .fs-chart-columns {
        display: flex;
        align-items: flex-end;
        justify-content: space-around;
        gap: 1.25rem;
        min-height: 300px;
        padding: 0.75rem 0.5rem 0;
        border-bottom: 1px solid var(--fs-border);
    }

    .fs-chart-column {
        flex: 1 1 0;
        min-width: 105px;
        max-width: 220px;
        height: 275px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        align-items: center;
    }

    .fs-chart-value {
        color: var(--fs-ink);
        font-size: 0.76rem;
        font-weight: 750;
        margin-bottom: 0.45rem;
        white-space: nowrap;
    }

    .fs-chart-bar-area {
        width: min(74px, 62%);
        height: 205px;
        display: flex;
        align-items: flex-end;
        justify-content: center;
        border-bottom: 1px solid rgba(22,150,111,0.12);
    }

    .fs-chart-bar {
        width: 100%;
        min-height: 12px;
        border-radius: 9px 9px 3px 3px;
        background: linear-gradient(
            180deg,
            var(--fs-green),
            var(--fs-teal)
        );
        box-shadow: 0 7px 16px rgba(22,150,111,0.16);
        transition: transform 0.15s ease;
    }

    .fs-chart-bar:hover {
        transform: translateY(-3px);
    }

    .fs-chart-label {
        width: 100%;
        margin-top: 0.65rem;
        color: #56716d;
        font-size: 0.72rem;
        line-height: 1.25;
        text-align: center;
        overflow-wrap: anywhere;
    }

    @media (max-width: 700px) {
        .fs-chart-columns {
            justify-content: flex-start;
        }

        .fs-chart-column {
            min-width: 92px;
        }
    }

    /* Buttons and inputs */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--fs-green), var(--fs-teal)) !important;
        border: none !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        min-height: 2.55rem;
    }

    .stButton > button[kind="primary"]:hover {
        filter: brightness(0.96);
        box-shadow: 0 7px 18px rgba(22,150,111,0.18);
    }

    .stButton > button[kind="secondary"] {
        border: 1px solid var(--fs-border) !important;
        border-radius: 10px !important;
        color: #3f625e !important;
        background: #ffffff !important;
        font-weight: 650 !important;
    }

    .stTextInput input {
        border-radius: 10px !important;
        border: 1px solid #d4e5e0 !important;
        background: #fbfefd !important;
        color: var(--fs-ink) !important;
        min-height: 2.65rem;
    }

    .stTextInput input:focus {
        border-color: var(--fs-green) !important;
        box-shadow: 0 0 0 1px rgba(22,150,111,0.12) !important;
    }

    .stTextInput label {
        color: #365b57 !important;
        font-weight: 650 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# GENERAL HELPERS
# ============================================================

def money(value):

    try:

        value = float(value)

    except Exception:

        value = 0.0

    return f"₹{value:,.2f}"


def safe_float(value, default=0.0):

    try:

        if value is None:

            return default

        return float(value)

    except Exception:

        return default


def clean_text(value):

    if value is None:

        return ""

    return str(value).strip()


# ============================================================
# DEPENDENCY-FREE FINANCIAL CHARTS
# ============================================================

def render_financial_bar_chart(data, value_label="Amount"):
    """Render a financial bar chart directly with Streamlit."""
    if not data:
        return

    clean_data = []

    for key, value in data.items():
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            continue

        if numeric_value < 0:
            numeric_value = 0.0

        label = str(key).strip() or "Other"
        clean_data.append((label, numeric_value))

    if not clean_data:
        return

    clean_data.sort(key=lambda item: item[1], reverse=True)

    labels = [item[0] for item in clean_data]
    values = [item[1] for item in clean_data]

    fig, ax = plt.subplots(figsize=(10, 4.8))

    bars = ax.bar(labels, values)

    ax.set_ylabel(value_label)
    ax.set_xlabel("")
    ax.set_title("Spending Breakdown", fontsize=14, pad=14)
    ax.grid(axis="y", alpha=0.20)
    ax.set_axisbelow(True)

    max_value = max(values) if values else 0
    offset = max(max_value * 0.025, 1)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + offset,
            money(value),
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    st.pyplot(fig, width="stretch")
    plt.close(fig)


# ============================================================
# DATE HELPERS
# ============================================================

def parse_dates(series):

    return pd.to_datetime(
        series,
        errors="coerce"
    )


def safe_day_name(series):

    dates = parse_dates(series)

    valid_dates = dates.dropna()

    if valid_dates.empty:

        return pd.Series(
            dtype="object"
        )

    return valid_dates.dt.day_name()


# ============================================================
# OLLAMA CONNECTION CHECK
# ============================================================

def check_ollama():

    try:

        import requests

        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=3
        )

        if response.status_code != 200:

            return False, []

        data = response.json()

        models = []

        for model in data.get(
            "models",
            []
        ):

            name = model.get(
                "name",
                ""
            )

            if name:

                models.append(name)

        return True, models

    except Exception:

        return False, []


# ============================================================
# AI RESPONSE CLEANING
# ============================================================

def clean_ai_response(text):

    if not text:

        return ""

    text = str(text).strip()

    # --------------------------------------------------------
    # Remove Qwen thinking blocks
    # --------------------------------------------------------

    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    # --------------------------------------------------------
    # Handle malformed Qwen output
    # --------------------------------------------------------

    if "</think>" in text.lower():

        parts = re.split(
            r"</think>",
            text,
            flags=re.IGNORECASE
        )

        if len(parts) > 1:

            text = parts[-1]

    # --------------------------------------------------------
    # Remove code fences
    # --------------------------------------------------------

    text = re.sub(
        r"```(?:text|markdown)?",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = text.replace(
        "```",
        ""
    )

    # --------------------------------------------------------
    # Remove obvious reasoning leakage
    # --------------------------------------------------------

    lines = text.splitlines()

    cleaned_lines = []

    unwanted_prefixes = [

        "We are to reply",
        "We must output",
        "The instruction says",
        "Since the instruction says",
        "We need to",
        "We should",
        "We are given",
        "Let's analyze",
        "Analysis:",
        "Reasoning:",
        "Thought process:",
        "Final answer:",

    ]

    for line in lines:

        stripped = line.strip()

        if not stripped:

            continue

        if any(
            stripped.lower().startswith(
                prefix.lower()
            )
            for prefix in unwanted_prefixes
        ):

            continue

        cleaned_lines.append(
            stripped
        )

    text = "\n".join(
        cleaned_lines
    ).strip()

    return text


# ============================================================
# AI SECTION PARSER
# ============================================================

def parse_ai_sections(text):

    text = clean_ai_response(text)

    result = {

        "summary": "",

        "concern": "",

        "suggestion_1": "",

        "suggestion_2": "",

    }

    if not text:

        return result

    text = text.replace(
        "\r",
        ""
    )

    # --------------------------------------------------------
    # Normalize headings
    # --------------------------------------------------------

    text = re.sub(
        r"\*\*",
        "",
        text
    )

    # --------------------------------------------------------
    # Spending Summary
    # --------------------------------------------------------

    match = re.search(
        r"Spending Summary\s*:?\s*(.*?)(?=\n\s*Main Concern\s*:|"
        r"\n\s*Two Practical Suggestions\s*:|$)",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if match:

        result["summary"] = (
            match.group(1)
            .strip()
        )

    # --------------------------------------------------------
    # Main Concern
    # --------------------------------------------------------

    match = re.search(
        r"Main Concern\s*:?\s*(.*?)(?=\n\s*Two Practical Suggestions\s*:|$)",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if match:

        result["concern"] = (
            match.group(1)
            .strip()
        )

    # --------------------------------------------------------
    # Suggestions
    # --------------------------------------------------------

    match = re.search(
        r"Two Practical Suggestions\s*:?\s*(.*)",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if match:

        suggestions_text = (
            match.group(1)
            .strip()
        )

        suggestion_matches = re.findall(
            r"(?:^|\n)\s*(?:1[\.\)]|-)\s*(.*)",
            suggestions_text
        )

        if len(suggestion_matches) >= 1:

            result["suggestion_1"] = (
                suggestion_matches[0].strip()
            )

        if len(suggestion_matches) >= 2:

            result["suggestion_2"] = (
                suggestion_matches[1].strip()
            )

    # --------------------------------------------------------
    # Additional fallback parser
    # --------------------------------------------------------

    if not result["summary"]:

        match = re.search(
            r"(?:Summary)\s*:?\s*(.*?)(?=\n|$)",
            text,
            flags=re.IGNORECASE
        )

        if match:

            result["summary"] = (
                match.group(1).strip()
            )

    if not result["concern"]:

        match = re.search(
            r"(?:Concern)\s*:?\s*(.*?)(?=\n|$)",
            text,
            flags=re.IGNORECASE
        )

        if match:

            result["concern"] = (
                match.group(1).strip()
            )

    return result


# ============================================================
# FALLBACK AI ADVICE
# ============================================================

def local_financial_advice(insights):

    if not isinstance(
        insights,
        dict
    ):

        insights = {}

    total = safe_float(
        insights.get(
            "total_spending",
            0
        )
    )

    count = int(
        safe_float(
            insights.get(
                "transaction_count",
                0
            )
        )
    )

    category = clean_text(
        insights.get(
            "highest_category",
            "Other"
        )
    )

    category_amount = safe_float(
        insights.get(
            "highest_category_amount",
            0
        )
    )

    category_percentage = safe_float(
        insights.get(
            "highest_category_percentage",
            0
        )
    )

    high_spending = int(
        safe_float(
            insights.get(
                "high_spending_transactions",
                0
            )
        )
    )

    unusual = int(
        safe_float(
            insights.get(
                "unusual_transactions",
                0
            )
        )
    )

    highest_day = clean_text(
        insights.get(
            "highest_spending_day",
            "Unknown"
        )
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    if count > 0:

        summary = (
            f"Spending totaled {money(total)} across "
            f"{count} transactions. "
            f"{category} was the highest spending category "
            f"at {money(category_amount)}."
        )

    else:

        summary = (
            "There is not enough transaction data to "
            "produce a detailed spending summary."
        )

    # --------------------------------------------------------
    # Concern
    # --------------------------------------------------------

    if category_percentage >= 50:

        concern = (
            f"{category} accounts for "
            f"{category_percentage:.1f}% of total spending, "
            f"which is a significant portion of your expenses."
        )

    elif category_percentage >= 30:

        concern = (
            f"{category} is your largest spending category, "
            f"accounting for {category_percentage:.1f}% "
            f"of total spending at {money(category_amount)}."
        )

    else:

        concern = (
            f"{category} is your highest spending category, "
            f"accounting for {category_percentage:.1f}% "
            f"of total spending."
        )

    # --------------------------------------------------------
    # Suggestion 1
    # --------------------------------------------------------

    suggestion_1 = (
        f"Review your {category} transactions and identify "
        f"one or two purchases that could be reduced "
        f"without affecting essential needs."
    )

    # --------------------------------------------------------
    # Suggestion 2
    # --------------------------------------------------------

    if unusual > 0:

        suggestion_2 = (
            f"Review the {unusual} unusual transaction"
            f"{'s' if unusual != 1 else ''} detected "
            f"before making similar purchases again."
        )

    elif highest_day and highest_day != "Unknown":

        suggestion_2 = (
            f"Monitor your spending on {highest_day}, "
            f"which was the highest-spending day in "
            f"the analyzed data."
        )

    elif high_spending > 0:

        suggestion_2 = (
            f"Review the {high_spending} transactions "
            f"that were above your average transaction amount."
        )

    else:

        suggestion_2 = (
            "Continue tracking your transactions regularly "
            "so you can identify spending patterns early."
        )

    return {

        "success": True,

        "source": "Local fallback",

        "summary": summary,

        "concern": concern,

        "suggestion_1": suggestion_1,

        "suggestion_2": suggestion_2,

        "error": None,

    }


# ============================================================
# VALIDATE AI RESULT
# ============================================================

def validate_ai_sections(sections):

    if not isinstance(
        sections,
        dict
    ):

        return False

    required = [

        "summary",

        "concern",

        "suggestion_1",

        "suggestion_2",

    ]

    for key in required:

        value = clean_text(
            sections.get(
                key,
                ""
            )
        )

        if not value:

            return False

    return True


# ============================================================
# AI FINANCIAL ADVICE
# ============================================================

def get_ai_financial_advice(insights):

    """
    Uses backend.ai_advice.py.

    If the backend returns an incomplete or unusable
    response, the application automatically uses the
    deterministic local fallback.
    """

    if not isinstance(
        insights,
        dict
    ):

        return local_financial_advice(
            {}
        )

    # --------------------------------------------------------
    # Try backend AI module
    # --------------------------------------------------------

    if AI_MODULE_READY:

        try:

            raw_result = generate_financial_advice(
                insights
            )

            # ------------------------------------------------
            # String response
            # ------------------------------------------------

            if isinstance(
                raw_result,
                str
            ):

                cleaned = clean_ai_response(
                    raw_result
                )

                sections = parse_ai_sections(
                    cleaned
                )

                if validate_ai_sections(
                    sections
                ):

                    return {

                        "success": True,

                        "source":
                            "Ollama / Qwen3",

                        "summary":
                            sections["summary"],

                        "concern":
                            sections["concern"],

                        "suggestion_1":
                            sections["suggestion_1"],

                        "suggestion_2":
                            sections["suggestion_2"],

                        "error": None,

                    }

                # ------------------------------------------------
                # Incomplete Qwen response
                # ------------------------------------------------

                fallback = local_financial_advice(
                    insights
                )

                fallback["source"] = (
                    "Local fallback "
                    "(AI response incomplete)"
                )

                return fallback

            # ------------------------------------------------
            # Dictionary response
            # ------------------------------------------------

            if isinstance(
                raw_result,
                dict
            ):

                if raw_result.get(
                    "success",
                    False
                ):

                    # Check if dictionary contains
                    # complete advice fields.

                    sections = {

                        "summary":
                            raw_result.get(
                                "summary",
                                ""
                            ),

                        "concern":
                            raw_result.get(
                                "concern",
                                ""
                            ),

                        "suggestion_1":
                            raw_result.get(
                                "suggestion_1",
                                ""
                            ),

                        "suggestion_2":
                            raw_result.get(
                                "suggestion_2",
                                ""
                            ),

                    }

                    if validate_ai_sections(
                        sections
                    ):

                        return {

                            "success": True,

                            "source":
                                raw_result.get(
                                    "source",
                                    "Ollama / Qwen3"
                                ),

                            "summary":
                                sections["summary"],

                            "concern":
                                sections["concern"],

                            "suggestion_1":
                                sections["suggestion_1"],

                            "suggestion_2":
                                sections["suggestion_2"],

                            "error": None,

                        }

                fallback = local_financial_advice(
                    insights
                )

                fallback["source"] = (
                    "Local fallback"
                )

                return fallback

        except Exception as e:

            fallback = local_financial_advice(
                insights
            )

            fallback["source"] = (
                "Local fallback "
                "(Ollama unavailable)"
            )

            fallback["error"] = str(e)

            return fallback

    # --------------------------------------------------------
    # AI module unavailable
    # --------------------------------------------------------

    return local_financial_advice(
        insights
    )



# ============================================================
# SMART AI TRANSACTION CATEGORIZATION
# ============================================================

FINANCIAL_CATEGORIES = [
    "Food",
    "Medical/Hospital",
    "Education/Tuition",
    "Hotel/Travel",
    "Shopping",
    "Transport",
    "Utilities",
    "Family",
    "Entertainment",
    "Rent/Home",
    "Savings",
    "Other",
]


CATEGORY_KEYWORDS = {
    "Food": [
        "restaurant", "food", "grocery", "groceries", "supermarket",
        "swiggy", "zomato", "zepto", "blinkit", "bigbasket",
        "cafe", "coffee", "bakery", "pizza", "burger", "hotel food",
    ],
    "Medical/Hospital": [
        "hospital", "clinic", "doctor", "medical", "medicine",
        "pharmacy", "medicines", "diagnostic", "lab test",
        "health", "apollo", "medplus",
    ],
    "Education/Tuition": [
        "tuition", "college", "school", "education", "course",
        "exam", "udemy", "coursera", "training", "books",
        "stationery", "academy", "fees", "fee",
    ],
    "Hotel/Travel": [
        "hotel", "airbnb", "booking.com", "booking", "flight",
        "airline", "train", "irctc", "bus", "travel", "trip",
        "resort", "oyo", "make my trip", "makemytrip",
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "shopping", "clothing",
        "clothes", "electronics", "purchase", "store", "mall",
        "retail", "ajio", "meesho",
    ],
    "Transport": [
        "uber", "ola", "auto", "taxi", "cab", "metro", "fuel",
        "petrol", "diesel", "parking", "transport",
    ],
    "Utilities": [
        "electricity", "water bill", "internet", "wifi", "broadband",
        "mobile", "phone bill", "recharge", "jio", "airtel",
        "vi ", "bsnl", "utility", "gas bill",
    ],
    "Family": [
        "family", "mother", "father", "parents", "parent",
        "brother", "sister", "home support", "family support",
    ],
    "Entertainment": [
        "netflix", "prime video", "spotify", "youtube premium",
        "movie", "cinema", "gaming", "game", "entertainment",
        "subscription", "concert",
    ],
    "Rent/Home": [
        "rent", "house rent", "apartment", "housing", "maintenance",
        "home", "furniture", "household",
    ],
    "Savings": [
        "savings", "investment", "deposit", "mutual fund",
        "fixed deposit", "recurring deposit", "sip",
    ],
}


def keyword_transaction_category(description):
    """
    Fast deterministic first-pass categorization.

    This is deliberately used before the local LLM so that common
    merchants/categories are classified quickly and consistently.
    """
    text = clean_text(description).lower()

    if not text:
        return "Other"

    # More specific categories first.
    ordered_categories = [
        "Medical/Hospital",
        "Education/Tuition",
        "Hotel/Travel",
        "Utilities",
        "Transport",
        "Rent/Home",
        "Family",
        "Entertainment",
        "Food",
        "Shopping",
        "Savings",
    ]

    for category in ordered_categories:
        keywords = CATEGORY_KEYWORDS.get(category, [])

        for keyword in keywords:
            if keyword.strip() in text:
                return category

    return "Other"


def ai_transaction_category(description):
    """
    Categorize one transaction using the local Ollama/Qwen model.

    Keyword matching is the fast fallback. The LLM is only called when
    the deterministic rules cannot confidently classify the description.
    """
    description = clean_text(description)

    if not description:
        return "Other"

    keyword_category = keyword_transaction_category(description)

    if keyword_category != "Other":
        return keyword_category

    try:
        import requests

        prompt = f"""
You are a personal finance transaction classifier.

Classify this transaction into exactly ONE category from this list:
{", ".join(FINANCIAL_CATEGORIES)}

Transaction description:
{description}

Rules:
- Return ONLY the category name.
- Do not explain.
- Do not return punctuation.
- If uncertain, return Other.
"""

        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt.strip(),
                "stream": False,
                "options": {
                    "temperature": 0,
                },
            },
            timeout=20,
        )

        if response.status_code != 200:
            return "Other"

        payload = response.json()

        raw = clean_ai_response(
            payload.get("response", "")
        ).strip()

        # Exact category match first.
        for category in FINANCIAL_CATEGORIES:
            if raw.lower() == category.lower():
                return category

        # Handle minor formatting differences safely.
        normalized = re.sub(
            r"[^a-zA-Z/ ]",
            "",
            raw
        ).strip().lower()

        for category in FINANCIAL_CATEGORIES:
            category_normalized = re.sub(
                r"[^a-zA-Z/ ]",
                "",
                category
            ).strip().lower()

            if normalized == category_normalized:
                return category

    except Exception:
        pass

    return "Other"


def categorize_transactions(df):
    """
    Add/update the category column for uploaded transactions.

    Existing non-empty user-provided categories are preserved.
    Missing or generic 'Other' categories are intelligently classified.
    """
    if df is None or df.empty:
        return df

    result = df.copy()

    if "description" not in result.columns:
        result["description"] = ""

    if "category" not in result.columns:
        result["category"] = "Other"

    result["category"] = (
        result["category"]
        .fillna("Other")
        .astype(str)
        .str.strip()
    )

    result.loc[
        result["category"] == "",
        "category"
    ] = "Other"

    categorized = []

    for _, row in result.iterrows():
        current_category = clean_text(
            row.get("category", "Other")
        )

        # Preserve meaningful existing categories.
        if (
            current_category
            and current_category.lower() != "other"
        ):
            categorized.append(current_category)
            continue

        categorized.append(
            ai_transaction_category(
                row.get("description", "")
            )
        )

    result["category"] = categorized

    return result


# ============================================================
# CSV NORMALIZATION
# ============================================================

def normalize_uploaded_csv(uploaded_file):

    try:

        df = pd.read_csv(
            uploaded_file
        )

    except Exception as e:

        raise ValueError(
            f"Could not read CSV: {e}"
        )

    if df.empty:

        raise ValueError(
            "The uploaded CSV is empty."
        )

    # --------------------------------------------------------
    # Normalize column names
    # --------------------------------------------------------

    df.columns = [

        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")

        for column in df.columns

    ]

    # --------------------------------------------------------
    # Column aliases
    # --------------------------------------------------------

    aliases = {

        "transaction_date":
            "date",

        "transactiondate":
            "date",

        "trans_date":
            "date",

        "details":
            "description",

        "merchant":
            "description",

        "name":
            "description",

        "transaction":
            "description",

        "value":
            "amount",

        "price":
            "amount",

        "cost":
            "amount",

        "expense":
            "amount",

    }

    rename_map = {}

    for old, new in aliases.items():

        if (
            old in df.columns
            and new not in df.columns
        ):

            rename_map[old] = new

    if rename_map:

        df = df.rename(
            columns=rename_map
        )

    required = [

        "date",

        "description",

        "amount"

    ]

    missing = [

        column
        for column in required
        if column not in df.columns

    ]

    if missing:

        raise ValueError(
            "Missing required CSV columns: "
            + ", ".join(missing)
            + ". Required columns are: "
            + ", ".join(required)
        )

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Description
    # --------------------------------------------------------

    df["description"] = (
        df["description"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # Amount
    # --------------------------------------------------------

    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(
            ",",
            "",
            regex=False
        )
        .str.replace(
            "₹",
            "",
            regex=False
        )
        .str.replace(
            "$",
            "",
            regex=False
        )
        .str.strip()
    )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Remove invalid rows
    # --------------------------------------------------------

    df = df.dropna(
        subset=[
            "date",
            "amount"
        ]
    ).copy()

    df = df[
        df["amount"] > 0
    ].copy()

    if df.empty:

        raise ValueError(
            "No valid positive transactions were found."
        )

    df = df.reset_index(
        drop=True
    )

    return df


# ============================================================
# LOCAL TRUSTED ANALYSIS
# ============================================================

def calculate_dashboard_insights(df):

    empty_result = {

        "total_spending": 0.0,

        "transaction_count": 0,

        "average_transaction": 0.0,

        "highest_transaction": 0.0,

        "highest_category": "None",

        "highest_category_amount": 0.0,

        "highest_category_percentage": 0.0,

        "highest_spending_day": "None",

        "unusual_transactions": 0,

        "high_spending_transactions": 0,

        "category_spending": {},

        "monthly_spending": {},

        "day_spending": {},

        "category_percentages": {},

        "top_transactions": [],

        "spending_concentration": 0.0,

    }

    if df is None or df.empty:

        return empty_result

    data = df.copy()

    # --------------------------------------------------------
    # Dates
    # --------------------------------------------------------

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce"
    )

    data = data.dropna(
        subset=["date"]
    ).copy()

    # --------------------------------------------------------
    # Amount
    # --------------------------------------------------------

    data["amount"] = pd.to_numeric(
        data["amount"],
        errors="coerce"
    )

    data = data.dropna(
        subset=["amount"]
    ).copy()

    data = data[
        data["amount"] > 0
    ]

    if data.empty:

        return empty_result

    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    if "category" not in data.columns:

        data["category"] = "Other"

    data["category"] = (
        data["category"]
        .fillna("Other")
        .astype(str)
        .str.strip()
    )

    data.loc[
        data["category"] == "",
        "category"
    ] = "Other"

    # --------------------------------------------------------
    # Basic statistics
    # --------------------------------------------------------

    total = float(
        data["amount"].sum()
    )

    count = int(
        len(data)
    )

    average = float(
        data["amount"].mean()
    )

    highest_transaction = float(
        data["amount"].max()
    )

    # --------------------------------------------------------
    # Category analysis
    # --------------------------------------------------------

    category_spending = (
        data.groupby(
            "category"
        )["amount"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    if not category_spending.empty:

        highest_category = str(
            category_spending.index[0]
        )

        highest_category_amount = float(
            category_spending.iloc[0]
        )

    else:

        highest_category = "None"

        highest_category_amount = 0.0

    highest_category_percentage = (

        (
            highest_category_amount
            / total
        ) * 100

        if total > 0

        else 0.0

    )

    # --------------------------------------------------------
    # Day analysis
    # --------------------------------------------------------

    day_series = (
        data
        .assign(
            day_name=lambda x:
                x["date"].dt.day_name()
        )
        .groupby(
            "day_name"
        )["amount"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    if not day_series.empty:

        highest_day = str(
            day_series.index[0]
        )

    else:

        highest_day = "None"

    # --------------------------------------------------------
    # Monthly analysis
    # --------------------------------------------------------

    month_series = (
        data
        .assign(
            month=lambda x:
                x["date"]
                .dt.to_period("M")
                .astype(str)
        )
        .groupby(
            "month"
        )["amount"]
        .sum()
        .sort_index()
    )

    # --------------------------------------------------------
    # IQR anomaly detection
    # --------------------------------------------------------

    if len(data) >= 4:

        q1 = float(
            data["amount"].quantile(
                0.25
            )
        )

        q3 = float(
            data["amount"].quantile(
                0.75
            )
        )

        iqr = q3 - q1

        lower = q1 - (
            1.5 * iqr
        )

        upper = q3 + (
            1.5 * iqr
        )

        unusual = int(
            (
                (data["amount"] < lower)
                |
                (data["amount"] > upper)
            ).sum()
        )

    else:

        unusual = 0

    # --------------------------------------------------------
    # High spending
    # --------------------------------------------------------

    high_spending = int(
        (
            data["amount"]
            > average
        ).sum()
    )

    return {

        "total_spending":
            total,

        "transaction_count":
            count,

        "average_transaction":
            average,

        "highest_transaction":
            highest_transaction,

        "highest_category":
            highest_category,

        "highest_category_amount":
            highest_category_amount,

        "highest_category_percentage":
            highest_category_percentage,

        "highest_spending_day":
            highest_day,

        "unusual_transactions":
            unusual,

        "high_spending_transactions":
            high_spending,

        "category_spending":
            {
                str(k): float(v)
                for k, v
                in category_spending.items()
            },

        "monthly_spending":
            {
                str(k): float(v)
                for k, v
                in month_series.items()
            },

        "day_spending":
            {
                str(k): float(v)
                for k, v
                in day_series.sort_values(ascending=False).items()
            },

        "category_percentages":
            {
                str(k): float((v / total) * 100)
                for k, v
                in category_spending.items()
            },

        "top_transactions":
            data.nlargest(5, "amount")[
                [c for c in ["date", "description", "amount", "category"] if c in data.columns]
            ].to_dict("records"),

        "spending_concentration":
            float(
                (category_spending.head(3).sum() / total) * 100
            ) if total > 0 else 0.0,

    }


# ============================================================
# SMART AI ANOMALY DETECTION
# ============================================================

def detect_transaction_anomalies(df):
    """
    Detect unusually large transactions using robust statistical rules.

    A transaction is flagged when it is either:
    - above the global IQR upper fence, or
    - substantially above the mean using a z-score of 2 or more.

    The function also provides a human-readable reason for each anomaly.
    """
    if df is None or df.empty:
        return pd.DataFrame(), {
            "count": 0,
            "method": "IQR + z-score",
        }

    data = df.copy()

    if "amount" not in data.columns:
        return pd.DataFrame(), {
            "count": 0,
            "method": "IQR + z-score",
        }

    data["amount"] = pd.to_numeric(
        data["amount"],
        errors="coerce"
    )

    data = data.dropna(subset=["amount"]).copy()
    data = data[data["amount"] > 0].copy()

    if data.empty:
        return pd.DataFrame(), {
            "count": 0,
            "method": "IQR + z-score",
        }

    mean_amount = float(data["amount"].mean())
    std_amount = float(data["amount"].std(ddof=0))

    q1 = float(data["amount"].quantile(0.25))
    q3 = float(data["amount"].quantile(0.75))
    iqr = q3 - q1
    upper_fence = q3 + (1.5 * iqr)

    if std_amount > 0:
        data["z_score"] = (
            (data["amount"] - mean_amount) / std_amount
        )
    else:
        data["z_score"] = 0.0

    data["iqr_flag"] = data["amount"] > upper_fence
    data["z_flag"] = data["z_score"] >= 2.0
    data["anomaly"] = data["iqr_flag"] | data["z_flag"]

    anomalies = data[data["anomaly"]].copy()

    if anomalies.empty:
        return pd.DataFrame(), {
            "count": 0,
            "method": "IQR + z-score",
            "mean": mean_amount,
            "upper_fence": upper_fence,
        }

    reasons = []

    for _, row in anomalies.iterrows():
        amount = float(row["amount"])
        z = float(row["z_score"])
        iqr_flag = bool(row["iqr_flag"])
        z_flag = bool(row["z_flag"])

        if iqr_flag and z_flag:
            reason = (
                f"{money(amount)} is far above your normal transaction range "
                f"and is {z:.1f} standard deviations above the average."
            )
        elif iqr_flag:
            reason = (
                f"{money(amount)} is above the statistical upper spending "
                f"limit of {money(upper_fence)}."
            )
        else:
            reason = (
                f"{money(amount)} is unusually high compared with your "
                f"average transaction of {money(mean_amount)}."
            )

        reasons.append(reason)

    anomalies["reason"] = reasons

    if "date" in anomalies.columns:
        anomalies["date"] = pd.to_datetime(
            anomalies["date"],
            errors="coerce"
        )

    return anomalies, {
        "count": int(len(anomalies)),
        "method": "IQR + z-score",
        "mean": mean_amount,
        "upper_fence": upper_fence,
    }


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    # Clean brand header
    st.markdown(
        """
        <div class="auth-brand">
            <div class="auth-brand-name">FinSight-AI</div>
            <div class="auth-brand-subtitle">Personal Finance Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Keep the authentication experience compact and centered.
    left, center, right = st.columns([1.15, 0.9, 1.15])

    with center:

        if "auth_mode" not in st.session_state:
            st.session_state.auth_mode = "login"

        with st.container(border=True):

            st.markdown(
                """
                <div class="auth-card-header">
                    <div class="auth-eyebrow">SECURE ACCESS</div>
                    <div class="auth-title">Welcome back</div>
                    <div class="auth-description">
                        Sign in to continue to your personal finance dashboard.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            login_col, register_col = st.columns(2, gap="small")

            with login_col:
                if st.button(
                    "Sign in",
                    width="stretch",
                    type="primary" if st.session_state.auth_mode == "login" else "secondary",
                    key="auth_login_tab",
                ):
                    st.session_state.auth_mode = "login"
                    st.rerun()

            with register_col:
                if st.button(
                    "Create account",
                    width="stretch",
                    type="primary" if st.session_state.auth_mode == "register" else "secondary",
                    key="auth_register_tab",
                ):
                    st.session_state.auth_mode = "register"
                    st.rerun()

            st.markdown('<div class="auth-divider"></div>', unsafe_allow_html=True)

            if st.session_state.auth_mode == "login":

                st.markdown('<div class="form-section-title">Sign in to FinSight-AI</div>', unsafe_allow_html=True)

                email = st.text_input(
                    "Email address",
                    placeholder="you@example.com",
                    key="login_email",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    key="login_password",
                )

                if st.button(
                    "Sign in to dashboard",
                    width="stretch",
                    type="primary",
                    key="login_submit",
                ):

                    if not email or not password:
                        st.warning("Please enter your email and password.")
                    else:
                        try:
                            result = login_user(email.strip(), password)

                            if result:
                                user_id, name = result
                                user = get_user(user_id)

                                st.session_state.logged_in = True
                                st.session_state.user_id = user_id
                                st.session_state.user_name = name

                                if user:
                                    st.session_state.user_email = user[2]

                                st.session_state.analysis_df = None
                                st.session_state.anomaly_df = None
                                st.session_state.insights = None
                                st.session_state.uploaded_file_name = None
                                st.session_state.ai_advice = None
                                st.session_state.page = "Dashboard"

                                st.rerun()
                            else:
                                st.error("Invalid email or password.")

                        except Exception as e:
                            st.error(f"Login error: {e}")

                st.markdown(
                    '<div class="auth-helper">Your financial information stays inside your FinSight-AI account.</div>',
                    unsafe_allow_html=True,
                )

            else:

                st.markdown('<div class="form-section-title">Create your account</div>', unsafe_allow_html=True)

                name = st.text_input(
                    "Full name",
                    placeholder="Enter your name",
                    key="register_name",
                )

                reg_email = st.text_input(
                    "Email address",
                    placeholder="you@example.com",
                    key="register_email",
                )

                reg_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Create a password",
                    key="register_password",
                )

                if st.button(
                    "Create my account",
                    width="stretch",
                    type="primary",
                    key="register_submit",
                ):

                    if not name or not reg_email or not reg_password:
                        st.warning("Please complete all registration fields.")
                    elif len(reg_password) < 6:
                        st.warning("Password should contain at least 6 characters.")
                    else:
                        try:
                            success, user_id = register_user(
                                name.strip(),
                                reg_email.strip(),
                                reg_password,
                            )

                            if success:
                                st.session_state.auth_mode = "login"
                                st.rerun()
                            else:
                                st.error("An account with this email already exists.")

                        except Exception as e:
                            st.error(f"Registration error: {e}")

            st.markdown(
                """
                <div class="auth-security">
                    <span>Secure account access</span>
                    <span>•</span>
                    <span>Personal finance dashboard</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# SIDEBAR
# ============================================================

def sidebar():

    with st.sidebar:

        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-name">FinSight-AI</div>
                <div class="sidebar-brand-subtitle">Personal Finance Intelligence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="sidebar-user-card">
                <div class="sidebar-user-label">SIGNED IN AS</div>
                <div class="sidebar-user-name">{st.session_state.user_name or 'User'}</div>
                <div class="sidebar-user-email">{st.session_state.user_email or ''}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-section-label">Workspace</div>', unsafe_allow_html=True)

        pages = [
            "Dashboard",
            "Transaction Analysis",
            "Budget Planner",
            "Savings Planner",
            "Emergency Fund",
            "Financial Health",
            "AI Financial Agent",
            "Recurring Bills",
            "Financial Goals",
        ]

        current_page = st.session_state.page
        if current_page not in pages:
            current_page = "Dashboard"

        page = st.radio(
            "Navigation",
            pages,
            index=pages.index(current_page),
            label_visibility="collapsed",
            key="main_navigation",
        )

        st.session_state.page = page

        st.markdown('<div class="sidebar-section-label status-label">System status</div>', unsafe_allow_html=True)

        connected, models = check_ollama()

        if connected:
            if OLLAMA_MODEL in models:
                available_model = OLLAMA_MODEL
            elif models:
                available_model = models[0]
            else:
                available_model = "No models"

            st.markdown(
                f"""
                <div class="ollama-status online">
                    <div class="status-dot"></div>
                    <div>
                        <div class="status-title">AI assistant online</div>
                        <div class="status-detail">{available_model}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="ollama-status offline">
                    <div class="status-dot"></div>
                    <div>
                        <div class="status-title">AI assistant offline</div>
                        <div class="status-detail">Start Ollama to enable advice</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)

        if st.button(
            "Log out",
            width="stretch",
            key="sidebar_logout",
        ):
            for key, value in DEFAULT_SESSION.items():
                st.session_state[key] = value
            st.rerun()


# ============================================================
# FINANCIAL PROFILE
# ============================================================

def financial_profile_form():

    st.subheader(
        "💵 Personal Finance Information"
    )

    st.caption(
        "Enter your current financial information. "
        "FinSight-AI combines this information with "
        "your transaction data."
    )

    existing = get_financial_profile(
        st.session_state.user_id
    )

    if existing:

        current_income = safe_float(
            existing[0]
        )

        current_savings = safe_float(
            existing[1]
        )

        current_family = safe_float(
            existing[2]
        )

        current_goal = safe_float(
            existing[3]
        )

    else:

        current_income = 0.0
        current_savings = 0.0
        current_family = 0.0
        current_goal = 0.0

    c1, c2 = st.columns(2)

    with c1:

        income = st.number_input(
            "💵 Monthly Income (₹)",
            min_value=0.0,
            value=current_income,
            step=1000.0
        )

        savings = st.number_input(
            "🏦 Current Savings (₹)",
            min_value=0.0,
            value=current_savings,
            step=1000.0
        )

    with c2:

        family_support = st.number_input(
            "👨‍👩‍👧 Family Support (₹)",
            min_value=0.0,
            value=current_family,
            step=500.0
        )

        savings_goal = st.number_input(
            "🎯 Monthly Savings Goal (₹)",
            min_value=0.0,
            value=current_goal,
            step=500.0
        )

    if st.button(
        "💾 Save Financial Information",
        width="stretch"
    ):

        try:

            save_financial_profile(

                st.session_state.user_id,

                income,

                savings,

                family_support,

                savings_goal

            )

            st.success(
                "Financial information saved successfully."
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Could not save financial information: {e}"
            )


# ============================================================
# DASHBOARD
# ============================================================

def dashboard_page():

    st.title(
        " FinSight-AI"
    )

    st.subheader(
        f"👋 Welcome, {st.session_state.user_name}"
    )

    st.caption(
        "Your personal financial overview."
    )

    st.divider()

    financial_profile_form()

    st.divider()

    profile = get_financial_profile(
        st.session_state.user_id
    )

    if profile:

        income = safe_float(
            profile[0]
        )

        current_savings = safe_float(
            profile[1]
        )

        family_support = safe_float(
            profile[2]
        )

        monthly_goal = safe_float(
            profile[3]
        )

    else:

        income = 0.0
        current_savings = 0.0
        family_support = 0.0
        monthly_goal = 0.0

    # --------------------------------------------------------
    # Expenses
    # --------------------------------------------------------

    expenses = 0.0

    try:

        transactions = get_transactions(
            st.session_state.user_id
        )

    except Exception:

        transactions = []

    if transactions:

        for row in transactions:

            amount = safe_float(
                row[3]
            )

            transaction_type = (
                str(row[5])
                .lower()
                .strip()
            )

            if transaction_type in [

                "expense",
                "debit",
                "spending",
                "spent",
                ""

            ]:

                expenses += amount

    if st.session_state.insights:

        expenses = safe_float(
            st.session_state.insights.get(
                "total_spending",
                expenses
            )
        )

    remaining = (
        income
        - expenses
        - family_support
    )

    # --------------------------------------------------------
    # Overview
    # --------------------------------------------------------

    st.subheader(
        " Financial Overview"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "💵 Monthly Income",
        money(income)
    )

    c2.metric(
        "💳 Expenses",
        money(expenses)
    )

    c3.metric(
        "👨‍👩‍👧 Family Support",
        money(family_support)
    )

    c4.metric(
        " Remaining",
        money(remaining)
    )

    st.divider()

    # --------------------------------------------------------
    # Savings
    # --------------------------------------------------------

    st.subheader(
        "🏦 Savings Overview"
    )

    s1, s2, s3 = st.columns(3)

    s1.metric(
        "Current Savings",
        money(current_savings)
    )

    s2.metric(
        "Monthly Savings Goal",
        money(monthly_goal)
    )

    available_above_goal = (
        remaining
        - monthly_goal
    )

    if available_above_goal >= 0:

        s3.success(
            "✅ Savings Goal On Track"
        )

        st.write(
            "Available above goal: "
            f"**{money(available_above_goal)}**"
        )

    else:

        s3.error(
            "⚠️ Savings Goal Needs Attention"
        )

        st.write(
            "Shortfall to monthly goal: "
            f"**{money(abs(available_above_goal))}**"
        )

    st.divider()

    # --------------------------------------------------------
    # Quick statistics
    # --------------------------------------------------------

    st.subheader(
        "📊 Quick Financial Statistics"
    )

    if st.session_state.insights:

        insights = st.session_state.insights

        q1, q2, q3, q4 = st.columns(4)

        q1.metric(
            "🧾 Transactions",
            str(
                insights.get(
                    "transaction_count",
                    0
                )
            )
        )

        q2.metric(
            "💸 Average Expense",
            money(
                insights.get(
                    "average_transaction",
                    0
                )
            )
        )

        q3.metric(
            "🔝 Highest Expense",
            money(
                insights.get(
                    "highest_transaction",
                    0
                )
            )
        )

        q4.metric(
            "🏆 Top Category",
            insights.get(
                "highest_category",
                "None"
            )
        )

    else:

        st.info(
            "📁 Upload a transaction CSV from "
            "**Transaction Analysis** to see detailed statistics."
        )


# ============================================================
# TRANSACTION ANALYSIS
# ============================================================


def build_spending_pattern_analysis(df, insights):

    """Build human-readable spending pattern intelligence from verified data."""

    result = {
        "pattern_level": "Balanced",
        "pattern_message": "Your spending is distributed across several categories.",
        "top_category": insights.get("highest_category", "None"),
        "top_category_share": safe_float(insights.get("highest_category_percentage", 0)),
        "top_3_share": safe_float(insights.get("spending_concentration", 0)),
        "largest_transaction": safe_float(insights.get("highest_transaction", 0)),
        "largest_transaction_description": "",
        "most_active_day": insights.get("highest_spending_day", "None"),
        "most_active_day_amount": 0.0,
        "recommendation": "Continue monitoring your largest spending categories and transactions.",
    }

    if df is None or df.empty:
        return result

    data = df.copy()

    if "amount" not in data.columns:
        return result

    data["amount"] = pd.to_numeric(data["amount"], errors="coerce")
    data = data.dropna(subset=["amount"])
    data = data[data["amount"] > 0].copy()

    if data.empty:
        return result

    # Largest transaction
    largest = data.loc[data["amount"].idxmax()]
    if "description" in data.columns:
        result["largest_transaction_description"] = str(
            largest.get("description", "Transaction")
        )

    # Day with highest total spending
    if "date" in data.columns:
        data["date"] = pd.to_datetime(data["date"], errors="coerce")
        valid_dates = data.dropna(subset=["date"])
        if not valid_dates.empty:
            day_totals = valid_dates.groupby(
                valid_dates["date"].dt.day_name()
            )["amount"].sum().sort_values(ascending=False)
            if not day_totals.empty:
                result["most_active_day"] = str(day_totals.index[0])
                result["most_active_day_amount"] = float(day_totals.iloc[0])

    # Concentration interpretation
    top_share = result["top_3_share"]
    if top_share >= 80:
        result["pattern_level"] = "Highly concentrated"
        result["pattern_message"] = (
            "Most of your spending is concentrated in a small number of categories."
        )
        result["recommendation"] = (
            "Review the top three categories first. Small reductions there can have the biggest impact."
        )
    elif top_share >= 60:
        result["pattern_level"] = "Moderately concentrated"
        result["pattern_message"] = (
            "A few categories account for most of your spending."
        )
        result["recommendation"] = (
            "Keep the largest categories within planned limits and monitor them each month."
        )
    else:
        result["pattern_level"] = "Distributed"
        result["pattern_message"] = (
            "Your spending is relatively distributed rather than dominated by only a few categories."
        )
        result["recommendation"] = (
            "Continue tracking category totals so gradual increases are visible early."
        )

    return result

def transaction_analysis_page():

    st.title(
        "📁 Transaction Analysis"
    )

    st.caption(
        "Upload your transaction CSV to analyze your spending."
    )

    uploaded_file = st.file_uploader(
        "Upload your transactions CSV",
        type=["csv"]
    )

    if uploaded_file is not None:

        if (
            st.session_state.uploaded_file_name
            != uploaded_file.name
        ):

            st.session_state.uploaded_file_name = (
                uploaded_file.name
            )

            st.session_state.analysis_df = None

            st.session_state.anomaly_df = None

            st.session_state.insights = None

            st.session_state.ai_advice = None

        if st.button(
            "🔍 Analyze Transactions",
            width="stretch"
        ):

            try:

                # ------------------------------------------------
                # Normalize
                # ------------------------------------------------

                normalized_df = (
                    normalize_uploaded_csv(
                        uploaded_file
                    )
                )

                # ------------------------------------------------
                # Temporary file
                # ------------------------------------------------

                temp_dir = os.path.join(
                    PROJECT_ROOT,
                    "data"
                )

                os.makedirs(
                    temp_dir,
                    exist_ok=True
                )

                temp_path = os.path.join(
                    temp_dir,
                    "_temp_transactions.csv"
                )

                normalized_df.to_csv(
                    temp_path,
                    index=False
                )

                # ------------------------------------------------
                # Backend analysis
                # ------------------------------------------------

                try:

                    analyzed_df, backend_insights = (
                        analyze_transactions(
                            temp_path
                        )
                    )

                except Exception:

                    analyzed_df = (
                        normalized_df.copy()
                    )

                    backend_insights = {}

                # ------------------------------------------------
                # Normalize analyzed dataframe
                # ------------------------------------------------

                if analyzed_df is None:

                    analyzed_df = (
                        normalized_df.copy()
                    )

                analyzed_df = analyzed_df.copy()

                analyzed_df["date"] = (
                    pd.to_datetime(
                        analyzed_df["date"],
                        errors="coerce"
                    )
                )

                analyzed_df["amount"] = (
                    pd.to_numeric(
                        analyzed_df["amount"],
                        errors="coerce"
                    )
                )

                # ------------------------------------------------
                # Smart transaction categorization
                # ------------------------------------------------

                analyzed_df = categorize_transactions(
                    analyzed_df
                )

                analyzed_df["category"] = (
                    analyzed_df["category"]
                    .fillna("Other")
                    .astype(str)
                    .str.strip()
                )

                analyzed_df.loc[
                    analyzed_df["category"] == "",
                    "category"
                ] = "Other"

                # ------------------------------------------------
                # Smart anomaly detection
                # ------------------------------------------------

                anomaly_df, anomaly_summary = (
                    detect_transaction_anomalies(
                        analyzed_df
                    )
                )

                # ------------------------------------------------
                # Trusted local statistics
                # ------------------------------------------------

                local_insights = (
                    calculate_dashboard_insights(
                        analyzed_df
                    )
                )

                local_insights["unusual_transactions"] = (
                    int(anomaly_summary.get("count", 0))
                )

                local_insights["anomaly_method"] = (
                    anomaly_summary.get(
                        "method",
                        "IQR + z-score"
                    )
                )

                local_insights["anomaly_mean"] = (
                    float(anomaly_summary.get("mean", 0.0))
                )

                local_insights["anomaly_upper_fence"] = (
                    float(anomaly_summary.get("upper_fence", 0.0))
                )

                # ------------------------------------------------
                # Keep only non-core backend fields
                # ------------------------------------------------

                if isinstance(
                    backend_insights,
                    dict
                ):

                    protected = {

                        "total_spending",

                        "transaction_count",

                        "average_transaction",

                        "highest_transaction",

                        "highest_category",

                        "highest_category_amount",

                        "highest_category_percentage",

                        "highest_spending_day",

                        "unusual_transactions",

                        "high_spending_transactions",

                        "category_spending",

                        "monthly_spending",

                        "day_spending",

                        "category_percentages",

                        "top_transactions",

                        "spending_concentration",

                    }

                    for key, value in backend_insights.items():

                        if key not in protected:

                            local_insights[
                                key
                            ] = value

                # ------------------------------------------------
                # Save state
                # ------------------------------------------------

                st.session_state.analysis_df = (
                    analyzed_df
                )

                st.session_state.anomaly_df = (
                    anomaly_df
                )

                local_insights["spending_pattern"] = (
                    build_spending_pattern_analysis(
                        analyzed_df,
                        local_insights
                    )
                )

                st.session_state.insights = (
                    local_insights
                )

                st.session_state.ai_advice = None

                st.success(
                    "Transaction analysis completed!"
                )

            except Exception as e:

                st.error(
                    f"Transaction analysis failed: {e}"
                )

    # ========================================================
    # SHOW RESULTS
    # ========================================================

    df = st.session_state.analysis_df

    insights = st.session_state.insights

    if df is None or insights is None:

        st.info(
            "Upload a CSV and click "
            "**Analyze Transactions** to begin."
        )

        return

    # --------------------------------------------------------
    # Financial profile
    # --------------------------------------------------------

    profile = get_financial_profile(
        st.session_state.user_id
    )

    if profile:

        income = safe_float(
            profile[0]
        )

        family_support = safe_float(
            profile[2]
        )

    else:

        income = 0.0

        family_support = 0.0

    total_spending = safe_float(
        insights.get(
            "total_spending",
            0
        )
    )

    remaining = (
        income
        - total_spending
        - family_support
    )

    # --------------------------------------------------------
    # Financial overview
    # --------------------------------------------------------

    st.subheader(
        " Financial Overview"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "💵 Monthly Income",
        money(income)
    )

    c2.metric(
        "💳 Expenses",
        money(total_spending)
    )

    c3.metric(
        "👨‍👩‍👧 Family Support",
        money(family_support)
    )

    c4.metric(
        " Remaining",
        money(remaining)
    )

    st.divider()

    # --------------------------------------------------------
    # Financial insights
    # --------------------------------------------------------

    st.subheader(
        "📊 Financial Insights"
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Highest Category",
        insights.get(
            "highest_category",
            "None"
        )
    )

    c2.metric(
        "Amount Spent",
        money(
            insights.get(
                "highest_category_amount",
                0
            )
        )
    )

    c3.metric(
        "Unusual Transactions",
        str(
            insights.get(
                "unusual_transactions",
                0
            )
        )
    )

    c4.metric(
        "High-Spending Transactions",
        str(
            insights.get(
                "high_spending_transactions",
                0
            )
        )
    )

    c5.metric(
        "Category Share",
        f"{safe_float(insights.get('highest_category_percentage', 0)):.1f}%"
    )

    st.info(
        "📅 Highest spending day: "
        f"**{insights.get('highest_spending_day', 'None')}**"
    )

    # --------------------------------------------------------
    # Smart anomaly detection results
    # --------------------------------------------------------

    anomaly_df = st.session_state.get(
        "anomaly_df",
        None
    )

    st.subheader("🚨 Unusual Spending Detection")

    anomaly_count = int(
        safe_float(
            insights.get(
                "unusual_transactions",
                0
            )
        )
    )

    if anomaly_count > 0 and anomaly_df is not None and not anomaly_df.empty:

        st.warning(
            f"FinSight-AI detected **{anomaly_count} unusual transaction"
            f"{'s' if anomaly_count != 1 else ''}** using "
            f"{insights.get('anomaly_method', 'IQR + z-score')} analysis."
        )

        anomaly_display = anomaly_df.copy()

        if "date" in anomaly_display.columns:
            anomaly_display["date"] = (
                pd.to_datetime(
                    anomaly_display["date"],
                    errors="coerce"
                )
                .dt.strftime("%Y-%m-%d")
            )

        if "amount" in anomaly_display.columns:
            anomaly_display["amount"] = (
                anomaly_display["amount"].map(money)
            )

        columns = [
            column
            for column in [
                "date",
                "description",
                "amount",
                "category",
                "z_score",
                "reason",
            ]
            if column in anomaly_display.columns
        ]

        st.dataframe(
            anomaly_display[columns],
            hide_index=True,
            width="stretch"
        )

    else:

        st.success(
            "No statistically unusual transactions were detected "
            "in this dataset."
        )

    # --------------------------------------------------------
    # Spending summary
    # --------------------------------------------------------

    st.subheader(
        "📈 Spending Summary"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        " Total Spending",
        money(
            insights.get(
                "total_spending",
                0
            )
        )
    )

    c2.metric(
        "🧾 Average Transaction",
        money(
            insights.get(
                "average_transaction",
                0
            )
        )
    )

    c3.metric(
        "🏆 Highest Category",
        insights.get(
            "highest_category",
            "None"
        )
    )

    c4.metric(
        "📊 Category Share",
        f"{safe_float(insights.get('highest_category_percentage', 0)):.1f}%"
    )

    st.divider()

    # --------------------------------------------------------
    # Category breakdown
    # --------------------------------------------------------

    st.subheader(
        "📊 Category Breakdown"
    )

    category_data = insights.get(
        "category_spending",
        {}
    )

    if category_data:

        category_df = pd.DataFrame({

            "Category":
                list(category_data.keys()),

            "Amount":
                list(category_data.values())

        })

        category_chart_data = {
            str(row["Category"]): float(row["Amount"])
            for _, row in category_df.iterrows()
        }

        render_financial_bar_chart(
            category_chart_data,
            value_label="Spending"
        )

        with st.expander(
            "📋 View Category Spending"
        ):

            display_category = (
                category_df.copy()
            )

            display_category["Amount"] = (
                display_category["Amount"]
                .map(money)
            )

            st.dataframe(
                display_category,
                hide_index=True,
                width="stretch"
            )

    # --------------------------------------------------------
    # Spending pattern intelligence
    # --------------------------------------------------------

    st.subheader(
        "🧠 Spending Pattern Intelligence"
    )

    pattern = insights.get(
        "spending_pattern",
        {}
    )

    pc1, pc2, pc3, pc4 = st.columns(4)

    pc1.metric(
        "Top Category",
        pattern.get("top_category", "None")
    )

    pc2.metric(
        "Top Category Share",
        f"{safe_float(pattern.get('top_category_share', 0)):.1f}%"
    )

    pc3.metric(
        "Top 3 Category Share",
        f"{safe_float(pattern.get('top_3_share', 0)):.1f}%"
    )

    pc4.metric(
        "Largest Transaction",
        money(pattern.get("largest_transaction", 0))
    )

    st.info(
        f"**Spending pattern: {pattern.get('pattern_level', 'Balanced')}** · "
        f"{pattern.get('pattern_message', '')}"
    )

    p1, p2 = st.columns(2)

    with p1:
        st.markdown("#### 📌 Key spending signals")
        st.write(
            f"**Highest-spending day:** {pattern.get('most_active_day', 'None')} "
            f"({money(pattern.get('most_active_day_amount', 0))})"
        )
        st.write(
            f"**Largest transaction:** {money(pattern.get('largest_transaction', 0))}"
        )
        if pattern.get("largest_transaction_description"):
            st.write(
                f"**Largest transaction:** {pattern.get('largest_transaction_description')}"
            )

    with p2:
        st.markdown("#### 💡 FinSight-AI observation")
        st.write(
            pattern.get(
                "recommendation",
                "Continue monitoring your spending patterns."
            )
        )

    category_percentages = insights.get(
        "category_percentages",
        {}
    )

    if category_percentages:
        pattern_df = pd.DataFrame({
            "Category": list(category_percentages.keys()),
            "Share": list(category_percentages.values())
        })
        pattern_df = pattern_df.sort_values(
            "Share",
            ascending=False
        )

        with st.expander("📊 View category spending shares"):
            display_pattern = pattern_df.copy()
            display_pattern["Share"] = display_pattern["Share"].map(
                lambda x: f"{safe_float(x):.1f}%"
            )
            st.dataframe(
                display_pattern,
                hide_index=True,
                width="stretch"
            )

    # --------------------------------------------------------
    # Monthly spending
    # --------------------------------------------------------

    st.subheader(
        "📅 Monthly Spending"
    )

    monthly_data = insights.get(
        "monthly_spending",
        {}
    )

    if monthly_data:

        monthly_df = pd.DataFrame({

            "Month":
                list(monthly_data.keys()),

            "Spending":
                list(monthly_data.values())

        })

        monthly_df["Month"] = (
            pd.to_datetime(
                monthly_df["Month"],
                errors="coerce"
            )
        )

        monthly_df = monthly_df.dropna(
            subset=["Month"]
        )

        monthly_df = (
            monthly_df
            .sort_values("Month")
        )

        monthly_df["Month"] = (
            monthly_df["Month"]
            .dt.strftime("%Y-%m")
        )

        monthly_chart_data = {
            str(row["Month"]): float(row["Spending"])
            for _, row in monthly_df.iterrows()
        }

        render_financial_bar_chart(
            monthly_chart_data,
            value_label="Monthly spending"
        )

    # --------------------------------------------------------
    # Transactions
    # --------------------------------------------------------

    st.subheader(
        "📋 Transactions"
    )

    display_df = df.copy()

    if "date" in display_df.columns:

        display_df["date"] = (
            pd.to_datetime(
                display_df["date"],
                errors="coerce"
            )
            .dt.strftime(
                "%Y-%m-%d"
            )
        )

    if "amount" in display_df.columns:

        display_df["amount"] = (
            display_df["amount"]
            .map(money)
        )

    st.dataframe(
        display_df,
        hide_index=True,
        width="stretch"
    )

    # --------------------------------------------------------
    # Top transactions
    # --------------------------------------------------------

    st.subheader(
        "🏆 Top Transactions"
    )

    top_df = (
        df.copy()
        .sort_values(
            "amount",
            ascending=False
        )
        .head(5)
    )

    top_display = top_df.copy()

    if "date" in top_display.columns:

        top_display["date"] = (
            pd.to_datetime(
                top_display["date"],
                errors="coerce"
            )
            .dt.strftime(
                "%Y-%m-%d"
            )
        )

    top_display["amount"] = (
        top_display["amount"]
        .map(money)
    )

    st.dataframe(
        top_display,
        hide_index=True,
        width="stretch"
    )

    st.divider()

    # ========================================================
    # SAVE TRANSACTIONS
    # ========================================================

    st.subheader(
        "💾 Save Transactions"
    )

    if st.button(
        "💾 Save Analyzed Transactions",
        width="stretch"
    ):

        saved_count = 0

        try:

            for _, row in df.iterrows():

                transaction_date = (
                    pd.to_datetime(
                        row["date"],
                        errors="coerce"
                    )
                )

                if pd.isna(
                    transaction_date
                ):

                    continue

                description = str(
                    row.get(
                        "description",
                        ""
                    )
                )

                amount = safe_float(
                    row.get(
                        "amount",
                        0
                    )
                )

                category = str(
                    row.get(
                        "category",
                        "Other"
                    )
                )

                add_transaction(

                    st.session_state.user_id,

                    transaction_date.strftime(
                        "%Y-%m-%d"
                    ),

                    description,

                    amount,

                    category,

                    "expense",

                    "csv"

                )

                saved_count += 1

            st.success(
                f"Saved {saved_count} transactions."
            )

        except Exception as e:

            st.error(
                f"Could not save transactions: {e}"
            )

    # ========================================================
    # SAVED TRANSACTIONS
    # ========================================================

    st.subheader(
        "📋 Saved Transactions"
    )

    try:

        saved = get_transactions(
            st.session_state.user_id
        )

    except Exception:

        saved = []

    if saved:

        saved_df = pd.DataFrame(

            saved,

            columns=[

                "ID",

                "Date",

                "Description",

                "Amount",

                "Category",

                "Type",

                "Source",

            ]

        )

        saved_df["Amount"] = (
            saved_df["Amount"]
            .map(money)
        )

        st.dataframe(
            saved_df,
            hide_index=True,
            width="stretch"
        )

        # ----------------------------------------------------
        # Delete transaction
        # ----------------------------------------------------

        st.subheader(
            "🗑️ Delete Transaction"
        )

        transaction_options = {

            f"{row[0]} | {row[2]} | {money(row[3])}":
                row[0]

            for row in saved

        }

        selected = st.selectbox(
            "Select transaction to delete",
            list(
                transaction_options.keys()
            )
        )

        if st.button(
            "🗑️ Delete Selected Transaction",
            width="stretch"
        ):

            transaction_id = (
                transaction_options[
                    selected
                ]
            )

            try:

                deleted = delete_transaction(

                    st.session_state.user_id,

                    transaction_id

                )

                if deleted:

                    st.success(
                        "Transaction deleted."
                    )

                    st.rerun()

                else:

                    st.error(
                        "Transaction could not be deleted."
                    )

            except Exception as e:

                st.error(
                    f"Delete error: {e}"
                )

    else:

        st.info(
            "No saved transactions yet."
        )

    # ========================================================
    # AI FINANCIAL ADVICE
    # ========================================================

    st.divider()

    st.subheader(
        "🤖 AI Financial Advice"
    )

    st.caption(
        f"Local {OLLAMA_MODEL} analyzes your verified "
        "transaction statistics and provides concise suggestions."
    )

    # --------------------------------------------------------
    # AI module status
    # --------------------------------------------------------

    if not AI_MODULE_READY:

        st.warning(
            "AI advice module could not be loaded. "
            "The application will use local deterministic "
            "financial advice instead."
        )

        if AI_MODULE_ERROR:

            with st.expander(
                "View AI module error"
            ):

                st.code(
                    AI_MODULE_ERROR
                )

    if st.button(
        "🤖 Generate AI Financial Advice",
        width="stretch"
    ):

        with st.spinner(
            "Qwen3 is analyzing your verified spending data..."
        ):

            advice = get_ai_financial_advice(
                insights
            )

            st.session_state.ai_advice = advice

    advice = st.session_state.ai_advice

    if advice:

        # ----------------------------------------------------
        # Failed response
        # ----------------------------------------------------

        if not advice.get(
            "success",
            False
        ):

            st.error(
                advice.get(
                    "error",
                    "AI advice generation failed."
                )
            )

        else:

            source = advice.get(
                "source",
                "Local analysis"
            )

            st.caption(
                f"Generated using: **{source}**"
            )

            # ------------------------------------------------
            # Spending Summary
            # ------------------------------------------------

            st.markdown(
                "###  Spending Summary"
            )

            summary = clean_text(
                advice.get(
                    "summary",
                    ""
                )
            )

            if summary:

                st.write(
                    summary
                )

            else:

                st.info(
                    "No AI summary was returned."
                )

            # ------------------------------------------------
            # Main Concern
            # ------------------------------------------------

            st.markdown(
                "### ⚠️ Main Concern"
            )

            concern = clean_text(
                advice.get(
                    "concern",
                    ""
                )
            )

            if concern:

                st.write(
                    concern
                )

            else:

                st.info(
                    "No specific concern was identified."
                )

            # ------------------------------------------------
            # Suggestions
            # ------------------------------------------------

            st.markdown(
                "### 💡 Two Practical Suggestions"
            )

            suggestion_1 = clean_text(
                advice.get(
                    "suggestion_1",
                    ""
                )
            )

            suggestion_2 = clean_text(
                advice.get(
                    "suggestion_2",
                    ""
                )
            )

            if suggestion_1:

                st.write(
                    "1. "
                    + suggestion_1
                )

            if suggestion_2:

                st.write(
                    "2. "
                    + suggestion_2
                )


# ============================================================
# BUDGET PLANNER
# ============================================================

def budget_planner_page():

    st.title("📊 Budget Planner")

    st.caption(
        "Set monthly spending limits and compare them with your actual transaction spending."
    )

    df = st.session_state.analysis_df

    if df is None or df.empty:

        st.info(
            "Analyze a transaction CSV first. Your actual category spending will appear here automatically."
        )
        return

    data = df.copy()

    if "amount" not in data.columns:
        st.error("The analyzed transaction data does not contain an amount column.")
        return

    data["amount"] = pd.to_numeric(data["amount"], errors="coerce")
    data = data.dropna(subset=["amount"])
    data = data[data["amount"] > 0].copy()

    if data.empty:
        st.info("No positive spending transactions are available for budgeting.")
        return

    if "category" not in data.columns:
        data["category"] = "Other"

    data["category"] = (
        data["category"]
        .fillna("Other")
        .astype(str)
        .str.strip()
    )
    data.loc[data["category"] == "", "category"] = "Other"

    actual_spending = (
        data.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    # Keep the full financial category list visible, while also including
    # any category that may have come from the uploaded file.
    categories = list(FINANCIAL_CATEGORIES)
    for category in actual_spending:
        if category not in categories:
            categories.append(category)

    if not st.session_state.budget_limits:
        st.session_state.budget_limits = {category: 0.0 for category in categories}
    else:
        for category in categories:
            st.session_state.budget_limits.setdefault(category, 0.0)

    st.subheader("Set your monthly limits")
    st.caption(
        "Enter ₹0 for categories you do not want to budget. Your limits are kept for this session."
    )

    budget_values = {}
    left, right = st.columns(2)

    for index, category in enumerate(categories):
        target = left if index % 2 == 0 else right
        with target:
            budget_values[category] = st.number_input(
                f"{category} budget (₹)",
                min_value=0.0,
                value=float(st.session_state.budget_limits.get(category, 0.0)),
                step=500.0,
                key=f"budget_input_{re.sub(r'[^a-zA-Z0-9]+', '_', category)}"
            )

    if st.button(
        "💾 Save Monthly Budget",
        width="stretch",
        key="save_monthly_budget"
    ):
        st.session_state.budget_limits = budget_values.copy()
        st.success("Monthly budget saved successfully.")

    st.divider()
    st.subheader("Budget performance")

    rows = []
    total_budget = 0.0
    total_actual = float(sum(actual_spending.values()))

    for category in categories:
        budget = float(st.session_state.budget_limits.get(category, budget_values.get(category, 0.0)))
        actual = float(actual_spending.get(category, 0.0))

        # Categories with no budget are shown separately as unplanned spending.
        if budget > 0:
            remaining = budget - actual
            utilization = (actual / budget) * 100.0
            if actual > budget:
                status = "Over budget"
            elif utilization >= 80:
                status = "Near limit"
            else:
                status = "Within budget"

            total_budget += budget
            rows.append({
                "category": category,
                "budget": budget,
                "actual": actual,
                "remaining": remaining,
                "utilization": utilization,
                "status": status,
            })
        elif actual > 0:
            rows.append({
                "category": category,
                "budget": 0.0,
                "actual": actual,
                "remaining": -actual,
                "utilization": 0.0,
                "status": "No budget set",
            })

    if not rows:
        st.info("Set at least one monthly category limit to see your budget performance.")
        return

    total_remaining = total_budget - total_actual
    total_utilization = (total_actual / total_budget * 100.0) if total_budget > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Monthly Budget", money(total_budget))

    with c2:
        st.metric("Actual Spending", money(total_actual))

    with c3:
        st.metric(
            "Budget Remaining",
            money(total_remaining),
            delta=f"{total_utilization:.1f}% used" if total_budget > 0 else None,
            delta_color="inverse" if total_remaining < 0 else "normal",
        )

    with c4:
        over_count = sum(1 for row in rows if row["status"] == "Over budget")
        st.metric("Categories Over Budget", over_count)

    st.markdown("### Category limits")

    for row in sorted(rows, key=lambda item: item["actual"], reverse=True):
        category = row["category"]
        budget = row["budget"]
        actual = row["actual"]
        status = row["status"]

        st.markdown(
            f"**{escape(category)}** &nbsp; · &nbsp; "
            f"Spent {money(actual)}"
            + (f" of {money(budget)}" if budget > 0 else " · no limit set")
        , unsafe_allow_html=True)

        if budget > 0:
            progress = min(actual / budget, 1.0)
            st.progress(progress)
            if status == "Over budget":
                st.error(
                    f"{category}: over budget by {money(actual - budget)}."
                )
            elif status == "Near limit":
                st.warning(
                    f"{category}: {money(budget - actual)} remaining. You have used {actual / budget * 100:.1f}% of the limit."
                )
            else:
                st.success(
                    f"{category}: {money(budget - actual)} remaining. Within budget."
                )
        else:
            st.warning(
                f"{category}: {money(actual)} spent without a monthly limit."
            )

    st.divider()
    st.subheader("FinSight-AI budget insight")

    over_budget = [row for row in rows if row["status"] == "Over budget"]
    near_limit = [row for row in rows if row["status"] == "Near limit"]
    unplanned = [row for row in rows if row["status"] == "No budget set"]

    if total_budget <= 0:
        st.info("Set your monthly limits to unlock budget-based financial guidance.")
    elif over_budget:
        biggest = max(over_budget, key=lambda row: row["actual"] - row["budget"])
        st.error(
            f"Your spending is above budget in {len(over_budget)} "
            f"{'categories' if len(over_budget) != 1 else 'category'}. "
            f"The largest overrun is {biggest['category']} by {money(biggest['actual'] - biggest['budget'])}."
        )
    elif near_limit:
        biggest = max(near_limit, key=lambda row: row["actual"] / row["budget"])
        st.warning(
            f"Your budget is currently under control, but {biggest['category']} is close to its limit "
            f"at {biggest['actual'] / biggest['budget'] * 100:.1f}% used."
        )
    else:
        st.success(
            "Your analyzed spending is currently within the category limits you set."
        )

    if unplanned:
        names = ", ".join(row["category"] for row in unplanned if row["actual"] > 0)
        if names:
            st.caption(
                f"Unplanned spending detected in: {names}. Consider adding limits for these categories if they are recurring expenses."
            )


# ============================================================
# SAVINGS PLANNER
# ============================================================

def savings_planner_page():

    st.title("🏦 Savings Planner")

    st.caption(
        "Build a realistic savings plan using your income, actual spending, budget, and savings goal."
    )

    profile = get_financial_profile(st.session_state.user_id)

    if profile:
        monthly_income = safe_float(profile[0])
        current_savings = safe_float(profile[1])
        family_support = safe_float(profile[2])
        saved_monthly_goal = safe_float(profile[3])
    else:
        monthly_income = 0.0
        current_savings = 0.0
        family_support = 0.0
        saved_monthly_goal = 0.0

    # Use the analyzed transaction data as the actual spending source.
    total_expenses = 0.0
    category_spending = {}
    df = st.session_state.analysis_df

    if df is not None and not df.empty and "amount" in df.columns:
        data = df.copy()
        data["amount"] = pd.to_numeric(data["amount"], errors="coerce")
        data = data.dropna(subset=["amount"])
        data = data[data["amount"] > 0].copy()
        total_expenses = float(data["amount"].sum())

        if "category" in data.columns:
            data["category"] = (
                data["category"].fillna("Other").astype(str).str.strip()
            )
            data.loc[data["category"] == "", "category"] = "Other"
            category_spending = data.groupby("category")["amount"].sum().to_dict()

    if total_expenses <= 0:
        st.info(
            "Analyze a transaction CSV first so FinSight-AI can calculate your realistic savings capacity."
        )
        return

    # Current cash-flow position.
    family_adjusted_income = max(monthly_income - family_support, 0.0)
    free_cash_flow = family_adjusted_income - total_expenses

    st.subheader("Your current savings picture")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Monthly Income", money(monthly_income))

    with c2:
        st.metric("Actual Expenses", money(total_expenses))

    with c3:
        st.metric("Current Savings", money(current_savings))

    with c4:
        st.metric(
            "Potential Monthly Savings",
            money(max(free_cash_flow, 0.0)),
        )

    if monthly_income <= 0:
        st.warning(
            "Your monthly income is currently set to ₹0. Add your income on the Dashboard for a meaningful savings calculation."
        )

    if free_cash_flow <= 0:
        st.error(
            "Your current income is not covering your analyzed expenses and family support. A positive savings plan is not currently feasible without reducing expenses or increasing income."
        )
    else:
        savings_rate = (free_cash_flow / monthly_income * 100.0) if monthly_income > 0 else 0.0
        st.success(
            f"Your current estimated savings capacity is {money(free_cash_flow)} per month, about {savings_rate:.1f}% of monthly income."
        )

    st.divider()
    st.subheader("Set your savings target")

    c1, c2 = st.columns(2)

    with c1:
        target_amount = st.number_input(
            "Savings target (₹)",
            min_value=0.0,
            value=max(saved_monthly_goal, 0.0),
            step=1000.0,
            key="savings_target_amount",
        )

        target_months = st.number_input(
            "Target time (months)",
            min_value=1,
            value=6,
            step=1,
            key="savings_target_months",
        )

    with c2:
        desired_monthly_saving = st.number_input(
            "Desired monthly saving (₹)",
            min_value=0.0,
            value=max(saved_monthly_goal, 0.0),
            step=500.0,
            key="desired_monthly_saving",
        )

        emergency_months = st.number_input(
            "Emergency fund target (months of expenses)",
            min_value=1,
            max_value=12,
            value=3,
            step=1,
            key="emergency_months",
        )

    # Keep the current Savings Planner inputs available to the AI Financial Agent.
    st.session_state.savings_plan = {
        "target_amount": float(target_amount),
        "target_months": float(target_months),
        "current_savings": float(current_savings),
        "desired_monthly_saving": float(desired_monthly_saving),
        "emergency_months": float(emergency_months),
    }

    # Savings calculations.
    feasible_monthly = max(free_cash_flow, 0.0)
    required_monthly = (max(target_amount - current_savings, 0.0) / target_months) if target_months > 0 else 0.0
    target_gap = max(target_amount - current_savings, 0.0)

    if desired_monthly_saving > 0:
        desired_months = (
            target_gap / desired_monthly_saving
            if target_gap > 0
            else 0.0
        )
    else:
        desired_months = None

    if feasible_monthly > 0 and target_gap > 0:
        feasible_months = target_gap / feasible_monthly
    else:
        feasible_months = 0.0

    essential_categories = {
    "Food",
    "Medical/Hospital",
    "Education/Tuition",
    "Transport",
    "Utilities",
    "Rent/Home",
    "Family",
    }

    essential_expenses = float(
        sum(
            amount
            for category, amount in category_spending.items()
            if category in essential_categories
            )
    )

    emergency_baseline = (
        essential_expenses
        if essential_expenses > 0
        else total_expenses
    )

    emergency_target = emergency_baseline * emergency_months
    emergency_gap = max(emergency_target - current_savings, 0.0)

    st.divider()
    st.subheader("Savings feasibility")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Target Amount", money(target_amount))

    with c2:
        st.metric("Required / Month", money(required_monthly))

    with c3:
        st.metric("Feasible / Month", money(feasible_monthly))

    with c4:
        if target_gap <= 0:
            st.metric("Target Status", "Achieved")
        elif feasible_monthly >= required_monthly:
            st.metric("Target Status", "Feasible")
        else:
            st.metric("Target Status", "Needs adjustment")

    if target_gap <= 0:
        st.success("You have already reached this savings target.")
    elif feasible_monthly >= required_monthly and required_monthly > 0:
        st.success(
            f"This target is currently feasible. Saving about {money(required_monthly)} per month can reach it in {target_months} months."
        )
    elif required_monthly > 0:
        shortfall = required_monthly - feasible_monthly
        st.warning(
            f"This target needs {money(required_monthly)} per month, but your current estimated capacity is {money(feasible_monthly)}. You are short by {money(shortfall)} per month."
        )

    st.markdown("### Emergency fund")

    if emergency_target > 0:
        emergency_progress = min(current_savings / emergency_target, 1.0)
        st.progress(emergency_progress)

    e1, e2, e3 = st.columns(3)

    with e1:
        st.metric("Emergency Target", money(emergency_target))

    with e2:
        st.metric("Current Savings", money(current_savings))

    with e3:
        st.metric("Emergency Fund Gap", money(emergency_gap))

    st.divider()
    st.subheader("FinSight-AI savings recommendation")

    if free_cash_flow <= 0:
        st.error(
            "Priority: stabilize your monthly cash flow before setting an aggressive savings target. Review your largest spending categories and reduce non-essential expenses first."
        )
    elif target_gap <= 0:
        st.success(
            "Your selected savings target has already been reached. Consider redirecting future savings toward an emergency fund or another financial goal."
        )
    elif feasible_monthly >= required_monthly:
        st.success(
            f"Your target looks achievable. A monthly saving of {money(required_monthly)} meets the {target_months}-month target while staying within your current estimated savings capacity."
        )
    else:
        st.warning(
            f"Your target is currently ambitious. You would need an additional {money(required_monthly - feasible_monthly)} per month. Start with a lower target or reduce spending in your highest categories."
        )

    if desired_monthly_saving > 0 and target_gap > 0:
        if desired_monthly_saving <= feasible_monthly:
            st.info(
                f"At {money(desired_monthly_saving)} per month, you could reach the target in approximately {desired_months:.1f} months."
            )
        else:
            st.info(
                f"Your desired saving of {money(desired_monthly_saving)} is above your current estimated capacity by {money(desired_monthly_saving - feasible_monthly)} per month."
            )

    if category_spending:
        highest = max(category_spending.items(), key=lambda item: item[1])
        st.caption(
            f"Savings opportunity: {highest[0]} is currently your largest spending category at {money(highest[1])}."
        )

# ============================================================
# EMERGENCY FUND PLANNER
# ============================================================

def emergency_fund_page():
    st.title("Emergency Fund")
    st.caption(
        "Build a financial safety buffer based on your spending, current savings, and monthly savings capacity."
    )

    profile = get_financial_profile(st.session_state.user_id)

    if profile:
        monthly_income = safe_float(profile[0])
        current_savings = safe_float(profile[1])
        family_support = safe_float(profile[2])
    else:
        monthly_income = 0.0
        current_savings = 0.0
        family_support = 0.0

    df = st.session_state.analysis_df

    if df is None or df.empty or "amount" not in df.columns:
        st.info(
            "Analyze a transaction CSV first. FinSight-AI needs your spending data to estimate your emergency fund target."
        )
        return

    data = df.copy()
    data["amount"] = pd.to_numeric(data["amount"], errors="coerce")
    data = data.dropna(subset=["amount"])
    data = data[data["amount"] > 0].copy()

    if data.empty:
        st.info("No valid spending transactions were found for the emergency fund calculation.")
        return

    total_expenses = float(data["amount"].sum())

    if "category" in data.columns:
        data["category"] = (
            data["category"].fillna("Other").astype(str).str.strip()
        )
        data.loc[data["category"] == "", "category"] = "Other"
        category_spending = data.groupby("category")["amount"].sum().to_dict()
    else:
        category_spending = {}

    # Use clearly essential categories when the uploaded data has category information.
    # If no essential-category spending is detected, use total analyzed spending as the
    # conservative monthly expense baseline.
    essential_categories = {
        "Food",
        "Medical/Hospital",
        "Education/Tuition",
        "Transport",
        "Utilities",
        "Rent/Home",
        "Family",
    }

    essential_expenses = float(
        sum(
            amount
            for category, amount in category_spending.items()
            if category in essential_categories
        )
    )

    baseline_expenses = essential_expenses if essential_expenses > 0 else total_expenses
    baseline_label = (
        "Estimated essential monthly expenses"
        if essential_expenses > 0
        else "Analyzed monthly expenses"
    )

    adjusted_income = max(monthly_income - family_support, 0.0)
    monthly_cash_flow = adjusted_income - total_expenses
    monthly_capacity = max(monthly_cash_flow, 0.0)

    st.subheader("Your emergency fund picture")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Current Savings", money(current_savings))

    with c2:
        st.metric("Expense Baseline", money(baseline_expenses))

    with c3:
        st.metric("Monthly Savings Capacity", money(monthly_capacity))

    with c4:
        coverage_now = (
            current_savings / baseline_expenses
            if baseline_expenses > 0
            else 0.0
        )
        st.metric("Current Coverage", f"{coverage_now:.1f} months")

    if monthly_income <= 0:
        st.warning(
            "Your monthly income is currently ₹0. Add your income on the Dashboard for a more useful emergency fund plan."
        )

    st.divider()
    st.subheader("Choose your safety target")

    target_months = st.radio(
        "Emergency fund size",
        [3, 6],
        index=0,
        horizontal=True,
        format_func=lambda value: f"{value} months",
        key="emergency_target_months",
    )

    st.caption(
        "3 months is a practical starting target. 6 months provides a larger safety buffer."
    )

    target_amount = baseline_expenses * float(target_months)
    target_gap = max(target_amount - current_savings, 0.0)

    default_contribution = (
        min(monthly_capacity, target_gap)
        if monthly_capacity > 0
        else 0.0
    )

    contribution = st.number_input(
        "Monthly emergency-fund contribution (₹)",
        min_value=0.0,
        value=float(round(default_contribution, 2)),
        step=500.0,
        key="emergency_monthly_contribution",
    )

    contribution = max(float(contribution), 0.0)

    if target_gap <= 0:
        estimated_months = 0.0
    elif contribution > 0:
        estimated_months = target_gap / contribution
    else:
        estimated_months = None

    progress = (
        min(current_savings / target_amount, 1.0)
        if target_amount > 0
        else 0.0
    )

    st.divider()
    st.subheader("Emergency fund status")

    st.progress(progress)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Target", money(target_amount))

    with c2:
        st.metric("Current Savings", money(current_savings))

    with c3:
        st.metric("Remaining Gap", money(target_gap))

    with c4:
        if target_gap <= 0:
            status = "Fully funded"
        elif contribution <= 0:
            status = "No contribution"
        elif monthly_capacity > 0 and contribution > monthly_capacity:
            status = "Above capacity"
        else:
            status = "In progress"

        st.metric("Status", status)

    if target_gap <= 0:
        st.success(
            f"Your current savings already cover the selected {target_months}-month emergency fund target."
        )
    elif contribution <= 0:
        st.warning(
            "Set a monthly contribution above ₹0 to estimate how long it will take to reach your target."
        )
    elif monthly_capacity <= 0:
        st.error(
            "Your current analyzed expenses and family support leave no positive monthly savings capacity. Stabilize cash flow before committing to an emergency-fund contribution."
        )
    elif contribution > monthly_capacity:
        st.warning(
            f"Your planned contribution of {money(contribution)} is above your estimated monthly savings capacity of {money(monthly_capacity)}."
        )
    else:
        st.success(
            f"At {money(contribution)} per month, you could reach the target in approximately {estimated_months:.1f} months."
        )

    st.divider()
    st.subheader("FinSight-AI emergency fund recommendation")

    if target_gap <= 0:
        recommendation = (
            "Your emergency fund target is covered. Keep this money accessible for genuine emergencies "
            "and direct future surplus toward other financial goals."
        )
        st.success(recommendation)
    elif monthly_capacity <= 0:
        recommendation = (
            "Your first priority should be improving monthly cash flow. Review your largest spending "
            "categories and avoid setting an emergency contribution that your current cash flow cannot support."
        )
        st.error(recommendation)
    elif contribution > monthly_capacity:
        recommended = monthly_capacity
        recommendation = (
            f"Reduce the planned contribution to around {money(recommended)} or lower. "
            f"That keeps the emergency-fund plan within your current estimated savings capacity."
        )
        st.warning(recommendation)
    else:
        if target_months == 3:
            recommendation = (
                "Start with the 3-month emergency fund target. Automate the contribution if possible, "
                "then increase the target toward 6 months after the first buffer is built."
            )
        else:
            recommendation = (
                "The 6-month target gives you a stronger safety buffer. Keep the monthly contribution "
                "realistic so the emergency fund does not force you to miss essential expenses."
            )
        st.info(recommendation)

    st.markdown("### What FinSight-AI used")

    u1, u2, u3 = st.columns(3)

    with u1:
        st.metric("Total Analyzed Spending", money(total_expenses))

    with u2:
        st.metric("Essential Expense Baseline", money(baseline_expenses))

    with u3:
        st.metric("Family Support", money(family_support))

    if essential_expenses > 0:
        st.caption(
            f"The target uses {baseline_label.lower()} of {money(essential_expenses)} based on essential categories detected in your analyzed transactions."
        )
    else:
        st.caption(
            "No clearly essential-category spending was detected, so the planner uses your total analyzed spending as the expense baseline."
        )

    if category_spending:
        highest = max(category_spending.items(), key=lambda item: item[1])
        st.caption(
            f"Spending review opportunity: {highest[0]} is your largest analyzed category at {money(highest[1])}."
        )

    st.caption(
        "Emergency-fund estimates are planning estimates, not financial advice. Keep the fund accessible and adjust the target when your essential expenses change."
    )


# ============================================================
# FINANCIAL HEALTH
# ============================================================

def financial_health_page():

    st.title("🩺 Financial Health")

    st.caption(
        "Understand your overall financial health using cash flow, spending control, savings capacity, and emergency readiness."
    )

    profile = get_financial_profile(st.session_state.user_id)

    if profile:
        monthly_income = safe_float(profile[0])
        current_savings = safe_float(profile[1])
        family_support = safe_float(profile[2])
    else:
        monthly_income = 0.0
        current_savings = 0.0
        family_support = 0.0

    # Read the same analyzed transaction data used by Budget Planner and Savings Planner.
    df = st.session_state.analysis_df

    if df is None or df.empty or "amount" not in df.columns:
        st.info(
            "Analyze a transaction CSV first. FinSight-AI needs your actual spending data to calculate the health score."
        )
        return

    data = df.copy()
    data["amount"] = pd.to_numeric(data["amount"], errors="coerce")
    data = data.dropna(subset=["amount"])
    data = data[data["amount"] > 0].copy()

    if data.empty:
        st.info("No valid spending transactions were found for the health calculation.")
        return

    total_expenses = float(data["amount"].sum())

    # Category spending.
    category_spending = {}
    if "category" in data.columns:
        data["category"] = (
            data["category"].fillna("Other").astype(str).str.strip()
        )
        data.loc[data["category"] == "", "category"] = "Other"
        category_spending = data.groupby("category")["amount"].sum().to_dict()

    # Core financial measures.
    adjusted_income = max(monthly_income - family_support, 0.0)
    monthly_cash_flow = adjusted_income - total_expenses
    savings_capacity = max(monthly_cash_flow, 0.0)

    # Budget health uses the same session budget as Budget Planner.
    budget_limits = st.session_state.get("budget_limits", {})
    total_budget = float(
        sum(
            safe_float(value)
            for value in budget_limits.values()
            if safe_float(value) > 0
        )
    )

    budget_used_pct = (
        (total_expenses / total_budget) * 100.0
        if total_budget > 0
        else None
    )

    over_budget_categories = 0
    if category_spending and total_budget > 0:
        for category, actual in category_spending.items():
            limit = safe_float(budget_limits.get(category, 0.0))
            if limit > 0 and actual > limit:
                over_budget_categories += 1

    # Emergency fund target: 3 months of essential expenses.
    # Keep this consistent with the Emergency Fund planner.
    essential_categories = {
        "Food",
        "Medical/Hospital",
        "Education/Tuition",
        "Transport",
        "Utilities",
        "Rent/Home",
        "Family",
    }

    essential_expenses = float(
        sum(
            amount
            for category, amount in category_spending.items()
            if category in essential_categories
        )
    )

    emergency_baseline = (
        essential_expenses
        if essential_expenses > 0
        else total_expenses
    )

    emergency_target = emergency_baseline * 3.0

    emergency_coverage = (
        min(current_savings / emergency_target, 1.0)
        if emergency_target > 0
        else 0.0
    )

    # --------------------------------------------------------
    # Score calculation
    # --------------------------------------------------------
    # 30 points: cash-flow health
    if monthly_income <= 0:
        cash_flow_score = 0.0
    elif monthly_cash_flow <= 0:
        cash_flow_score = 5.0
    else:
        savings_rate = monthly_cash_flow / monthly_income
        cash_flow_score = min(30.0, 15.0 + (max(savings_rate, 0.0) * 21.0))

    # 25 points: spending/budget control
    if total_budget > 0:
        if budget_used_pct <= 80:
            budget_score = 25.0
        elif budget_used_pct <= 100:
            budget_score = 20.0
        elif budget_used_pct <= 110:
            budget_score = 12.0
        else:
            budget_score = 5.0

        budget_score -= min(over_budget_categories * 2.0, 8.0)
        budget_score = max(0.0, budget_score)
    else:
        # No budget should not completely destroy the score, but it should
        # reduce the spending-control component.
        budget_score = 10.0

    # 20 points: savings capacity
    if monthly_income <= 0:
        savings_score = 0.0
    else:
        savings_rate = savings_capacity / monthly_income
        savings_score = min(20.0, max(0.0, savings_rate * 25.0))

    # 25 points: emergency readiness
    emergency_score = emergency_coverage * 25.0

    total_score = int(round(
        min(
            100.0,
            max(
                0.0,
                cash_flow_score
                + budget_score
                + savings_score
                + emergency_score,
            ),
        )
    ))

    if total_score >= 80:
        health_label = "Strong"
    elif total_score >= 65:
        health_label = "Healthy"
    elif total_score >= 50:
        health_label = "Needs attention"
    else:
        health_label = "Needs improvement"

    st.subheader("Your financial health score")

    score_col, status_col = st.columns([1, 2])

    with score_col:
        st.metric("Health Score", f"{total_score}/100")

    with status_col:
        st.markdown(f"### {health_label}")
        st.caption(
            "This score is an educational snapshot based on the financial information and transaction data currently available in FinSight-AI."
        )

    st.progress(total_score / 100.0)

    st.divider()
    st.subheader("Health breakdown")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Cash Flow",
            "Strong" if monthly_cash_flow > 0 else "At risk",
        )
        st.caption(f"Monthly cash flow: {money(monthly_cash_flow)}")

    with c2:
        if total_budget > 0:
            budget_status = "On track" if budget_used_pct <= 100 else "Over budget"
            budget_detail = f"{budget_used_pct:.1f}% used"
        else:
            budget_status = "No budget"
            budget_detail = "Set category limits"
        st.metric("Spending Control", budget_status)
        st.caption(budget_detail)

    with c3:
        if monthly_income > 0:
            rate = (savings_capacity / monthly_income) * 100.0
            savings_detail = f"{rate:.1f}% capacity"
        else:
            savings_detail = "Income not set"
        st.metric(
            "Savings Health",
            money(savings_capacity),
        )
        st.caption(savings_detail)

    with c4:
        st.metric(
            "Emergency Readiness",
            f"{emergency_coverage * 100:.1f}%",
        )
        st.caption("Of 3-month target")

    st.divider()
    st.subheader("What is affecting your score?")

    positives = []
    concerns = []

    if monthly_income > 0 and monthly_cash_flow > 0:
        positives.append(
            f"Your income currently covers analyzed expenses, leaving about {money(savings_capacity)} in estimated monthly cash flow."
        )
    elif monthly_income <= 0:
        concerns.append(
            "Monthly income is not set, so FinSight-AI cannot fully assess cash-flow health."
        )
    else:
        concerns.append(
            f"Your analyzed expenses exceed available income by {money(abs(monthly_cash_flow))}."
        )

    if total_budget > 0 and budget_used_pct <= 100:
        positives.append(
            f"You are using {budget_used_pct:.1f}% of your current monthly budget."
        )
    elif total_budget > 0:
        concerns.append(
            f"Your analyzed spending is {budget_used_pct - 100:.1f}% above the total budget."
        )
    else:
        concerns.append(
            "No monthly budget is currently set, so spending control cannot be fully evaluated."
        )

    if savings_capacity > 0:
        positives.append(
            f"Your estimated monthly savings capacity is {money(savings_capacity)}."
        )
    else:
        concerns.append(
            "There is currently no positive monthly savings capacity."
        )

    if current_savings >= emergency_target and emergency_target > 0:
        positives.append(
            "Your current savings cover the 3-month emergency-fund target."
        )
    else:
        concerns.append(
            f"Your emergency-fund gap is {money(max(emergency_target - current_savings, 0.0))}."
        )

    if positives:
        st.markdown("**What is going well**")
        for item in positives:
            st.write(f"✓ {item}")

    if concerns:
        st.markdown("**What needs attention**")
        for item in concerns:
            st.write(f"• {item}")

    st.divider()
    st.subheader("Top actions to improve your score")

    actions = []

    if monthly_income <= 0:
        actions.append("Add your monthly income on the Dashboard.")
    elif monthly_cash_flow <= 0:
        actions.append("Reduce non-essential expenses or increase income until monthly cash flow becomes positive.")

    if total_budget <= 0:
        actions.append("Set realistic monthly limits for your main spending categories in Budget Planner.")
    elif over_budget_categories > 0:
        actions.append(f"Review the {over_budget_categories} category/categories currently above budget.")

    if current_savings < emergency_target:
        actions.append(
            f"Build toward a 3-month emergency fund of {money(emergency_target)}."
        )

    if category_spending:
        highest_category, highest_amount = max(
            category_spending.items(),
            key=lambda item: item[1],
        )
        actions.append(
            f"Review {highest_category}, your largest spending category at {money(highest_amount)}."
        )

    if not actions:
        actions.append(
            "Maintain your current spending discipline and continue building savings."
        )

    for index, action in enumerate(actions[:3], start=1):
        st.write(f"{index}. {action}")

    st.caption(
        "FinSight-AI health scores are planning guidance, not professional financial advice."
    )


# ============================================================
# RECURRING BILLS
# ============================================================

def recurring_bills_page():

    st.title(
        "🔁 Recurring Bills"
    )

    st.caption(
        "Manage your recurring monthly expenses."
    )

    st.subheader(
        "➕ Add Recurring Bill"
    )

    c1, c2 = st.columns(2)

    with c1:

        bill_name = st.text_input(
            "Bill Name"
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=100.0
        )

        category = st.selectbox(
            "Category",
            [

                "Entertainment",

                "Utilities",

                "Mobile",

                "Insurance",

                "Education",

                "Housing",

                "Medical",

                "Other",

            ]
        )

    with c2:

        due_day = st.number_input(
            "Due Day of Month",
            min_value=1,
            max_value=31,
            value=1
        )

        frequency = st.selectbox(
            "Frequency",
            [

                "monthly",

                "weekly",

                "yearly",

            ]
        )

    if st.button(
        "➕ Add Recurring Bill",
        width="stretch"
    ):

        if not bill_name.strip():

            st.warning(
                "Enter a bill name."
            )

        elif amount <= 0:

            st.warning(
                "Amount must be greater than zero."
            )

        else:

            try:

                add_recurring_bill(

                    st.session_state.user_id,

                    bill_name.strip(),

                    amount,

                    category,

                    int(due_day),

                    frequency

                )

                st.success(
                    "Recurring bill added."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Could not add bill: {e}"
                )

    st.divider()

    st.subheader(
        "📋 Your Recurring Bills"
    )

    try:

        bills = get_recurring_bills(
            st.session_state.user_id
        )

    except Exception as e:

        bills = []

        st.error(
            f"Could not load bills: {e}"
        )

    if bills:

        total_monthly = 0.0

        for bill in bills:

            (
                bill_id,
                bill_name,
                amount,
                category,
                due_day,
                frequency,
                active
            ) = bill

            amount = safe_float(
                amount
            )

            if frequency == "monthly":

                total_monthly += amount

            with st.container(
                border=True
            ):

                c1, c2, c3 = st.columns(
                    [2, 1, 1]
                )

                with c1:

                    st.markdown(
                        f"### 💳 {bill_name}"
                    )

                    st.write(
                        category
                    )

                with c2:

                    st.metric(
                        "Amount",
                        money(amount)
                    )

                with c3:

                    st.write(
                        f"Due: Day {due_day}"
                    )

                    st.write(
                        frequency
                    )

                    if st.button(
                        "Deactivate",
                        key=f"bill_{bill_id}"
                    ):

                        try:

                            deactivate_recurring_bill(

                                st.session_state.user_id,

                                bill_id

                            )

                            st.success(
                                "Bill deactivated."
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Error: {e}"
                            )

        st.divider()

        st.metric(
            "💳 Monthly Recurring Bills",
            money(total_monthly)
        )

    else:

        st.info(
            "No recurring bills added yet."
        )


# ============================================================
# FINANCIAL GOALS
# ============================================================

def financial_goals_page():

    st.title(
        "🎯 Financial Goals"
    )

    st.caption(
        "Create and track your personal financial goals."
    )

    st.subheader(
        "➕ Create Financial Goal"
    )

    c1, c2 = st.columns(2)

    with c1:

        goal_name = st.text_input(
            "Goal Name"
        )

        target_amount = st.number_input(
            "Target Amount (₹)",
            min_value=0.0,
            step=1000.0
        )

        current_amount = st.number_input(
            "Current Amount (₹)",
            min_value=0.0,
            step=1000.0
        )

    with c2:

        monthly_contribution = st.number_input(
            "Monthly Contribution (₹)",
            min_value=0.0,
            step=500.0
        )

        deadline = st.date_input(
            "Target Date",
            value=date.today()
        )

    if st.button(
        "🎯 Create Financial Goal",
        width="stretch"
    ):

        if not goal_name.strip():

            st.warning(
                "Enter a goal name."
            )

        elif target_amount <= 0:

            st.warning(
                "Target amount must be greater than zero."
            )

        else:

            try:

                add_financial_goal(

                    st.session_state.user_id,

                    goal_name.strip(),

                    target_amount,

                    current_amount,

                    monthly_contribution,

                    deadline.isoformat()

                )

                st.success(
                    "Financial goal created."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Could not create goal: {e}"
                )

    st.divider()

    st.subheader(
        "📋 Your Financial Goals"
    )

    try:

        goals = get_financial_goals(
            st.session_state.user_id
        )

    except Exception as e:

        goals = []

        st.error(
            f"Could not load goals: {e}"
        )

    if not goals:

        st.info(
            "No financial goals created yet."
        )

        return

    for goal in goals:

        (
            goal_id,
            goal_name,
            target_amount,
            current_amount,
            monthly_contribution,
            deadline
        ) = goal

        target_amount = safe_float(
            target_amount
        )

        current_amount = safe_float(
            current_amount
        )

        monthly_contribution = safe_float(
            monthly_contribution
        )

        if target_amount > 0:

            progress = (
                current_amount
                / target_amount
            )

        else:

            progress = 0.0

        progress = max(
            0.0,
            min(
                progress,
                1.0
            )
        )

        remaining = max(
            target_amount
            - current_amount,
            0
        )

        with st.container(
            border=True
        ):

            st.markdown(
                f"### 🎯 {goal_name}"
            )

            st.write(
                f"{money(current_amount)} / "
                f"{money(target_amount)}"
            )

            st.progress(
                progress
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Current Amount",
                money(current_amount)
            )

            c2.metric(
                "Monthly Contribution",
                money(monthly_contribution)
            )

            c3.metric(
                "Remaining",
                money(remaining)
            )

            if deadline:

                st.write(
                    f"📅 Deadline: **{deadline}**"
                )

            # ------------------------------------------------
            # Update
            # ------------------------------------------------

            with st.expander(
                "✏️ Update Goal"
            ):

                new_current = st.number_input(
                    "Current Amount",
                    min_value=0.0,
                    value=current_amount,
                    key=f"current_{goal_id}"
                )

                new_contribution = st.number_input(
                    "Monthly Contribution",
                    min_value=0.0,
                    value=monthly_contribution,
                    key=f"contribution_{goal_id}"
                )

                if st.button(
                    "💾 Update",
                    key=f"update_{goal_id}"
                ):

                    try:

                        update_financial_goal(

                            st.session_state.user_id,

                            goal_id,

                            new_current,

                            new_contribution

                        )

                        st.success(
                            "Goal updated."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Update error: {e}"
                        )

            # ------------------------------------------------
            # Delete
            # ------------------------------------------------

            if st.button(
                "🗑️ Delete Goal",
                key=f"delete_{goal_id}"
            ):

                try:

                    delete_financial_goal(

                        st.session_state.user_id,

                        goal_id

                    )

                    st.success(
                        "Goal deleted."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Delete error: {e}"
                    )


# ============================================================
# AI FINANCIAL AGENT
# ============================================================

def ai_financial_agent_page():

    st.markdown(
        '<div class="page-kicker">AI ASSISTANT</div>',
        unsafe_allow_html=True,
    )

    st.title("AI Financial Agent")

    st.caption(
        "Ask questions about your spending, savings, budget, and emergency fund."
    )

    if not AGENT_MODULE_READY:

        st.error("Financial Agent module is not available.")

        if AGENT_MODULE_ERROR:
            st.caption(AGENT_MODULE_ERROR)

        st.info(
            "Make sure backend/financial_agent.py exists and can be imported."
        )
        return

    # --------------------------------------------------------
    # VERIFIED FINANCIAL PROFILE
    # --------------------------------------------------------

    profile = get_financial_profile(
        st.session_state.user_id
    )

    if profile:

        monthly_income = safe_float(profile[0])
        current_savings = safe_float(profile[1])
        family_support = safe_float(profile[2])

    else:

        monthly_income = 0.0
        current_savings = 0.0
        family_support = 0.0

    # --------------------------------------------------------
    # VERIFIED TRANSACTION ANALYSIS
    # Uses the same analyzed dataframe as the other pages.
    # --------------------------------------------------------

    analysis_df = st.session_state.analysis_df

    total_expenses = 0.0
    highest_category = "None"
    highest_category_amount = 0.0
    category_spending = {}

    if (
        analysis_df is not None
        and not analysis_df.empty
        and "amount" in analysis_df.columns
    ):

        data = analysis_df.copy()

        data["amount"] = pd.to_numeric(
            data["amount"],
            errors="coerce",
        )

        data = data.dropna(
            subset=["amount"]
        )

        data = data[
            data["amount"] > 0
        ].copy()

        if not data.empty:

            total_expenses = float(
                data["amount"].sum()
            )

            if "category" in data.columns:

                data["category"] = (
                    data["category"]
                    .fillna("Other")
                    .astype(str)
                    .str.strip()
                )

                data.loc[
                    data["category"] == "",
                    "category"
                ] = "Other"

                category_spending = (
                    data.groupby("category")["amount"]
                    .sum()
                    .to_dict()
                )

                if category_spending:

                    highest_category = max(
                        category_spending,
                        key=category_spending.get,
                    )

                    highest_category_amount = float(
                        category_spending[
                            highest_category
                        ]
                    )

            try:
                category_spending = tool_get_category_spending(
                    category_spending
                )
            except Exception:
                category_spending = {
                    str(k): float(v)
                    for k, v in category_spending.items()
                }

    # --------------------------------------------------------
    # VERIFIED BUDGET DATA
    # --------------------------------------------------------

    budget_limits = st.session_state.get(
        "budget_limits",
        {},
    )

    budget_status = tool_get_budget_status(
        budget_limits=budget_limits,
        category_spending=category_spending,
    )

    snapshot = tool_get_financial_snapshot(
        monthly_income=monthly_income,
        current_savings=current_savings,
        family_support=family_support,
        total_expenses=total_expenses,
        highest_category=highest_category,
        highest_category_amount=highest_category_amount,
        budget_limits=budget_limits,
        category_spending=category_spending,
    )

    emergency = tool_get_emergency_fund(
        current_savings=current_savings,
        monthly_expenses=total_expenses,
        target_months=3,
    )

    # --------------------------------------------------------
    # VERIFIED SAVINGS GOAL DATA
    # --------------------------------------------------------
    #
    # Savings Planner stores its current widget values in
    # Streamlit session state. Reuse those values here so the
    # agent can evaluate the same plan without asking Qwen
    # to calculate it.
    #
    savings_plan = st.session_state.get(
        "savings_plan",
        {},
    ).copy()

    savings_plan["target_amount"] = safe_float(
        savings_plan.get(
            "target_amount",
            st.session_state.get(
                "savings_target_amount",
                0.0,
            ),
        )
    )

    savings_plan["target_months"] = safe_float(
        savings_plan.get(
            "target_months",
            st.session_state.get(
                "savings_target_months",
                6,
            ),
        )
    )

    savings_plan["current_savings"] = current_savings

    savings_plan["desired_monthly_saving"] = safe_float(
        savings_plan.get(
            "desired_monthly_saving",
            st.session_state.get(
                "desired_monthly_saving",
                0.0,
            ),
        )
    )

    savings_plan["potential_monthly_savings"] = max(
        snapshot["monthly_cash_flow"],
        0.0,
    )

    savings_plan["feasible_monthly_saving"] = max(
        snapshot["monthly_cash_flow"],
        0.0,
    )

    target_amount_for_agent = safe_float(
        savings_plan.get(
            "target_amount",
            0.0,
        )
    )

    target_months_for_agent = max(
        safe_float(
            savings_plan.get(
                "target_months",
                6,
            )
        ),
        1.0,
    )

    target_gap_for_agent = max(
        target_amount_for_agent
        - current_savings,
        0.0,
    )

    savings_plan["required_monthly_saving"] = (
        target_gap_for_agent
        / target_months_for_agent
    )

    savings_plan["emergency_target"] = (
        total_expenses * 3.0
    )

    savings_plan["emergency_gap"] = max(
        savings_plan["emergency_target"]
        - current_savings,
        0.0,
    )

    savings_goal = tool_get_savings_goal_status(
        savings_plan=savings_plan,
    )

    # --------------------------------------------------------
    # VERIFIED SAVED RECURRING BILLS + FINANCIAL GOALS
    # These come from SQLite, not Streamlit session state.
    # --------------------------------------------------------

    saved_bill_rows = get_recurring_bills(
        st.session_state.user_id
    )

    recurring_bills = [
        {
            "id": row[0],
            "bill_name": row[1],
            "amount": safe_float(row[2]),
            "category": row[3],
            "due_day": row[4],
            "frequency": row[5],
            "active": row[6],
        }
        for row in saved_bill_rows
    ]

    saved_goal_rows = get_financial_goals(
        st.session_state.user_id
    )

    financial_goals = [
        {
            "id": row[0],
            "goal_name": row[1],
            "target_amount": safe_float(row[2]),
            "current_amount": safe_float(row[3]),
            "monthly_contribution": safe_float(row[4]),
            "deadline": row[5],
        }
        for row in saved_goal_rows
    ]

    # --------------------------------------------------------
    # FINANCIAL AGENT TOOLS
    # --------------------------------------------------------

    # --------------------------------------------------------
    # ASK THE AGENT
    # --------------------------------------------------------

    st.markdown("### Ask your financial agent")

    question = st.text_area(
        "Financial question",
        placeholder=(
            "Example: How much can I save this month?\n"
            "Example: How healthy is my current cash flow?\n"
            "Example: How much emergency fund should I build?\n"
            "Example: Am I spending too much?\n"
            "Example: Am I over budget?\n"
            "Example: Am I on track for my savings goal?"
        ),
        height=120,
        key="financial_agent_question",
    )

    if st.button(
        "Ask Financial Agent",
        type="primary",
        width="stretch",
        key="ask_financial_agent",
    ):

        if not question.strip():

            st.warning(
                "Please enter a financial question."
            )

        else:

            with st.spinner(
                "Financial agent is analyzing your data..."
            ):

                result = run_financial_agent(
                    question=question,
                    snapshot=snapshot,
                    emergency=emergency,
                    category_spending=category_spending,
                    budget_status=budget_status,
                    savings_goal=savings_goal,
                    recurring_bills=recurring_bills,
                    financial_goals=financial_goals,
                    ollama_base_url=OLLAMA_BASE_URL,
                    ollama_model=OLLAMA_MODEL,
                )

            if result.get("success"):

                st.markdown("### Agent Response")

                st.write(
                    result.get(
                        "answer",
                        "",
                    )
                )

                st.caption(
                    f"Source: {result.get('source', 'Financial Agent')}"
                )

                tools_used = result.get(
                    "tools_used",
                    [],
                )

                if tools_used:

                    st.caption(
                        "Tools used: "
                        + " • ".join(tools_used)
                    )

            else:

                st.error(
                    result.get(
                        "answer",
                        "Unable to answer safely.",
                    )
                )

                if result.get("error"):
                    st.caption(
                        f"Agent error: {result.get('error')}"
                    )

    # --------------------------------------------------------
    # VERIFIED CONTEXT
    # --------------------------------------------------------

    st.markdown("### Verified financial context")

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Monthly Income",
            money(snapshot["monthly_income"]),
        )

    with c2:

        st.metric(
            "Analyzed Expenses",
            money(snapshot["total_expenses"]),
        )

    with c3:

        st.metric(
            "Current Savings",
            money(snapshot["current_savings"]),
        )

    with c4:

        st.metric(
            "Monthly Cash Flow",
            money(snapshot["monthly_cash_flow"]),
        )

    st.markdown("### Saved data available to agent")

    st.write(
        f"Recurring bills saved: {len(recurring_bills)}"
    )
    st.write(
        f"Financial goals saved: {len(financial_goals)}"
    )

    st.markdown("### Agent safety")

    st.info(
        "The agent does not access your bank account or make transactions. "
        "Your app calculates the financial values first, and the local "
        f"{OLLAMA_MODEL} model is used to explain those verified results."
    )


# ============================================================
# APPLICATION ROUTER
# ============================================================

def main():


    # --------------------------------------------------------
    # Backend check
    # --------------------------------------------------------

    if not BACKEND_READY:

        st.error(
            "❌ FinSight-AI backend could not be loaded."
        )

        st.code(
            BACKEND_ERROR
            or "Unknown backend error"
        )

        st.info(
            "Make sure your project has this structure:\n\n"
            "FinSight-AI/\n"
            "├── backend/\n"
            "│   ├── __init__.py\n"
            "│   ├── database.py\n"
            "│   ├── analysis.py\n"
            "│   └── ai_advice.py\n"
            "└── frontend/\n"
            "    └── app.py"
        )

        return

    # --------------------------------------------------------
    # Login
    # --------------------------------------------------------

    if not st.session_state.logged_in:

        login_page()

        return

    # --------------------------------------------------------
    # Sidebar
    # --------------------------------------------------------

    sidebar()

    # --------------------------------------------------------
    # Router
    # --------------------------------------------------------

    page = st.session_state.page

    if page == "Dashboard":

        dashboard_page()

    elif page == "Transaction Analysis":

        transaction_analysis_page()

    elif page == "Budget Planner":

        budget_planner_page()

    elif page == "Savings Planner":

        savings_planner_page()

    elif page == "Emergency Fund":

        emergency_fund_page()

    elif page == "Financial Health":

        financial_health_page()

    elif page == "AI Financial Agent":

        ai_financial_agent_page()

    elif page == "Recurring Bills":

        recurring_bills_page()

    elif page == "Financial Goals":

        financial_goals_page()

    else:

        dashboard_page()

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

    st.divider()

    st.caption(
        " FinSight-AI | Personal Financial Analysis Assistant"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()