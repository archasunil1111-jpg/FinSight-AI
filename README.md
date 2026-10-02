# FinSight-AI

**Personal Finance Intelligence Assistant**

FinSight-AI is a privacy-focused personal finance application built with **Python and Streamlit**. It analyzes transaction data, tracks personal financial information, manages recurring bills and financial goals, and provides financial explanations through a **locally running Qwen3:4B model using Ollama**.

The application combines deterministic financial calculations with local AI assistance so that financial values are calculated by the application before being explained by the AI assistant.

## Features

### 📊 Transaction Analysis
- Upload transaction data for analysis
- Calculate financial statistics
- Analyze spending patterns and categories
- Identify high-spending and unusual transactions
- Generate visual summaries of transaction data

### 💰 Financial Overview
- Track monthly income
- Track current savings
- Track monthly savings goals
- Track family support
- Calculate expenses and remaining monthly cash flow

### 🔁 Recurring Bills
- Add and manage recurring monthly expenses
- Store bill category and amount
- Track monthly recurring-bill totals
- Store recurring due dates

### 🎯 Financial Goals
- Create financial goals
- Track current progress toward a target
- Set monthly contribution amounts
- Calculate remaining amounts
- Track goal deadlines

### 💼 Budget & Savings Planning
- Store budget limits
- Manage savings plans
- Keep financial planning data separated from transaction analysis

### 🤖 AI Financial Agent
The application includes a local AI financial assistant that can explain verified financial information related to:

- Spending
- Savings
- Monthly cash flow
- Recurring bills
- Financial goals
- Budget information
- Emergency savings

The application calculates financial values first and provides the verified results to the local AI model for explanation.

### 🔐 Privacy-Focused AI
FinSight-AI uses **Ollama** to run the language model locally.

The AI assistant does not directly access a bank account or perform financial transactions. The application prepares the financial context and uses the local model to explain the calculated results.

## Technology Stack

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

## Project Structure

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
└── README.md
```

Local databases, uploaded user files, temporary files, Python cache files, and virtual-environment files are excluded from the repository through `.gitignore`.

## How It Works

```text
             ┌─────────────────────┐
             │   Streamlit UI      │
             │    frontend/app.py  │
             └──────────┬──────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │   SQLite Database   │
             │ Financial Records   │
             └──────────┬──────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │ Financial Analysis  │
             │ & Verified Values   │
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
             │ Ollama              │
             │ Qwen3:4B            │
             │ Local AI Model      │
             └─────────────────────┘
```

The application follows a simple separation:

**Application → calculates financial values → AI explains the verified results**

This helps keep numerical financial calculations separate from language-model-generated explanations.

## Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/archasunil1111-jpg/FinSight-AI.git
cd FinSight-AI
```

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

If a `requirements.txt` file is present:

```bash
pip install -r requirements.txt
```

Otherwise, install the project's required Python packages according to the imports used by the application.

### 4. Install Ollama

Install Ollama separately and make sure it is available from the terminal.

Check:

```bash
ollama --version
```

### 5. Download Qwen3:4B

```bash
ollama pull qwen3:4b
```

Check the installed models:

```bash
ollama list
```

### 6. Start FinSight-AI

From the project root:

```bash
python -m streamlit run frontend/app.py
```

Streamlit will provide the local web address in the terminal.

## AI Safety & Privacy

FinSight-AI is designed as a **personal finance analysis and learning project**.

- The AI assistant does not connect directly to a bank account.
- The application calculates financial values before sending context to the local AI model.
- Ollama allows the language model to run locally.
- Local databases and uploaded personal financial files are excluded from Git through `.gitignore`.
- The application should not be treated as professional financial advice or a replacement for a financial advisor.

## Exploratory Data Analysis

The project also contains a Jupyter notebook for exploratory analysis:

```text
notebooks/data_analysis.ipynb
```

The notebook is used to explore transaction data and understand spending patterns before integrating analytical functionality into the application.

## Project Purpose

FinSight-AI was developed as a practical project combining:

- Data analysis
- Financial data processing
- SQLite database management
- Streamlit application development
- Local LLM integration
- AI-assisted financial explanations
- Personal financial goal and budget tracking

## Author

**Archa Sunil**

B.Tech Artificial Intelligence & Machine Learning

GitHub: [archasunil1111-jpg](https://github.com/archasunil1111-jpg)

---

**Note:** FinSight-AI is an educational/portfolio project. It does not provide regulated financial advice and does not execute financial transactions.
