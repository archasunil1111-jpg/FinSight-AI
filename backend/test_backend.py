from analysis import analyze_transactions
from llm import generate_financial_advice


# Analyze transactions
df, insights = analyze_transactions(
    "data/transactions.csv"
)

print("\n--- FINANCIAL INSIGHTS ---")
print(insights)


# Generate AI advice
advice = generate_financial_advice(insights)

print("\n--- AI FINANCIAL ADVICE ---")
print(advice)