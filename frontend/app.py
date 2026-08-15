import streamlit as st
import sys
import os

# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

sys.path.append(BACKEND_DIR)

from analysis import analyze_transactions
from llm import generate_financial_advice

from database import (
    create_tables,
    register_user,
    login_user,
    get_financial_profile,
    update_financial_profile
)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

create_tables()


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="FinSight-AI",
    page_icon="💰",
    layout="wide"
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None


# --------------------------------------------------
# LOGIN / SIGN UP
# --------------------------------------------------

if not st.session_state.logged_in:

    st.title("💰 FinSight-AI")

    st.subheader(
        "Personal Financial Analysis Assistant"
    )

    st.write(
        "Analyze your income, savings, expenses, family support, "
        "and financial goals with AI-powered recommendations."
    )

    login_tab, signup_tab = st.tabs(
        ["🔐 Login", "📝 Sign Up"]
    )

    # --------------------------------------------------
    # LOGIN
    # --------------------------------------------------

    with login_tab:

        st.header("🔐 Login")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            width="stretch"
        ):

            if not email or not password:

                st.warning(
                    "Please enter both email and password."
                )

            else:

                user = login_user(
                    email.strip(),
                    password
                )

                if user:

                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.user_name = user[1]

                    st.success(
                        "✅ Login successful!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "❌ Invalid email or password."
                    )

    # --------------------------------------------------
    # SIGN UP
    # --------------------------------------------------

    with signup_tab:

        st.header("📝 Create Account")

        name = st.text_input(
            "Full Name",
            key="signup_name"
        )

        email = st.text_input(
            "Email",
            key="signup_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="signup_confirm"
        )

        if st.button(
            "Create Account",
            width="stretch"
        ):

            if not name or not email or not password:

                st.warning(
                    "Please fill in all fields."
                )

            elif password != confirm_password:

                st.error(
                    "❌ Passwords do not match."
                )

            elif len(password) < 6:

                st.error(
                    "❌ Password must contain at least 6 characters."
                )

            else:

                success, user_id = register_user(
                    name.strip(),
                    email.strip(),
                    password
                )

                if success:

                    st.success(
                        "✅ Account created successfully! "
                        "You can now log in."
                    )

                else:

                    st.error(
                        "❌ An account with this email already exists."
                    )

    st.stop()


# ==================================================
# LOGGED-IN DASHBOARD
# ==================================================

st.title("💰 FinSight-AI")

st.subheader(
    f"👋 Welcome, {st.session_state.user_name}"
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("👤 Account")

    st.write(
        f"**User:** {st.session_state.user_name}"
    )

    st.divider()

    if st.button(
        "🚪 Logout",
        width="stretch"
    ):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = None

        st.rerun()


# ==================================================
# PERSONAL FINANCE INFORMATION
# ==================================================

st.header("💵 Personal Finance Information")

st.write(
    "Enter your current financial information. "
    "FinSight-AI will use this together with your transaction data "
    "to calculate your available money and savings position."
)


# --------------------------------------------------
# GET SAVED PROFILE
# --------------------------------------------------

profile = get_financial_profile(
    st.session_state.user_id
)


if profile:

    old_income = float(profile[0] or 0.0)
    old_savings = float(profile[1] or 0.0)
    old_family = float(profile[2] or 0.0)
    old_goal = float(profile[3] or 0.0)

else:

    # IMPORTANT:
    # Keep all values as FLOATS.
    # Streamlit requires value/min_value/step
    # to use the same numeric type.

    old_income = 0.0
    old_savings = 0.0
    old_family = 0.0
    old_goal = 0.0


# --------------------------------------------------
# FINANCIAL INPUTS
# --------------------------------------------------

col1, col2 = st.columns(2)


with col1:

    monthly_income = st.number_input(
        "💵 Monthly Income (₹)",
        min_value=0.0,
        value=old_income,
        step=100.0,
        format="%.2f"
    )

    current_savings = st.number_input(
        "🏦 Current Savings (₹)",
        min_value=0.0,
        value=old_savings,
        step=100.0,
        format="%.2f"
    )


with col2:

    family_support = st.number_input(
        "👨‍👩‍👧 Money Given to Family This Month (₹)",
        min_value=0.0,
        value=old_family,
        step=100.0,
        format="%.2f"
    )

    savings_goal = st.number_input(
        "🎯 Monthly Savings Goal (₹)",
        min_value=0.0,
        value=old_goal,
        step=100.0,
        format="%.2f"
    )


# --------------------------------------------------
# SAVE PROFILE
# --------------------------------------------------

if st.button(
    "💾 Save Financial Information",
    width="stretch"
):

    update_financial_profile(
        st.session_state.user_id,
        float(monthly_income),
        float(current_savings),
        float(family_support),
        float(savings_goal)
    )

    st.success(
        "✅ Financial information saved."
    )


st.divider()


# ==================================================
# TRANSACTION DATA
# ==================================================

st.header("📁 Transaction Data")

st.write(
    "Upload your transaction CSV file to analyze your spending."
)


uploaded_file = st.file_uploader(
    "Upload your transactions CSV",
    type=["csv"]
)


# ==================================================
# CSV ANALYSIS
# ==================================================

if uploaded_file is not None:

    # --------------------------------------------------
    # SAVE FILE
    # --------------------------------------------------

    data_dir = os.path.join(
        BASE_DIR,
        "data"
    )

    os.makedirs(
        data_dir,
        exist_ok=True
    )

    temp_file = os.path.join(
        data_dir,
        "uploaded_transactions.csv"
    )


    with open(
        temp_file,
        "wb"
    ) as f:

        f.write(
            uploaded_file.getbuffer()
        )


    # --------------------------------------------------
    # ANALYZE
    # --------------------------------------------------

    try:

        df, insights = analyze_transactions(
            temp_file
        )

        st.success(
            "✅ Transaction analysis completed!"
        )

    except Exception as e:

        st.error(
            f"❌ Unable to analyze the CSV file: {e}"
        )

        st.stop()


    # ==================================================
    # FINANCIAL CALCULATIONS
    # ==================================================

    total_expenses = float(
        insights.get(
            "total_spending",
            0.0
        )
    )


    remaining_money = (
        float(monthly_income)
        - total_expenses
        - float(family_support)
    )


    savings_difference = (
        remaining_money
        - float(savings_goal)
    )


    # ==================================================
    # FINANCIAL OVERVIEW
    # ==================================================

    st.header("💰 Financial Overview")

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "💵 Monthly Income",
            f"₹{float(monthly_income):,.2f}"
        )


    with col2:

        st.metric(
            "💳 Expenses",
            f"₹{total_expenses:,.2f}"
        )


    with col3:

        st.metric(
            "👨‍👩‍👧 Family Support",
            f"₹{float(family_support):,.2f}"
        )


    with col4:

        st.metric(
            "💰 Remaining",
            f"₹{remaining_money:,.2f}"
        )


    # ==================================================
    # SAVINGS OVERVIEW
    # ==================================================

    st.header("🏦 Savings Overview")

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Current Savings",
            f"₹{float(current_savings):,.2f}"
        )


    with col2:

        st.metric(
            "Monthly Savings Goal",
            f"₹{float(savings_goal):,.2f}"
        )


    with col3:

        if savings_difference >= 0:

            st.success(
                f"✅ Savings Goal On Track\n\n"
                f"Available above goal: "
                f"₹{savings_difference:,.2f}"
            )

        else:

            st.error(
                f"⚠️ Savings Goal Shortfall\n\n"
                f"Amount needed: "
                f"₹{abs(savings_difference):,.2f}"
            )


    st.divider()


    # ==================================================
    # FINANCIAL INSIGHTS
    # ==================================================

    st.header("📊 Financial Insights")


    col1, col2 = st.columns(2)


    with col1:

        st.write(
            f"**Highest Spending Category:** "
            f"{insights.get('highest_category', 'N/A')}"
        )

        st.write(
            f"**Amount Spent:** "
            f"₹{float(insights.get('highest_category_amount', 0.0)):,.2f}"
        )

        st.write(
            f"**Unusual Transactions:** "
            f"{int(insights.get('unusual_transactions', 0))}"
        )


    with col2:

        st.write(
            f"**High-Spending Transactions:** "
            f"{int(insights.get('high_spending_transactions', 0))}"
        )

        st.write(
            f"**Category Share:** "
            f"{float(insights.get('highest_category_percentage', 0.0)):.1f}%"
        )


    # ==================================================
    # SPENDING SUMMARY
    # ==================================================

    st.header("📈 Spending Summary")


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "💰 Total Spending",
            f"₹{total_expenses:,.2f}"
        )


    with col2:

        st.metric(
            "🧾 Average Transaction",
            f"₹{float(insights.get('average_transaction', 0.0)):,.2f}"
        )


    with col3:

        st.metric(
            "🏆 Highest Category",
            insights.get(
                "highest_category",
                "N/A"
            )
        )


    with col4:

        st.metric(
            "📊 Category Share",
            f"{float(insights.get('highest_category_percentage', 0.0)):.1f}%"
        )


    # ==================================================
    # TRANSACTIONS
    # ==================================================

    st.header("📋 Transactions")


    st.dataframe(
        df,
        width="stretch"
    )


    st.divider()


    # ==================================================
    # AI FINANCIAL ADVICE
    # ==================================================

    st.header("🤖 AI Financial Advice")

    st.caption(
        "Llama 3.2 analyzes your spending data "
        "and generates personalized financial suggestions."
    )


    try:

        with st.spinner(
            "🤖 Llama is analyzing your spending..."
        ):

            advice = generate_financial_advice(
                insights
            )

        st.write(advice)

    except Exception as e:

        st.warning(
            f"⚠️ AI advice could not be generated: {e}"
        )


# ==================================================
# NO CSV
# ==================================================

else:

    st.info(
        "📁 Upload a CSV file to begin financial analysis."
    )