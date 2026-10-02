# FinSight-AI

**Personal Finance Intelligence Assistant**

FinSight-AI is a privacy-focused personal finance application built with **Python and Streamlit**. It analyzes transaction data, tracks personal financial information, manages recurring bills and financial goals, and provides financial explanations using a **locally running Qwen3:4B model through Ollama**.

The application separates financial calculations from AI-generated explanations. Financial values are calculated by the application first, and the local AI assistant receives the prepared financial context to explain the results.

## ✨ Features

### 📊 Transaction Analysis

- Upload transaction data for analysis
- Calculate financial statistics
- Analyze spending patterns and categories
- Identify high-spending and unusual transactions
- Generate visual summaries of transaction data
- Explore transaction data through a Jupyter notebook

### 💰 Financial Overview

- Track monthly income
- Track current savings
- Track monthly savings goals
- Track family support
- Calculate expenses
- Calculate remaining monthly cash flow

### 🔁 Recurring Bills

- Add recurring monthly expenses
- Store bill categories and amounts
- Track recurring monthly-bill totals
- Store recurring due dates
- View recurring financial commitments separately from transaction analysis

### 🎯 Financial Goals

- Create financial goals
- Set target amounts
- Track current progress
- Set monthly contribution amounts
- Calculate remaining amounts
- Track goal deadlines

### 💼 Budget & Savings Planning

- Store budget limits
- Create and manage savings plans
- Track planned savings contributions
- Keep budgeting and savings information separate from transaction analysis

### 🤖 AI Financial Agent

FinSight-AI includes a local AI financial assistant that can explain prepared financial information related to:

- Spending
- Savings
- Monthly cash flow
- Recurring bills
- Financial goals
- Budget information
- Emergency savings

The application calculates relevant financial values first and then provides the prepared context to the local AI model.

This creates a simple separation:

**Application calculates → Financial Agent prepares context → Local AI explains**

### 🔐 Privacy-Focused AI

FinSight-AI uses **Ollama** to run the language model locally.

The AI assistant:

- Does not directly connect to a bank account
- Does not execute financial transactions
- Does not make payments
- Receives financial context prepared by the application
- Uses a locally running Qwen3:4B model for explanations

Local databases, uploaded user files, temporary files, Python cache files, and virtual-environment files are excluded from Git using `.gitignore`.

---

## 🛠️ Technology Stack

- **Python**
- **Streamlit**
- **Pandas**
- **NumPy**
- **Scikit-learn**
- **SQLite**
- **Ollama**
- **Qwen3:4B**
- **Jupyter Notebook**
- **Git & GitHub**

---

## 📁 Project Structure

```text
FinSight-AI/
│
├── backend/
│   ├── __init__.py
│   ├── analysis.py
│   ├── database.py
│   ├── llm.py
│   ├── ai_advice.py
│   ├── financial_agent.py
│   ├── budget_store.py
│   └── savings_plan_store.py
│
├── data/
│   └── transactions.csv
│
├── frontend/
│   ├── app.py
│   └── bills.py
│
├── notebooks/
│   └── data_analysis.ipynb
│
├── .gitignore
├── requirements.txt
└── README.md
```

### Backend

The `backend` directory contains the application's financial processing and AI-related logic.

- `analysis.py` → transaction and financial analysis
- `database.py` → SQLite database operations
- `llm.py` → local LLM interaction
- `ai_advice.py` → AI-generated financial explanations
- `financial_agent.py` → financial context preparation and AI-agent logic
- `budget_store.py` → budget-related data management
- `savings_plan_store.py` → savings-plan data management
- `__init__.py` → Python package initialization

### Frontend

The `frontend` directory contains the Streamlit interface.

- `app.py` → main application interface
- `bills.py` → recurring-bill functionality

### Data

The `data` directory contains repository-safe sample transaction data.

Local databases and user-specific uploaded financial data are excluded through `.gitignore`.

### Notebook

`notebooks/data_analysis.ipynb` contains exploratory data analysis used to examine transaction data and spending patterns.

---

## 🔄 How It Works

```text
             ┌─────────────────────┐
             │    Streamlit UI     │
             │    frontend/app.py  │
             └──────────┬──────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │   SQLite Database   │
             │   Financial Data    │
             └──────────┬──────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │ Financial Analysis  │
             │  Calculations       │
             └──────────┬──────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │   Financial Agent   │
             │ Context Preparation │
             └──────────┬──────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │       Ollama        │
             │      Qwen3:4B       │
             │     Local Model     │
             └─────────────────────┘
```

The application follows a simple architecture:

**User → Streamlit → Financial calculations → Verified context → Local AI explanation**

The purpose of this separation is to keep numerical financial calculations within the application rather than relying on the language model to perform the underlying calculations.

---

## 🚀 Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/archasunil1111-jpg/FinSight-AI.git
cd FinSight-AI
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

Install the dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

FinSight-AI uses Ollama for local AI processing.

Install Ollama separately and verify that it is available from the terminal:

```bash
ollama --version
```

### 5. Download the Qwen3:4B model

```bash
ollama pull qwen3:4b
```

Check the installed models:

```bash
ollama list
```

### 6. Start the application

From the project root:

```bash
python -m streamlit run frontend/app.py
```

Streamlit will display the local application URL in the terminal.

---

## 📦 Python Dependencies

The main Python dependencies are listed in:

```text
requirements.txt
```

Install them with:

```bash
pip install -r requirements.txt
```

Ollama and the Qwen3:4B model are installed separately because they are local AI infrastructure rather than Python packages.

---

## 🔒 AI Safety & Privacy

FinSight-AI is designed as a **personal finance analysis and learning project**.

Important limitations:

- The application does not connect directly to a bank account.
- The application does not execute financial transactions.
- The application does not make payments.
- The local AI assistant is used for explanations based on application-prepared context.
- Financial calculations are performed by the application before AI explanation.
- Local databases and user-uploaded financial files are excluded from Git.
- The application should not be treated as professional financial advice or a replacement for a qualified financial advisor.

Users should independently verify important financial decisions.

---

## 📓 Exploratory Data Analysis

The project includes a Jupyter notebook:

```text
notebooks/data_analysis.ipynb
```

The notebook is used to explore transaction data, examine spending patterns, and support the development of the application's analytical functionality.

---

## 🎯 Project Purpose

FinSight-AI was developed as a practical project combining:

- Data analysis
- Financial data processing
- SQLite database management
- Streamlit application development
- Local LLM integration
- AI-assisted financial explanations
- Budget tracking
- Savings planning
- Financial goal tracking
- Recurring-bill management

The project demonstrates how traditional application logic and local generative AI can be combined while keeping financial calculations separate from language-model-generated explanations.

---

## 🌱 Future Improvements

Possible future improvements include:

- Improved transaction categorization
- More financial visualizations
- Enhanced budget analytics
- Additional savings-planning features
- More detailed goal tracking
- Improved AI-agent context handling
- Automated testing
- Better error handling and validation
- Deployment support for environments where local Ollama processing is available

---

## ⚠️ Disclaimer

FinSight-AI is an **educational and portfolio project**.

It does not provide regulated financial advice, connect directly to bank accounts, or execute financial transactions. AI-generated explanations should be treated as informational and should not replace professional financial advice.
