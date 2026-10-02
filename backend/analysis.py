import pandas as pd
import numpy as np
import re


# ============================================================
# FIN SIGHT-AI
# ADVANCED TRANSACTION ANALYSIS ENGINE
# ============================================================


# ============================================================
# CATEGORY KEYWORDS
# ============================================================

CATEGORY_KEYWORDS = {

    "Food": [
        "swiggy",
        "zomato",
        "restaurant",
        "food",
        "cafe",
        "coffee",
        "bakery",
        "grocery",
        "groceries",
        "supermarket",
        "bigbasket",
        "zepto",
        "blinkit",
        "instamart",
        "dominos",
        "pizza",
        "kfc",
        "mcdonald",
        "burger",
        "meal",
        "dining"
    ],

    "Transport": [
        "uber",
        "ola",
        "rapido",
        "fuel",
        "petrol",
        "diesel",
        "transport",
        "bus",
        "train",
        "metro",
        "taxi",
        "auto",
        "parking",
        "toll",
        "irctc"
    ],

    "Shopping": [
        "amazon",
        "flipkart",
        "myntra",
        "shopping",
        "mall",
        "clothing",
        "clothes",
        "fashion",
        "ajio",
        "meesho",
        "snapdeal",
        "decathlon"
    ],

    "Entertainment": [
        "netflix",
        "spotify",
        "prime video",
        "youtube premium",
        "hotstar",
        "movie",
        "cinema",
        "entertainment",
        "game",
        "gaming",
        "bookmyshow",
        "disney"
    ],

    "Utilities": [
        "electricity",
        "water bill",
        "internet",
        "wifi",
        "utility",
        "kseb",
        "broadband",
        "electric bill",
        "gas bill",
        "lpg"
    ],

    "Medical": [
        "hospital",
        "medical",
        "medicine",
        "pharmacy",
        "doctor",
        "clinic",
        "health",
        "apollo",
        "diagnostic",
        "lab"
    ],

    "Education": [
        "course",
        "college",
        "school",
        "education",
        "book",
        "udemy",
        "coursera",
        "training",
        "exam",
        "tuition",
        "academy"
    ],

    "Insurance": [
        "insurance",
        "lic",
        "premium",
        "policy"
    ],

    "Loan/EMI": [
        "emi",
        "loan",
        "credit card",
        "repayment",
        "installment",
        "borrow"
    ],

    "Housing": [
        "rent",
        "house rent",
        "housing",
        "home",
        "maintenance",
        "apartment"
    ],

    "Mobile": [
        "mobile",
        "phone bill",
        "airtel",
        "jio",
        "vi",
        "vodafone",
        "recharge",
        "prepaid",
        "postpaid"
    ]
}


# ============================================================
# COLUMN ALIASES
# ============================================================

COLUMN_ALIASES = {

    "date": [
        "date",
        "transaction_date",
        "transaction date",
        "datetime",
        "timestamp"
    ],

    "description": [
        "description",
        "details",
        "detail",
        "merchant",
        "merchant_name",
        "merchant name",
        "transaction",
        "narration",
        "remarks",
        "name"
    ],

    "amount": [
        "amount",
        "transaction_amount",
        "transaction amount",
        "value",
        "expense",
        "debit",
        "withdrawal"
    ],

    "category": [
        "category",
        "expense_category",
        "expense category",
        "type_category",
        "spending_category"
    ]
}


# ============================================================
# NORMALIZE COLUMN NAME
# ============================================================

def normalize_column_name(column):

    column = str(column)

    column = column.strip().lower()

    column = re.sub(
        r"[^a-z0-9]+",
        "_",
        column
    )

    column = column.strip("_")

    return column


# ============================================================
# FIND COLUMN
# ============================================================

def find_column(
    columns,
    aliases
):

    normalized_columns = {
        normalize_column_name(column): column
        for column in columns
    }

    for alias in aliases:

        normalized_alias = normalize_column_name(
            alias
        )

        if normalized_alias in normalized_columns:

            return normalized_columns[
                normalized_alias
            ]

    return None


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(value):

    if pd.isna(value):

        return ""

    value = str(value)

    value = value.strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value


# ============================================================
# CATEGORY DETECTION
# ============================================================

def assign_category(description):

    description = clean_text(
        description
    ).lower()

    if not description:

        return "Other"

    # --------------------------------------------------------
    # Exact keyword matching
    # --------------------------------------------------------

    for category, keywords in CATEGORY_KEYWORDS.items():

        for keyword in keywords:

            keyword = keyword.lower()

            if keyword in description:

                return category

    return "Other"


# ============================================================
# CATEGORY CLEANING
# ============================================================

def clean_category(value):

    if pd.isna(value):

        return ""

    value = clean_text(value)

    if not value:

        return ""

    # Normalize common category spellings

    category_map = {

        "food & dining": "Food",
        "food and dining": "Food",
        "foods": "Food",

        "transportation": "Transport",
        "travel": "Transport",

        "shopping & retail": "Shopping",
        "retail": "Shopping",

        "entertainment & leisure":
            "Entertainment",

        "medical & health":
            "Medical",
        "healthcare":
            "Medical",

        "education & training":
            "Education",

        "loan":
            "Loan/EMI",
        "emi":
            "Loan/EMI",

        "utilities":
            "Utilities",

        "housing & rent":
            "Housing",

        "mobile recharge":
            "Mobile"
    }

    key = value.lower()

    if key in category_map:

        return category_map[key]

    return value.title()


# ============================================================
# CLEAN AMOUNT
# ============================================================

def clean_amount_series(series):

    # Convert everything to string first
    cleaned = series.astype(str)

    # Remove currency symbols
    cleaned = cleaned.str.replace(
        "₹",
        "",
        regex=False
    )

    cleaned = cleaned.str.replace(
        "$",
        "",
        regex=False
    )

    cleaned = cleaned.str.replace(
        "€",
        "",
        regex=False
    )

    cleaned = cleaned.str.replace(
        "£",
        "",
        regex=False
    )

    # Remove commas
    cleaned = cleaned.str.replace(
        ",",
        "",
        regex=False
    )

    # Remove spaces
    cleaned = cleaned.str.replace(
        " ",
        "",
        regex=False
    )

    # Keep numbers, decimal point and minus sign
    cleaned = cleaned.str.replace(
        r"[^0-9.\-]",
        "",
        regex=True
    )

    return pd.to_numeric(
        cleaned,
        errors="coerce"
    )


# ============================================================
# PREPARE CSV
# ============================================================

def prepare_dataframe(file_path):

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    df = pd.read_csv(
        file_path
    )

    if df.empty:

        raise ValueError(
            "The uploaded CSV file is empty."
        )

    # --------------------------------------------------------
    # NORMALIZE COLUMNS
    # --------------------------------------------------------

    df.columns = [
        normalize_column_name(column)
        for column in df.columns
    ]

    # --------------------------------------------------------
    # FIND COLUMNS
    # --------------------------------------------------------

    date_column = find_column(
        df.columns,
        COLUMN_ALIASES["date"]
    )

    description_column = find_column(
        df.columns,
        COLUMN_ALIASES["description"]
    )

    amount_column = find_column(
        df.columns,
        COLUMN_ALIASES["amount"]
    )

    category_column = find_column(
        df.columns,
        COLUMN_ALIASES["category"]
    )

    # --------------------------------------------------------
    # VALIDATE DATE
    # --------------------------------------------------------

    if date_column is None:

        raise ValueError(
            "CSV must contain a date column. "
            "Accepted names: date, transaction_date, datetime."
        )

    # --------------------------------------------------------
    # VALIDATE DESCRIPTION
    # --------------------------------------------------------

    if description_column is None:

        # Create description if unavailable
        df["description"] = "Transaction"

        description_column = "description"

    # --------------------------------------------------------
    # VALIDATE AMOUNT
    # --------------------------------------------------------

    if amount_column is None:

        raise ValueError(
            "CSV must contain an amount column. "
            "Accepted names: amount, expense, debit, withdrawal."
        )

    # --------------------------------------------------------
    # STANDARD DATE COLUMN
    # --------------------------------------------------------

    df["date"] = pd.to_datetime(
        df[date_column],
        errors="coerce"
    )

    # --------------------------------------------------------
    # STANDARD DESCRIPTION
    # --------------------------------------------------------

    df["description"] = (
        df[description_column]
        .apply(clean_text)
    )

    # --------------------------------------------------------
    # STANDARD AMOUNT
    # --------------------------------------------------------

    df["amount"] = clean_amount_series(
        df[amount_column]
    )

    # --------------------------------------------------------
    # REMOVE INVALID DATA
    # --------------------------------------------------------

    df = df.dropna(
        subset=[
            "date",
            "amount"
        ]
    ).copy()

    # --------------------------------------------------------
    # KEEP EXPENSES ONLY
    # --------------------------------------------------------

    df = df[
        df["amount"] > 0
    ].copy()

    if df.empty:

        raise ValueError(
            "No valid positive transactions were found."
        )

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    if category_column is not None:

        df["category"] = (
            df[category_column]
            .apply(clean_category)
        )

        # ----------------------------------------------------
        # FALLBACK ONLY FOR EMPTY CATEGORIES
        # ----------------------------------------------------

        missing_category = (
            df["category"]
            .eq("")
        )

        df.loc[
            missing_category,
            "category"
        ] = (
            df.loc[
                missing_category,
                "description"
            ]
            .apply(assign_category)
        )

    else:

        df["category"] = (
            df["description"]
            .apply(assign_category)
        )

    # --------------------------------------------------------
    # DATE FEATURES
    # --------------------------------------------------------

    df["month"] = (
        df["date"]
        .dt.to_period("M")
        .astype(str)
    )

    df["day"] = (
        df["date"]
        .dt.day
    )

    df["month_number"] = (
        df["date"]
        .dt.month
    )

    df["day_of_week"] = (
        df["date"]
        .dt.dayofweek
    )

    df["day_name"] = (
        df["date"]
        .dt.day_name()
    )

    return df


# ============================================================
# ANOMALY DETECTION
# ============================================================

def detect_anomalies(df):

    amounts = df["amount"]

    # Small datasets need gentler handling
    if len(df) < 4:

        df["anomaly"] = 1

        df["anomaly_status"] = "Normal"

        return df, 0

    Q1 = float(
        amounts.quantile(0.25)
    )

    Q3 = float(
        amounts.quantile(0.75)
    )

    IQR = Q3 - Q1

    # If all transactions are identical
    if IQR == 0:

        df["anomaly"] = 1

        df["anomaly_status"] = "Normal"

        return df, 0

    lower_bound = Q1 - (
        1.5 * IQR
    )

    upper_bound = Q3 + (
        1.5 * IQR
    )

    df["anomaly"] = np.where(

        (
            df["amount"] < lower_bound
        )
        |
        (
            df["amount"] > upper_bound
        ),

        -1,

        1
    )

    df["anomaly_status"] = (
        df["anomaly"]
        .map({
            1: "Normal",
            -1: "Unusual"
        })
    )

    unusual_count = int(
        (
            df["anomaly"] == -1
        ).sum()
    )

    return df, unusual_count


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_transactions(file_path):

    # --------------------------------------------------------
    # PREPARE DATA
    # --------------------------------------------------------

    df = prepare_dataframe(
        file_path
    )

    # --------------------------------------------------------
    # BASIC STATISTICS
    # --------------------------------------------------------

    total_spending = float(
        df["amount"].sum()
    )

    transaction_count = int(
        len(df)
    )

    average_transaction = float(
        df["amount"].mean()
    )

    median_transaction = float(
        df["amount"].median()
    )

    highest_transaction = float(
        df["amount"].max()
    )

    lowest_transaction = float(
        df["amount"].min()
    )

    # --------------------------------------------------------
    # CATEGORY SPENDING
    # --------------------------------------------------------

    category_spending = (
        df.groupby(
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

        highest_category = "Other"

        highest_category_amount = 0.0

    # --------------------------------------------------------
    # CATEGORY PERCENTAGE
    # --------------------------------------------------------

    if total_spending > 0:

        highest_category_percentage = (
            highest_category_amount
            / total_spending
        ) * 100

    else:

        highest_category_percentage = 0.0

    # --------------------------------------------------------
    # ALL CATEGORY PERCENTAGES
    # --------------------------------------------------------

    category_percentages = {}

    for category, amount in category_spending.items():

        percentage = (
            float(amount)
            / total_spending
        ) * 100

        category_percentages[
            str(category)
        ] = round(
            percentage,
            2
        )

    # --------------------------------------------------------
    # DAILY SPENDING
    # --------------------------------------------------------

    daily_spending = (
        df.groupby(
            "day_name"
        )["amount"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    if not daily_spending.empty:

        highest_spending_day = str(
            daily_spending.index[0]
        )

        highest_spending_day_amount = float(
            daily_spending.iloc[0]
        )

    else:

        highest_spending_day = "N/A"

        highest_spending_day_amount = 0.0

    # --------------------------------------------------------
    # MONTHLY SPENDING
    # --------------------------------------------------------

    monthly_spending = (
        df.groupby(
            "month"
        )["amount"]
        .sum()
        .sort_index()
    )

    monthly_spending_dict = {

        str(month):
            round(float(amount), 2)

        for month, amount
        in monthly_spending.items()

    }

    # --------------------------------------------------------
    # ANOMALIES
    # --------------------------------------------------------

    df, unusual_transactions = (
        detect_anomalies(df)
    )

    # --------------------------------------------------------
    # HIGH SPENDING
    #
    # Transactions greater than the average
    # --------------------------------------------------------

    high_spending_transactions = int(

        (
            df["amount"]
            > average_transaction
        ).sum()

    )

    # --------------------------------------------------------
    # TOP TRANSACTIONS
    # --------------------------------------------------------

    top_transactions = (
        df[
            [
                "date",
                "description",
                "amount",
                "category",
                "anomaly_status"
            ]
        ]
        .sort_values(
            "amount",
            ascending=False
        )
        .head(5)
    )

    top_transactions_list = []

    for _, row in top_transactions.iterrows():

        top_transactions_list.append({

            "date":
                row["date"].strftime(
                    "%Y-%m-%d"
                ),

            "description":
                str(
                    row["description"]
                ),

            "amount":
                round(
                    float(row["amount"]),
                    2
                ),

            "category":
                str(
                    row["category"]
                ),

            "status":
                str(
                    row["anomaly_status"]
                )

        })

    # --------------------------------------------------------
    # CATEGORY CHART DATA
    # --------------------------------------------------------

    category_chart_data = []

    for category, amount in category_spending.items():

        category_chart_data.append({

            "category":
                str(category),

            "amount":
                round(
                    float(amount),
                    2
                ),

            "percentage":
                round(
                    (
                        float(amount)
                        / total_spending
                    ) * 100,
                    2
                )

        })

    # --------------------------------------------------------
    # MONTHLY CHART DATA
    # --------------------------------------------------------

    monthly_chart_data = []

    for month, amount in monthly_spending.items():

        monthly_chart_data.append({

            "month":
                str(month),

            "amount":
                round(
                    float(amount),
                    2
                )

        })

    # --------------------------------------------------------
    # DAILY CHART DATA
    # --------------------------------------------------------

    daily_chart_data = []

    for day, amount in daily_spending.items():

        daily_chart_data.append({

            "day":
                str(day),

            "amount":
                round(
                    float(amount),
                    2
                )

        })

    # --------------------------------------------------------
    # TRANSACTION DATA FOR UI
    # --------------------------------------------------------

    transaction_table = []

    for _, row in df.iterrows():

        transaction_table.append({

            "date":
                row["date"].strftime(
                    "%Y-%m-%d"
                ),

            "description":
                str(
                    row["description"]
                ),

            "amount":
                round(
                    float(row["amount"]),
                    2
                ),

            "category":
                str(
                    row["category"]
                ),

            "day":
                str(
                    row["day_name"]
                ),

            "status":
                str(
                    row["anomaly_status"]
                )

        })

    # --------------------------------------------------------
    # FINAL INSIGHTS
    # --------------------------------------------------------

    insights = {

        # Basic
        "total_spending":
            round(
                total_spending,
                2
            ),

        "transaction_count":
            transaction_count,

        "average_transaction":
            round(
                average_transaction,
                2
            ),

        "median_transaction":
            round(
                median_transaction,
                2
            ),

        "highest_transaction":
            round(
                highest_transaction,
                2
            ),

        "lowest_transaction":
            round(
                lowest_transaction,
                2
            ),

        # Category
        "highest_category":
            highest_category,

        "highest_category_amount":
            round(
                highest_category_amount,
                2
            ),

        "highest_category_percentage":
            round(
                highest_category_percentage,
                2
            ),

        "category_percentages":
            category_percentages,

        "category_spending": {

            str(category):
                round(
                    float(amount),
                    2
                )

            for category, amount
            in category_spending.items()

        },

        # Daily
        "highest_spending_day":
            highest_spending_day,

        "highest_spending_day_amount":
            round(
                highest_spending_day_amount,
                2
            ),

        # Monthly
        "monthly_spending":
            monthly_spending_dict,

        # Anomaly
        "unusual_transactions":
            unusual_transactions,

        "high_spending_transactions":
            high_spending_transactions,

        # Tables
        "transactions":
            transaction_table,

        "top_transactions":
            top_transactions_list,

        # Charts
        "category_chart_data":
            category_chart_data,

        "monthly_chart_data":
            monthly_chart_data,

        "daily_chart_data":
            daily_chart_data
    }

    return df, insights


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print(
        "FinSight-AI Analysis Engine"
    )

    print(
        "Import analyze_transactions() "
        "from your Streamlit application."
    )