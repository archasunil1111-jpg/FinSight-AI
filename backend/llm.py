import requests


def generate_financial_advice(insights):

    prompt = f"""
You are FinSight-AI, a personal financial analysis assistant.

Analyze these financial insights:

Total spending: ₹{float(insights['total_spending']):.2f}
Average transaction: ₹{float(insights['average_transaction']):.2f}
Highest spending category: {insights['highest_category']}
Amount spent in highest category: ₹{float(insights['highest_category_amount']):.2f}
Percentage of spending in highest category: {float(insights['highest_category_percentage']):.1f}%
Unusual transactions: {int(insights['unusual_transactions'])}
High-spending transactions: {int(insights['high_spending_transactions'])}

Provide:

1. Spending Summary
2. Main Concern
3. Two Practical Suggestions

Keep the answer concise.
Do not explain your reasoning.
Do not invent transaction details.
"""


    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:3b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 200
                }
            },
            timeout=90
        )

        response.raise_for_status()

        result = response.json()

        return result["response"].strip()

    except requests.exceptions.ConnectionError:
        return "Unable to connect to Ollama. Please make sure Ollama is running."

    except requests.exceptions.Timeout:
        return "Ollama took too long to respond. Please try again."

    except Exception as e:
        return f"An error occurred while generating AI advice: {e}"