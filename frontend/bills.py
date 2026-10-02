import streamlit as st
import sys
import os

# ==================================================
# PATH SETUP
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

BACKEND_DIR = os.path.join(
    BASE_DIR,
    "backend"
)

sys.path.append(BACKEND_DIR)


# ==================================================
# DATABASE IMPORTS
# ==================================================

from database import (
    create_tables,
    add_recurring_bill,
    get_recurring_bills,
    deactivate_recurring_bill
)


# ==================================================
# DATABASE INITIALIZATION
# ==================================================

create_tables()


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Recurring Bills | FinSight-AI",
    page_icon="🔁",
    layout="wide"
)


# ==================================================
# SESSION STATE
# ==================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None


# ==================================================
# LOGIN CHECK
# ==================================================

if not st.session_state.logged_in:

    st.warning(
        "🔐 Please log in through FinSight-AI first."
    )

    st.stop()


# ==================================================
# HEADER
# ==================================================

st.title("🔁 Recurring Bills")

st.subheader(
    f"👋 Welcome, {st.session_state.user_name}"
)

st.write(
    "Manage your regular monthly bills and recurring expenses."
)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.header("💰 FinSight-AI")

    st.write(
        f"👤 **{st.session_state.user_name}**"
    )

    st.divider()

    st.page_link(
        "app.py",
        label="📊 Financial Dashboard",
        icon="📊"
    )

    st.page_link(
        "bills.py",
        label="🔁 Recurring Bills",
        icon="🔁"
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
# ADD NEW BILL
# ==================================================

st.header("➕ Add Recurring Bill")

st.write(
    "Add your regular bills such as rent, internet, "
    "subscriptions, electricity, EMI, or insurance."
)


with st.form("add_bill_form"):

    col1, col2 = st.columns(2)

    with col1:

        bill_name = st.text_input(
            "🧾 Bill Name",
            placeholder="Example: Internet Bill"
        )

        bill_amount = st.number_input(
            "💵 Amount (₹)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            format="%.2f"
        )

        category = st.selectbox(
            "📂 Category",
            [
                "Housing",
                "Utilities",
                "Mobile",
                "Internet",
                "Insurance",
                "Loan/EMI",
                "Entertainment",
                "Education",
                "Medical",
                "Food",
                "Transport",
                "Other"
            ]
        )

    with col2:

        due_day = st.number_input(
            "📅 Due Day",
            min_value=1,
            max_value=31,
            value=1,
            step=1
        )

        frequency = st.selectbox(
            "🔁 Frequency",
            [
                "monthly",
                "weekly",
                "yearly"
            ]
        )

    submitted = st.form_submit_button(
        "💾 Add Bill",
        width="stretch"
    )


# ==================================================
# SAVE BILL
# ==================================================

if submitted:

    if not bill_name.strip():

        st.warning(
            "⚠️ Please enter a bill name."
        )

    elif bill_amount <= 0:

        st.warning(
            "⚠️ Bill amount must be greater than ₹0."
        )

    else:

        try:

            bill_id = add_recurring_bill(
                st.session_state.user_id,
                bill_name.strip(),
                float(bill_amount),
                category,
                int(due_day),
                frequency
            )

            st.success(
                f"✅ {bill_name.strip()} added successfully!"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"❌ Unable to add bill: {e}"
            )


st.divider()


# ==================================================
# GET ACTIVE BILLS
# ==================================================

try:

    bills = get_recurring_bills(
        st.session_state.user_id
    )

except Exception as e:

    st.error(
        f"❌ Unable to load bills: {e}"
    )

    bills = []


# ==================================================
# BILL SUMMARY
# ==================================================

st.header("📊 Bill Summary")


total_monthly_bills = 0.0

monthly_bill_count = 0


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

    amount = float(amount)

    if frequency == "monthly":

        total_monthly_bills += amount
        monthly_bill_count += 1

    elif frequency == "weekly":

        # Approximate monthly equivalent
        total_monthly_bills += amount * 4.33
        monthly_bill_count += 1

    elif frequency == "yearly":

        # Approximate monthly equivalent
        total_monthly_bills += amount / 12
        monthly_bill_count += 1


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "🔁 Active Bills",
        len(bills)
    )


with col2:

    st.metric(
        "💰 Monthly Bill Estimate",
        f"₹{total_monthly_bills:,.2f}"
    )


with col3:

    st.metric(
        "📋 Monthly Bill Count",
        monthly_bill_count
    )


st.divider()


# ==================================================
# ACTIVE BILLS
# ==================================================

st.header("📋 Your Recurring Bills")


if not bills:

    st.info(
        "📭 You don't have any recurring bills yet."
    )

else:

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

        amount = float(amount)

        with st.container(border=True):

            col1, col2, col3, col4 = st.columns(
                [2.5, 1.5, 1.5, 1]
            )

            with col1:

                st.subheader(
                    f"🧾 {bill_name}"
                )

                st.caption(
                    f"📂 {category}"
                )

            with col2:

                st.write("💵 **Amount**")

                st.write(
                    f"₹{amount:,.2f}"
                )

            with col3:

                st.write("📅 **Due**")

                st.write(
                    f"Day {due_day}"
                )

                st.caption(
                    frequency.capitalize()
                )

            with col4:

                st.write("")

                if st.button(
                    "🗑️ Deactivate",
                    key=f"delete_bill_{bill_id}",
                    width="stretch"
                ):

                    try:

                        success = deactivate_recurring_bill(
                            st.session_state.user_id,
                            bill_id
                        )

                        if success:

                            st.success(
                                "Bill deactivated."
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Unable to deactivate bill."
                            )

                    except Exception as e:

                        st.error(
                            f"❌ Error: {e}"
                        )


st.divider()


# ==================================================
# MONTHLY BILL BREAKDOWN
# ==================================================

st.header("💰 Monthly Bill Breakdown")


if bills:

    monthly_data = []

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

        amount = float(amount)

        if frequency == "monthly":

            monthly_amount = amount

        elif frequency == "weekly":

            monthly_amount = amount * 4.33

        else:

            monthly_amount = amount / 12

        monthly_data.append({
            "Bill": bill_name,
            "Category": category,
            "Frequency": frequency.capitalize(),
            "Monthly Estimate": monthly_amount
        })

    st.dataframe(
        monthly_data,
        width="stretch",
        hide_index=True
    )

    st.info(
        f"💡 Estimated recurring monthly expenses: "
        f"**₹{total_monthly_bills:,.2f}**"
    )

else:

    st.info(
        "Add a recurring bill to see your monthly breakdown."
    )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "💰 FinSight-AI | Recurring Bills Management"
)