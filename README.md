# FinSight-AI

FinSight-AI is a personal finance analysis application that analyzes transaction data, identifies spending patterns and unusual transactions, and generates concise financial insights using a locally running LLM through Ollama.

## Features

- Transaction data analysis
- Spending category analysis
- Detection of high-spending and unusual transactions
- Financial statistics and visualizations
- SQLite database integration
- Streamlit-based user interface
- Local LLM-powered financial advice
- Privacy-focused AI processing using Ollama
- Notebook-based exploratory data analysis

## Technologies

- Python
- Pandas
- NumPy
- Scikit-learn
- SQLite
- Streamlit
- Ollama
- Llama 3.2
- REST APIs
- Jupyter Notebook
- Git & GitHub

## Project Structure

```text
FinSight-AI/
├── backend/
│   ├── analysis.py
│   ├── database.py
│   ├── llm.py
│   └── test_backend.py
├── data/
│   ├── transactions.csv
│   └── uploaded_transactions.csv
├── frontend/
│   └── app.py
├── notebooks/
│   └── data_analysis.ipynb
└── README.md
