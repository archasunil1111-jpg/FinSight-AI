import requests
import re


# ============================================================
# FinSight-AI
# AI FINANCIAL ADVICE ENGINE
# ============================================================

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen3:4b"


# ============================================================
# SAFE NUMBER HELPERS
# ============================================================

def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ============================================================
# CLEAN MODEL RESPONSE
# ============================================================

def _clean_response(text):
    """
    Removes Qwen thinking blocks and unnecessary formatting.
    """

    if not text:
        return ""

    text = str(text).strip()

    # Remove <think>...</think>
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Remove markdown fences
    text = text.replace("```text", "")
    text = text.replace("```markdown", "")
    text = text.replace("```", "")

    return text.strip()


# ============================================================
# PARSE MODEL RESPONSE
# ============================================================

def _format_response(text):
    """
    Converts model output into:

    {
        summary,
        concern,
        suggestion1,
        suggestion2
    }
    """

    if not text:
        return None

    text = _clean_response(text)

    if not text:
        return None

    # --------------------------------------------------------
    # Normalize markdown
    # --------------------------------------------------------

    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"__", "", text)

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary_match = re.search(
        r"Spending\s+Summary\s*:\s*(.*?)(?=\n\s*Main\s+Concern\s*:|\Z)",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    # --------------------------------------------------------
    # Concern
    # --------------------------------------------------------

    concern_match = re.search(
        r"Main\s+Concern\s*:\s*(.*?)(?=\n\s*Two\s+Practical\s+Suggestions\s*:|\Z)",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    # --------------------------------------------------------
    # Suggestions
    # --------------------------------------------------------

    suggestions_match = re.search(
        r"Two\s+Practical\s+Suggestions\s*:\s*(.*)$",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    if not summary_match or not concern_match:
        return None

    summary = summary_match.group(1).strip()
    concern = concern_match.group(1).strip()

    suggestion1 = ""
    suggestion2 = ""

    if suggestions_match:

        suggestions_text = suggestions_match.group(1).strip()

        # Remove unnecessary markdown
        suggestions_text = re.sub(
            r"\*\*",
            "",
            suggestions_text
        )

        # ----------------------------------------------------
        # Find numbered suggestions
        # ----------------------------------------------------

        matches = re.findall(
            r"(?:^|\n)\s*(?:1[\.\):]|[-•])\s*(.*?)(?=\n\s*(?:2[\.\):]|[-•])|\Z)",
            suggestions_text,
            flags=re.DOTALL
        )

        if len(matches) >= 1:
            suggestion1 = matches[0].strip()

        if len(matches) >= 2:
            suggestion2 = matches[1].strip()

        # ----------------------------------------------------
        # Inline backup
        # ----------------------------------------------------

        if not suggestion1 or not suggestion2:

            inline_match = re.search(
                r"1[\.\):]\s*(.*?)\s*2[\.\):]\s*(.*)",
                suggestions_text,
                flags=re.DOTALL
            )

            if inline_match:

                suggestion1 = inline_match.group(1).strip()
                suggestion2 = inline_match.group(2).strip()

    # --------------------------------------------------------
    # Clean numbering
    # --------------------------------------------------------

    suggestion1 = re.sub(
        r"^1[\.\):]\s*",
        "",
        suggestion1
    ).strip()

    suggestion2 = re.sub(
        r"^2[\.\):]\s*",
        "",
        suggestion2
    ).strip()

    summary = summary.strip()
    concern = concern.strip()

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if not summary:
        return None

    if not concern:
        return None

    if not suggestion1:
        return None

    if not suggestion2:
        return None

    return {
        "summary": summary,
        "concern": concern,
        "suggestion1": suggestion1,
        "suggestion2": suggestion2
    }


# ============================================================
# DETERMINISTIC FALLBACK
# ============================================================

def _fallback_advice(data):
    """
    Reliable advice generated directly from verified statistics.

    This does NOT depend on Ollama.
    """

    total = _safe_float(
        data.get("total_spending")
    )

    count = _safe_int(
        data.get("transaction_count")
    )

    average = _safe_float(
        data.get("average_transaction")
    )

    category = str(
        data.get(
            "highest_category",
            "Unknown"
        )
    ).strip()

    category_amount = _safe_float(
        data.get("highest_category_amount")
    )

    category_percentage = _safe_float(
        data.get("highest_category_percentage")
    )

    unusual = _safe_int(
        data.get("unusual_transactions")
    )

    high_spending = _safe_int(
        data.get("high_spending_transactions")
    )

    highest_day = str(
        data.get(
            "highest_spending_day",
            "Unknown"
        )
    ).strip()

    # ========================================================
    # SPENDING SUMMARY
    # ========================================================

    if category != "Unknown":

        summary = (
            f"Spending totaled ₹{total:,.2f} across "
            f"{count} transactions. "
            f"{category} was the highest spending category "
            f"at ₹{category_amount:,.2f}."
        )

    else:

        summary = (
            f"Spending totaled ₹{total:,.2f} across "
            f"{count} transactions, with an average "
            f"transaction of ₹{average:,.2f}."
        )

    # ========================================================
    # MAIN CONCERN
    # ========================================================

    if category != "Unknown":

        concern = (
            f"{category} is the largest spending category, "
            f"accounting for {category_percentage:.1f}% "
            f"of total spending at ₹{category_amount:,.2f}."
        )

    elif high_spending > 0:

        concern = (
            f"{high_spending} transactions were above "
            f"the average transaction amount of "
            f"₹{average:,.2f}."
        )

    else:

        concern = (
            f"The average transaction amount was "
            f"₹{average:,.2f} across {count} transactions."
        )

    # ========================================================
    # SUGGESTION 1
    # ========================================================

    if category != "Unknown":

        suggestion1 = (
            f"Review your {category} transactions and "
            f"identify purchases that could be reduced."
        )

    elif high_spending > 0:

        suggestion1 = (
            f"Review the {high_spending} transactions "
            f"that were above the average amount."
        )

    else:

        suggestion1 = (
            "Review your transactions regularly to "
            "identify opportunities to reduce spending."
        )

    # ========================================================
    # SUGGESTION 2
    # ========================================================

    if highest_day != "Unknown":

        suggestion2 = (
            f"Monitor spending on {highest_day}, "
            f"which was the highest-spending day "
            f"in the analyzed data."
        )

    elif unusual > 0:

        suggestion2 = (
            f"Review the {unusual} unusual transaction"
            f"{'s' if unusual != 1 else ''} identified "
            f"in the analysis."
        )

    else:

        suggestion2 = (
            "Continue tracking your spending to "
            "identify changes over time."
        )

    return {
        "summary": summary,
        "concern": concern,
        "suggestion1": suggestion1,
        "suggestion2": suggestion2
    }


# ============================================================
# QWEN PROMPT
# ============================================================

def _build_prompt(data):

    total = _safe_float(
        data.get("total_spending")
    )

    count = _safe_int(
        data.get("transaction_count")
    )

    average = _safe_float(
        data.get("average_transaction")
    )

    category = str(
        data.get(
            "highest_category",
            "Unknown"
        )
    )

    category_amount = _safe_float(
        data.get("highest_category_amount")
    )

    category_percentage = _safe_float(
        data.get("highest_category_percentage")
    )

    unusual = _safe_int(
        data.get("unusual_transactions")
    )

    high_spending = _safe_int(
        data.get("high_spending_transactions")
    )

    highest_day = str(
        data.get(
            "highest_spending_day",
            "Unknown"
        )
    )

    return f"""
You are FinSight-AI.

Use ONLY these verified statistics.

Total spending: ₹{total:,.2f}
Transactions: {count}
Average transaction: ₹{average:,.2f}
Highest category: {category}
Highest category amount: ₹{category_amount:,.2f}
Highest category percentage: {category_percentage:.1f}%
Unusual transactions: {unusual}
High-spending transactions: {high_spending}
Highest spending day: {highest_day}

Rules:
- Do not invent information.
- Do not invent transactions.
- Do not invent categories.
- Do not mention income.
- Do not mention savings.
- Do not give investment advice.
- Do not give loan advice.
- Do not explain reasoning.
- Do not show thinking.
- Keep every sentence concise.

Return ONLY this format:

Spending Summary: one concise sentence.

Main Concern: one concise sentence.

Two Practical Suggestions:
1. one concise suggestion.
2. one concise suggestion.
""".strip()


# ============================================================
# TRY OLLAMA
# ============================================================

def _try_ollama(data):

    prompt = _build_prompt(data)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "think": False,

        "options": {
            "temperature": 0.0,

            # Keep response short
            "num_predict": 120,

            # Reduce unnecessary generation
            "top_p": 0.8
        }
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=90
        )

        response.raise_for_status()

        result = response.json()

        # ----------------------------------------------------
        # Ollama response
        # ----------------------------------------------------

        answer = result.get(
            "response",
            ""
        )

        answer = _clean_response(answer)

        # ----------------------------------------------------
        # Some Ollama versions may return thinking separately
        # ----------------------------------------------------

        if not answer:

            answer = result.get(
                "thinking",
                ""
            )

            answer = _clean_response(answer)

        if not answer:
            return None

        # ----------------------------------------------------
        # Parse
        # ----------------------------------------------------

        formatted = _format_response(answer)

        if formatted:

            formatted["source"] = "qwen3"

            return formatted

        return None

    except Exception:

        return None


# ============================================================
# MAIN FUNCTION
# ============================================================

def generate_financial_advice(data):
    """
    Generate financial advice.

    Priority:

        1. Qwen3
        2. Deterministic fallback

    This guarantees that FinSight-AI
    always displays useful advice.
    """

    if not isinstance(data, dict):

        return {
            "summary": (
                "Unable to analyze financial data."
            ),

            "concern": (
                "Verified transaction statistics "
                "were not available."
            ),

            "suggestion1": (
                "Upload valid transaction data."
            ),

            "suggestion2": (
                "Try analyzing the transactions again."
            ),

            "source": "fallback"
        }

    # ========================================================
    # FIRST: TRY QWEN
    # ========================================================

    qwen_result = _try_ollama(data)

    if qwen_result is not None:

        return qwen_result

    # ========================================================
    # SECOND: GUARANTEED FALLBACK
    # ========================================================

    fallback = _fallback_advice(data)

    fallback["source"] = "fallback"

    return fallback