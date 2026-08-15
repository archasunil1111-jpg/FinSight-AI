import pandas as pd
import numpy as np


def assign_category(description):
    description = description.lower()

    if any(word in description for word in [
        "swiggy", "zomato", "restaurant", "supermarket",
        "grocery", "food"
    ]):
        return "Food"

    elif any(word in description for word in [
        "uber", "ola", "fuel", "petrol", "transport"
    ]):
        return "Transport"

    elif any(word in description for word in [
        "amazon", "flipkart", "shopping", "myntra"
    ]):
        return "Shopping"

    elif any(word in description for word in [
        "netflix", "spotify", "movie", "entertainment"
    ]):
        return "Entertainment"

    elif any(word in description for word in [
        "electricity", "water", "internet", "utility"
    ]):
        return "Utilities"

    else:
        return "Other"


def analyze_transactions(file_path):

    # Load CSV
    df = pd.read_csv(file_path)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Convert date
    df["date"] = pd.to_datetime(df["date"])

    # Convert amount to numeric
    df["amount"] = pd.to_numeric(df["amount"])

    # Create category
    df["category"] = df["description"].apply(assign_category)

    # Date features
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["day"] = df["date"].dt.day
    df["month_number"] = df["date"].dt.month
    df["day_of_week"] = df["date"].dt.dayofweek

    # Total spending
    total_spending = df["amount"].sum()

    # Average transaction
    average_transaction = df["amount"].mean()

    # Category spending
    category_spending = df.groupby("category")["amount"].sum()

    highest_category = category_spending.idxmax()
    highest_category_amount = category_spending.max()

    highest_category_percentage = (
        highest_category_amount / total_spending
    ) * 100

    # Anomaly detection using IQR
    Q1 = df["amount"].quantile(0.25)
    Q3 = df["amount"].quantile(0.75)

    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    df["anomaly"] = np.where(
        (df["amount"] < lower_bound) |
        (df["amount"] > upper_bound),
        -1,
        1
    )

    df["anomaly_status"] = df["anomaly"].map({
        1: "Normal",
        -1: "Unusual"
    })

    unusual_transactions = (df["anomaly"] == -1).sum()

    # High spending transactions
    high_spending_transactions = (
        df["amount"] > average_transaction
    ).sum()

    # Insights
    insights = {
        "total_spending": total_spending,
        "average_transaction": average_transaction,
        "highest_category": highest_category,
        "highest_category_amount": highest_category_amount,
        "highest_category_percentage": highest_category_percentage,
        "unusual_transactions": unusual_transactions,
        "high_spending_transactions": high_spending_transactions
    }

    return df, insights