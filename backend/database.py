# ==================================================

def add_financial_goal(
    user_id,
    goal_name,
    target_amount,
    current_amount,
    monthly_contribution,
    deadline
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO financial_goals
        (
            user_id,
            goal_name,
            target_amount,
            current_amount,
            monthly_contribution,
            deadline,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        goal_name,
        float(target_amount),
        float(current_amount),
        float(monthly_contribution),
        deadline,
        datetime.now().isoformat()
    ))

    conn.commit()

    goal_id = cursor.lastrowid

    conn.close()

    return goal_id


# ==================================================
# GET FINANCIAL GOALS
# ==================================================

def get_financial_goals(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            goal_name,
            target_amount,
            current_amount,
            monthly_contribution,
            deadline
        FROM financial_goals
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (
        user_id,
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows


# ==================================================
# UPDATE FINANCIAL GOAL
# ==================================================

def update_financial_goal(
    user_id,
    goal_id,
    current_amount,
    monthly_contribution
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE financial_goals

        SET
            current_amount = ?,
            monthly_contribution = ?

        WHERE id = ?

        AND user_id = ?
    """, (
        float(current_amount),
        float(monthly_contribution),
        goal_id,
        user_id
    ))

    conn.commit()

    updated = cursor.rowcount

    conn.close()

    return updated > 0


# ==================================================
# DELETE FINANCIAL GOAL
# ==================================================

def delete_financial_goal(
    user_id,
    goal_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM financial_goals
        WHERE id = ?
        AND user_id = ?
    """, (
        goal_id,
        user_id
    ))

    conn.commit()

    deleted = cursor.rowcount

    conn.close()

    return deleted > 0


# ==================================================
# DATABASE INITIALIZATION
# ==================================================

if __name__ == "__main__":

    create_tables()

    print(
        "Γ£à FinSight-AI database initialized successfully."
    )

    print(
        f"≡ƒôü Database location: {DB_PATH}"
    )
import sqlite3
import hashlib
from datetime import datetime
import os


# ==================================================
# PROJECT / DATABASE PATH
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

os.makedirs(
    DATA_DIR,
    exist_ok=True
)

DB_PATH = os.path.join(
    DATA_DIR,
    "finsight.db"
)


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection():

    conn = sqlite3.connect(DB_PATH)

    return conn


# ==================================================
# PASSWORD HASHING
# ==================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ==================================================
# CREATE TABLES
# ==================================================

def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------
    # USERS
    # --------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
    """)

    # --------------------------------------------------
    # FINANCIAL PROFILE
    # --------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_profiles (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER UNIQUE NOT NULL,

            monthly_income REAL DEFAULT 0,

            current_savings REAL DEFAULT 0,

            family_support REAL DEFAULT 0,

            monthly_savings_goal REAL DEFAULT 0,

            updated_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
            REFERENCES users(id)

        )
    """)

    # --------------------------------------------------
    # TRANSACTIONS
    # --------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            transaction_date TEXT NOT NULL,

            description TEXT NOT NULL,

            amount REAL NOT NULL,

            category TEXT NOT NULL,

            transaction_type TEXT NOT NULL,

            source TEXT DEFAULT 'manual',

            created_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
            REFERENCES users(id)

        )
    """)

    # --------------------------------------------------
    # RECURRING BILLS
    # --------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recurring_bills (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            bill_name TEXT NOT NULL,

            amount REAL NOT NULL,

            category TEXT NOT NULL,

            due_day INTEGER,

            frequency TEXT DEFAULT 'monthly',

            active INTEGER DEFAULT 1,

            created_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
            REFERENCES users(id)

        )
    """)

    # --------------------------------------------------
    # FINANCIAL GOALS
    # --------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_goals (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            goal_name TEXT NOT NULL,

            target_amount REAL NOT NULL,

            current_amount REAL DEFAULT 0,

            monthly_contribution REAL DEFAULT 0,

            deadline TEXT,

            created_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
            REFERENCES users(id)

        )
    """)

    conn.commit()
    conn.close()


# ==================================================
# REGISTER USER
# ==================================================

def register_user(
    name,
    email,
    password
):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        hashed_password = hash_password(password)

        cursor.execute("""
            INSERT INTO users
            (
                name,
                email,
                password,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            hashed_password,
            datetime.now().isoformat()
        ))

        conn.commit()

        user_id = cursor.lastrowid

        conn.close()

        return True, user_id

    except sqlite3.IntegrityError:

        conn.close()

        return False, None


# ==================================================
# LOGIN USER
# ==================================================

def login_user(
    email,
    password
):

    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(password)

    cursor.execute("""
        SELECT
            id,
            name
        FROM users
        WHERE email = ?
        AND password = ?
    """, (
        email,
        hashed_password
    ))

    result = cursor.fetchone()

    conn.close()

    return result


# ==================================================
# GET USER
# ==================================================

def get_user(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            created_at
        FROM users
        WHERE id = ?
    """, (
        user_id,
    ))

    result = cursor.fetchone()

    conn.close()

    return result


# ==================================================
# SAVE FINANCIAL PROFILE
# ==================================================

def save_financial_profile(
    user_id,
    monthly_income,
    current_savings,
    family_support,
    monthly_savings_goal
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO financial_profiles
        (
            user_id,
            monthly_income,
            current_savings,
            family_support,
            monthly_savings_goal,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?)

        ON CONFLICT(user_id)

        DO UPDATE SET

            monthly_income =
                excluded.monthly_income,

            current_savings =
                excluded.current_savings,

            family_support =
                excluded.family_support,

            monthly_savings_goal =
                excluded.monthly_savings_goal,

            updated_at =
                excluded.updated_at

    """, (
        user_id,
        float(monthly_income),
        float(current_savings),
        float(family_support),
        float(monthly_savings_goal),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


# ==================================================
# UPDATE FINANCIAL PROFILE
# ==================================================

def update_financial_profile(
    user_id,
    monthly_income,
    current_savings,
    family_support,
    monthly_savings_goal
):

    save_financial_profile(
        user_id,
        monthly_income,
        current_savings,
        family_support,
        monthly_savings_goal
    )


# ==================================================
# GET FINANCIAL PROFILE
# ==================================================

def get_financial_profile(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            monthly_income,
            current_savings,
            family_support,
            monthly_savings_goal
        FROM financial_profiles
        WHERE user_id = ?
    """, (
        user_id,
    ))

    result = cursor.fetchone()

    conn.close()

    return result


# ==================================================
# ADD TRANSACTION
# DUPLICATE PROTECTION INCLUDED
# ==================================================

def add_transaction(
    user_id,
    transaction_date,
    description,
    amount,
    category,
    transaction_type,
    source="manual"
):

    conn = get_connection()
    cursor = conn.cursor()

    amount = float(amount)

    # --------------------------------------------------
    # CHECK DUPLICATE
    # --------------------------------------------------

    cursor.execute("""
        SELECT id
        FROM transactions
        WHERE user_id = ?
        AND transaction_date = ?
        AND description = ?
        AND amount = ?
        AND category = ?
        AND transaction_type = ?
    """, (
        user_id,
        transaction_date,
        description,
        amount,
        category,
        transaction_type
    ))

    existing = cursor.fetchone()

    if existing:

        conn.close()

        return existing[0], False

    # --------------------------------------------------
    # INSERT TRANSACTION
    # --------------------------------------------------

    cursor.execute("""
        INSERT INTO transactions
        (
            user_id,
            transaction_date,
            description,
            amount,
            category,
            transaction_type,
            source,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        transaction_date,
        description,
        amount,
        category,
        transaction_type,
        source,
        datetime.now().isoformat()
    ))

    conn.commit()

    transaction_id = cursor.lastrowid

    conn.close()

    return transaction_id, True


# ==================================================
# GET USER TRANSACTIONS
# ==================================================

def get_transactions(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            transaction_date,
            description,
            amount,
            category,
            transaction_type,
            source
        FROM transactions
        WHERE user_id = ?
        ORDER BY transaction_date DESC
    """, (
        user_id,
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows


# ==================================================
# DELETE TRANSACTION
# ==================================================

def delete_transaction(
    user_id,
    transaction_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM transactions
        WHERE id = ?
        AND user_id = ?
    """, (
        transaction_id,
        user_id
    ))

    conn.commit()

    deleted = cursor.rowcount

    conn.close()

    return deleted > 0


# ==================================================
# ADD RECURRING BILL
# ==================================================

def add_recurring_bill(
    user_id,
    bill_name,
    amount,
    category,
    due_day,
    frequency="monthly"
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO recurring_bills
        (
            user_id,
            bill_name,
            amount,
            category,
            due_day,
            frequency,
            active,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        bill_name,
        float(amount),
        category,
        due_day,
        frequency,
        1,
        datetime.now().isoformat()
    ))

    conn.commit()

    bill_id = cursor.lastrowid

    conn.close()

    return bill_id


# ==================================================
# GET RECURRING BILLS
# ==================================================

def get_recurring_bills(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            bill_name,
            amount,
            category,
            due_day,
            frequency,
            active
        FROM recurring_bills
        WHERE user_id = ?
        AND active = 1
        ORDER BY
            CASE
                WHEN due_day IS NULL THEN 999
                ELSE due_day
            END
    """, (
        user_id,
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows


# ==================================================
# DEACTIVATE RECURRING BILL
# ==================================================

def deactivate_recurring_bill(
    user_id,
    bill_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE recurring_bills

        SET active = 0

        WHERE id = ?

        AND user_id = ?
    """, (
        bill_id,
        user_id
    ))

    conn.commit()

    updated = cursor.rowcount

    conn.close()

    return updated > 0


# ==================================================
# ADD FINANCIAL GOAL
# ==================================================

def add_financial_goal(
    user_id,
    goal_name,
    target_amount,
    current_amount,
    monthly_contribution,
    deadline
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO financial_goals
        (
            user_id,
            goal_name,
            target_amount,
            current_amount,
            monthly_contribution,
            deadline,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        goal_name,
        float(target_amount),
        float(current_amount),
        float(monthly_contribution),
        deadline,
        datetime.now().isoformat()
    ))

    conn.commit()

    goal_id = cursor.lastrowid

    conn.close()

    return goal_id


# ==================================================
# GET FINANCIAL GOALS
# ==================================================

def get_financial_goals(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            goal_name,
            target_amount,
            current_amount,
            monthly_contribution,
            deadline
        FROM financial_goals
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (
        user_id,
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows


# ==================================================
# UPDATE FINANCIAL GOAL
# ==================================================

def update_financial_goal(
    user_id,
    goal_id,
    current_amount,
    monthly_contribution
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE financial_goals

        SET
            current_amount = ?,
            monthly_contribution = ?

        WHERE id = ?

        AND user_id = ?
    """, (
        float(current_amount),
        float(monthly_contribution),
        goal_id,
        user_id
    ))

    conn.commit()

    updated = cursor.rowcount

    conn.close()

    return updated > 0


# ==================================================
# DELETE FINANCIAL GOAL
# ==================================================

def delete_financial_goal(
    user_id,
    goal_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM financial_goals
        WHERE id = ?
        AND user_id = ?
    """, (
        goal_id,
        user_id
    ))

    conn.commit()

    deleted = cursor.rowcount

    conn.close()

    return deleted > 0


# ==================================================
# DATABASE INITIALIZATION
# ==================================================

if __name__ == "__main__":

    create_tables()

    print(
        "Γ£à FinSight-AI database initialized successfully."
    )

    print(
        f"≡ƒôü Database location: {DB_PATH}"
    )