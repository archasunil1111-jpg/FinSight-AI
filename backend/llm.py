import requests


# ==================================================
# FINSIGHT-AI LLM
# ==================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"


# ==================================================
# GENERATE FINANCIAL ADVICE
# ==================================================

def generate_financial_advice(insights):

    # --------------------------------------------------
    # BASIC INSIGHTS
    # --------------------------------------------------

    total_spending = float(
        insights.get("total_spending", 0.0)
    )

    average_transaction = float(
        insights.get("average_transaction", 0.0)
    )

    median_transaction = float(
        insights.get("median_transaction", 0.0)
    )

    highest_transaction = float(
        insights.get("highest_transaction", 0.0)
    )

    lowest_transaction = float(
        insights.get("lowest_transaction", 0.0)
    )

    transaction_count = int(
        insights.get("transaction_count", 0)
    )


    # --------------------------------------------------
    # CATEGORY
    # --------------------------------------------------

    highest_category = insights.get(
        "highest_category",
        "N/A"
    )

    highest_category_amount = float(
        insights.get(
            "highest_category_amount",
            0.0
        )
    )

    highest_category_percentage = float(
        insights.get(
            "highest_category_percentage",
            0.0
        )
    )

    category_spending = insights.get(
        "category_spending",
        {}
    )


    category_text = ""

    for category, amount in category_spending.items():

        category_text += (
            f"- {category}: "
            f"₹{float(amount):,.2f}\n"
        )

    if not category_text:
        category_text = "No category data available."


    # --------------------------------------------------
    # DAILY
    # --------------------------------------------------

    highest_spending_day = insights.get(
        "highest_spending_day",
        "N/A"
    )

    highest_spending_day_amount = float(
        insights.get(
            "highest_spending_day_amount",
            0.0
        )
    )


    # --------------------------------------------------
    # MONTHLY
    # --------------------------------------------------

    monthly_spending = insights.get(
        "monthly_spending",
        {}
    )

    monthly_text = ""

    for month, amount in monthly_spending.items():

        monthly_text += (
            f"- {month}: "
            f"₹{float(amount):,.2f}\n"
        )

    if not monthly_text:
        monthly_text = "No monthly spending data available."


    # --------------------------------------------------
    # TRANSACTION PATTERNS
    # --------------------------------------------------

    unusual_transactions = int(
        insights.get(
            "unusual_transactions",
            0
        )
    )

    high_spending_transactions = int(
        insights.get(
            "high_spending_transactions",
            0
        )
    )


    # --------------------------------------------------
    # TOP TRANSACTIONS
    # --------------------------------------------------

    top_transactions = insights.get(
        "top_transactions",
        []
    )

    top_transaction_text = ""

    for transaction in top_transactions:

        top_transaction_text += (
            f"- {transaction.get('date', 'N/A')} | "
            f"{transaction.get('description', 'N/A')} | "
            f"₹{float(transaction.get('amount', 0.0)):,.2f} | "
            f"{transaction.get('category', 'Other')}\n"
        )

    if not top_transaction_text:

        top_transaction_text = (
            "No top transaction information available."
        )


    # ==================================================
    # PROMPT
    # ==================================================

    prompt = f"""
You are FinSight-AI, a personal financial analysis assistant.

Analyze the financial information below.

IMPORTANT RULES:

- Use only the supplied information.
- Never invent transactions.
- Never invent income.
- Never invent financial facts.
- Do not claim certainty when the data does not support it.
- Give practical budgeting and savings suggestions.
- Do not provide investment recommendations.
- Do not provide high-risk financial advice.
- Do not explain your internal reasoning.
- Do not create Markdown tables.
- Do not create category tables.
- Do not repeat the complete category breakdown.
- Do not repeat the complete transaction list.
- Keep the response concise.
- Use Indian Rupee formatting where appropriate.

==================================================
TRANSACTION SUMMARY
==================================================

Number of transactions:
{transaction_count}

Total spending:
₹{total_spending:,.2f}

Average transaction:
₹{average_transaction:,.2f}

Median transaction:
₹{median_transaction:,.2f}

Highest transaction:
₹{highest_transaction:,.2f}

Lowest transaction:
₹{lowest_transaction:,.2f}


==================================================
CATEGORY ANALYSIS
==================================================

Highest spending category:
{highest_category}

Amount spent in highest category:
₹{highest_category_amount:,.2f}

Highest category share:
{highest_category_percentage:.1f}%

Category information:

{category_text}


==================================================
DAILY SPENDING
==================================================

Highest spending day:
{highest_spending_day}

Amount spent on that day:
₹{highest_spending_day_amount:,.2f}


==================================================
MONTHLY SPENDING
==================================================

{monthly_text}


==================================================
SPENDING PATTERNS
==================================================

Unusual transactions:
{unusual_transactions}

Transactions above average transaction amount:
{high_spending_transactions}


==================================================
LARGEST TRANSACTIONS
==================================================

{top_transaction_text}


==================================================
RESPONSE FORMAT
==================================================

Respond using exactly these sections:

**Spending Summary:**

Write 1-2 concise sentences summarizing the spending.

**Main Concern:**

Identify the most important spending pattern that deserves attention.

If there is no obvious concern, say:
"Spending appears reasonably distributed based on the available data."

**Two Practical Suggestions:**

1. Give one practical budgeting or spending-control suggestion.
2. Give one practical savings or financial-management suggestion.

Do not add any other sections.
"""


    # ==================================================
    # OLLAMA REQUEST
    # ==================================================

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 180
                }
            },
            timeout=180
        )

        response.raise_for_status()

        result = response.json()

        advice = result.get(
            "response",
            ""
        ).strip()


        if not advice:

            return (
                "⚠️ Llama did not return financial advice."
            )


        return advice


    # ==================================================
    # OLLAMA CONNECTION ERROR
    # ==================================================

    except requests.exceptions.ConnectionError:

        return (
            "⚠️ Unable to connect to Ollama. "
            "Please make sure Ollama is running."
        )


    # ==================================================
    # TIMEOUT
    # ==================================================

    except requests.exceptions.Timeout:

        return (
            "⚠️ Ollama took too long to respond. "
            "Please try again."
        )


    # ==================================================
    # OTHER ERROR
    # ==================================================

    except requests.exceptions.RequestException as e:

        return (
            f"⚠️ Ollama request failed: {e}"
        )


    except Exception as e:

        return (
            f"⚠️ An error occurred while generating "
            f"AI advice: {e}"
        )