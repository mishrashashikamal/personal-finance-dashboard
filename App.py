import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")
st.title("💰 Personal Finance Dashboard")

DB_FILE = "finance.db"

def init_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS income (id INTEGER PRIMARY KEY, date TEXT, source TEXT, amount REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, date TEXT, category TEXT, description TEXT, amount REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS savings_goals (id INTEGER PRIMARY KEY, name TEXT, target_amount REAL, current_amount REAL, deadline TEXT)''')
    conn.commit()
    conn.close()

init_database()

def add_income(date, source, amount):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO income (date, source, amount) VALUES (?, ?, ?)", (date, source, amount))
    conn.commit()
    conn.close()

def add_expense(date, category, description, amount):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)", (date, category, description, amount))
    conn.commit()
    conn.close()

def get_income():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM income", conn)
    conn.close()
    return df

def get_expenses():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM expenses", conn)
    conn.close()
    return df

def get_total_income():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM income")
    total = cursor.fetchone()[0] or 0
    conn.close()
    return total

def get_total_expenses():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0] or 0
    conn.close()
    return total

tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "💵 Add Income", "💸 Add Expense", "🎯 Savings Goals"])

with tab1:
    st.header("Dashboard Overview")
    total_income = get_total_income()
    total_expenses = get_total_expenses()
    balance = total_income - total_expenses
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Income", f"₹{total_income:,.2f}")
    with col2:
        st.metric("Total Expenses", f"₹{total_expenses:,.2f}")
    with col3:
        st.metric("Balance", f"₹{balance:,.2f}")
    
    st.write("---")
    
    income_df = get_income()
    expenses_df = get_expenses()
    
    col1, col2 = st.columns(2)
    with col1:
        if not income_df.empty:
            st.subheader("Income by Source")
            income_chart = income_df.groupby('source')['amount'].sum()
            fig_income = px.pie(values=income_chart.values, names=income_chart.index, title="Income Distribution")
            st.plotly_chart(fig_income, use_container_width=True)
        else:
            st.info("No income data yet")
    
    with col2:
        if not expenses_df.empty:
            st.subheader("Expenses by Category")
            expense_chart = expenses_df.groupby('category')['amount'].sum()
            fig_expense = px.pie(values=expense_chart.values, names=expense_chart.index, title="Expense Distribution")
            st.plotly_chart(fig_expense, use_container_width=True)
        else:
            st.info("No expense data yet")

with tab2:
    st.header("Add Income")
    with st.form("income_form"):
        date = st.date_input("Date", value=datetime.now())
        source = st.selectbox("Income Source", ["Salary", "Freelance", "Investment", "Bonus", "Other"])
        amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
        if st.form_submit_button("Add Income"):
            add_income(str(date), source, amount)
            st.success(f"✓ Added ₹{amount} from {source}")
            st.rerun()

with tab3:
    st.header("Add Expense")
    with st.form("expense_form"):
        date = st.date_input("Date", value=datetime.now())
        category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Utilities", "Shopping", "Health", "Education", "Other"])
        description = st.text_input("Description", placeholder="e.g., Groceries")
        amount = st.number_input("Amount (₹)", min_value=0.0, step=50.0)
        if st.form_submit_button("Add Expense"):
            add_expense(str(date), category, description, amount)
            st.success(f"✓ Added expense: ₹{amount}")
            st.rerun()

with tab4:
    st.header("Savings Goals")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add Goal")
        with st.form("goal_form"):
            goal_name = st.text_input("Goal Name", placeholder="e.g., Vacation")
            target = st.number_input("Target Amount (₹)", min_value=0.0)
            current = st.number_input("Current Savings (₹)", min_value=0.0)
            deadline = st.date_input("Target Deadline")
            if st.form_submit_button("Add Goal"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO savings_goals (name, target_amount, current_amount, deadline) VALUES (?, ?, ?, ?)''', (goal_name, target, current, str(deadline)))
                conn.commit()
                conn.close()
                st.success(f"✓ Goal added!")
                st.rerun()
    
    with col2:
        st.subheader("Your Goals")
        conn = sqlite3.connect(DB_FILE)
        goals_df = pd.read_sql_query("SELECT * FROM savings_goals", conn)
        conn.close()
        if not goals_df.empty:
            for _, goal in goals_df.iterrows():
                progress = (goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
                st.write(f"**{goal['name']}**")
                st.progress(min(progress / 100, 1.0))
                st.write(f"₹{goal['current_amount']:,.0f} / ₹{goal['target_amount']:,.0f}")
        else:
            st.info("No goals yet")