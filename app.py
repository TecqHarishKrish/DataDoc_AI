import os
import json
import streamlit as st
import sqlite3

from backend.metadata_extractor import extract_metadata
from backend.quality_engine import analyze_quality
from backend.ai_summarizer import generate_table_summary

BASE_DIR = os.path.dirname(__file__)
METADATA_DIR = os.path.join(BASE_DIR, "metadata")
AI_DOCS_DIR = os.path.join(BASE_DIR, "ai_docs")
DB_PATH = os.path.join(BASE_DIR, "datadoc_demo.db")

# ----------------- EXISTING HELPERS -----------------

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def get_table_list():
    return [
        f.replace(".json", "")
        for f in os.listdir(METADATA_DIR)
        if f.endswith(".json") and not f.endswith("_quality.json")
    ]

def get_relationships():
    return {
        "customers": ["orders"],
        "orders": ["customers", "payments"],
        "payments": ["orders"]
    }

def get_sql_suggestion(query_type):
    templates = {
        "monthly_revenue": """
SELECT strftime('%Y-%m', order_date) AS month,
       SUM(total_amount) AS revenue
FROM orders
GROUP BY 1
ORDER BY 1;
""",
        "top_customers": """
SELECT c.name, SUM(o.total_amount) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.name
ORDER BY total_spent DESC;
"""
    }
    return templates.get(query_type, "No template available for this request.")

def add_hint_question(q):
    st.session_state.messages.append({"role": "user", "content": q})
    st.session_state.triggered_hint = q

# ----------------- DIRECT DB QUERY HELPERS -----------------

def run_query(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def email_completeness():
    rows = run_query("""
        SELECT COUNT(email), COUNT(*)
        FROM customers
    """)
    non_null, total = rows[0]
    return round((non_null / total) * 100, 2), total, total - non_null

def customers_by_city():
    return run_query("""
        SELECT city, COUNT(*) AS cnt
        FROM customers
        GROUP BY city
        ORDER BY cnt DESC
    """)

def top_customers_by_spend():
    return run_query("""
        SELECT c.customer_id, c.name, SUM(o.total_amount) AS total_spent
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.name
        ORDER BY total_spent DESC
        LIMIT 5
    """)

def customers_with_no_orders():
    return run_query("""
        SELECT c.customer_id, c.name
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.order_id IS NULL
    """)

def customers_with_failed_payments():
    return run_query("""
        SELECT DISTINCT c.customer_id, c.name
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN payments p ON o.order_id = p.order_id
        WHERE p.payment_status = 'FAILED'
    """)

def customers_with_pending_payments():
    return run_query("""
        SELECT DISTINCT c.customer_id, c.name
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN payments p ON o.order_id = p.order_id
        WHERE p.payment_status = 'PENDING'
    """)

def revenue_by_city():
    return run_query("""
        SELECT o.shipping_address, SUM(o.total_amount) AS revenue
        FROM orders o
        WHERE o.shipping_address IS NOT NULL
        GROUP BY o.shipping_address
        ORDER BY revenue DESC
    """)

def highest_spender():
    return run_query("""
        SELECT c.customer_id, c.name, SUM(o.total_amount) AS total_spent
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.name
        ORDER BY total_spent DESC
        LIMIT 1
    """)

def bangalore_vs_chennai():
    rows = run_query("""
        SELECT 
            SUM(CASE WHEN o.shipping_address='Bangalore' THEN o.total_amount ELSE 0 END) AS blr,
            SUM(CASE WHEN o.shipping_address='Chennai' THEN o.total_amount ELSE 0 END) AS chn
        FROM orders o
    """)
    return rows[0]

# ----------------- UI CONFIG -----------------

st.set_page_config(
    page_title="DataDoc AI",
    layout="wide",
    page_icon="🤖"
)
# --------- DARK / LIGHT MODE TOGGLE ---------

def apply_theme(dark_mode):
    if dark_mode:
        st.markdown("""
        <style>
        body, .stApp {
            background-color: #0E1117;
            color: white;
        }
        .stChatMessage[data-testid="chat-message-user"] {
            background-color: #1E293B;
            color: white;
        }
        .stChatMessage[data-testid="chat-message-assistant"] {
            background-color: #111827;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        body, .stApp {
            background-color: white;
            color: black;
        }
        .stChatMessage[data-testid="chat-message-user"] {
            background-color: #E3F2FD;
            color: black;
        }
        .stChatMessage[data-testid="chat-message-assistant"] {
            background-color: #F5F5F5;
            color: black;
        }
        </style>
        """, unsafe_allow_html=True)

st.markdown("""
<style>
.stChatMessage {
    border-radius: 12px;
    padding: 10px;
}
.stChatMessage[data-testid="chat-message-user"] {
    background-color: #E3F2FD;
}
.stChatMessage[data-testid="chat-message-assistant"] {
    background-color: #F5F5F5;
}
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------

with st.sidebar:
    st.header("⚙️ Controls")

    if st.button("🔄 Refresh Metadata & Quality"):
        with st.spinner("Re-extracting metadata and recomputing quality..."):
            extract_metadata()
            analyze_quality()
        st.success("✅ Refreshed successfully!")

    st.divider()

    st.subheader("📚 Available Tables")
    tables = get_table_list()
    for t in tables:
        st.write(f"• **{t}**")

    st.divider()

    st.subheader("💡 Hint Questions")
    hint_questions = [
        "Explain the customers table in simple terms",
        "What kind of information is stored about each customer?",
        "Which column uniquely identifies a customer?",
        "Which customers are from Chennai?",
        "Which customer columns have missing values?",
        "How complete is the email column in customers?",
        "Which city has the most customers?",
        "Who are the most valuable customers based on their orders?",
        "Which customers have not placed any orders?",
        "List customers with failed payments",
        "Which customer city generates the most revenue?",
        "Which customer has the highest total spending?",
        "Are customers from Bangalore spending more than Chennai?",
        "Explain like I'm 5"
    ]

    for q in hint_questions:
        if st.button(q):
            add_hint_question(q)

    st.divider()

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.experimental_rerun()

# ----------------- MAIN UI -----------------

st.title("🤖 DataDoc AI — Intelligent Data Dictionary")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I’m DataDoc AI. Ask me anything about your database 😊"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ----------------- CHAT INPUT -----------------

user_query = st.chat_input("Ask about your database...")

if "triggered_hint" in st.session_state:
    user_query = st.session_state.pop("triggered_hint")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})

    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):
            answer = ""        # ✅ ALWAYS define answer
            q = user_query.lower()

            # --------- EXACT ANSWERS FOR ALL HINT QUESTIONS ---------

            if "how complete is the email" in q:
                pct, total, missing = email_completeness()
                answer = (
                    f"📊 **Email Completeness in customers**\n\n"
                    f"- Total customers: {total}\n"
                    f"- Missing emails: {missing}\n"
                    f"- ✅ Completeness: **{pct}%**"
                )

            elif "which customer columns have missing" in q:
                rows = run_query("""
                    SELECT customer_id, name
                    FROM customers
                    WHERE email IS NULL
                """)
                answer = "📌 **Columns with missing values in customers:**\n\n"
                answer += "- **email** (missing for these customers):\n"
                for cid, name in rows:
                    answer += f"  • {cid} — {name}\n"

            elif "which city has the most customers" in q:
                rows = customers_by_city()
                city, count = rows[0]
                answer = f"🏙️ **City with most customers:** **{city} ({count})**"

            elif "most valuable customers" in q or "top customers" in q:
                rows = top_customers_by_spend()
                answer = "🏆 **Top customers by spending:**\n"
                for cid, name, spend in rows:
                    answer += f"- {name} (ID {cid}) — ₹{spend}\n"

            elif "which customers have not placed any orders" in q:
                rows = customers_with_no_orders()
                answer = "🚫 **Customers with NO orders:**\n"
                for cid, name in rows:
                    answer += f"- {name} (ID {cid})\n"

            elif "failed payments" in q:
                rows = customers_with_failed_payments()
                answer = "❌ **Customers with FAILED payments:**\n"
                for cid, name in rows:
                    answer += f"- {name} (ID {cid})\n"

            elif "pending payments" in q:
                rows = customers_with_pending_payments()
                answer = "⏳ **Customers with PENDING payments:**\n"
                for cid, name in rows:
                    answer += f"- {name} (ID {cid})\n"

            elif "which customer city generates the most revenue" in q:
                rows = revenue_by_city()
                city, rev = rows[0]
                answer = f"💰 **Top revenue city:** **{city} — ₹{rev}**"

            elif "which customer has the highest total spending" in q:
                cid, name, spend = highest_spender()[0]
                answer = f"🏆 **Highest spender:** {name} (ID {cid}) — ₹{spend}"

            elif "bangalore" in q and "chennai" in q:
                blr, chn = bangalore_vs_chennai()
                winner = "Bangalore" if blr > chn else "Chennai"
                answer = (
                    f"📊 **Bangalore vs Chennai spending:**\n"
                    f"- Bangalore: ₹{blr}\n"
                    f"- Chennai: ₹{chn}\n\n"
                    f"👉 **Winner: {winner}**"
                )

            elif "which column uniquely identifies a customer" in q:
                answer = (
                    "🔑 **Primary Key of customers table**\n\n"
                    "- The column that uniquely identifies each customer is: **customer_id**.\n"
                    "- It is the **Primary Key** and is used to join with `orders` and `payments`."
                )

            elif "which customers are from chennai" in q:
                rows = run_query("""
                    SELECT customer_id, name
                    FROM customers
                    WHERE city = 'Chennai'
                """)
                answer = "📍 **Customers from Chennai:**\n"
                for cid, name in rows:
                    answer += f"- {name} (ID {cid})\n"

            # --------- EXISTING BEHAVIOR (UNCHANGED) ---------

            elif "explain" in q:
                for table in tables:
                    if table in q:
                        md_path = os.path.join(AI_DOCS_DIR, f"{table}.md")
                        if os.path.exists(md_path):
                            with open(md_path, "r", encoding="utf-8") as f:
                                answer = f.read()
                        else:
                            answer = generate_table_summary(table)
                        break
                else:
                    answer = "Please mention a valid table (customers, orders, or payments)."

            elif "quality" in q or "null" in q or "missing" in q:
                results = analyze_quality()
                answer = "📊 **Latest Data Quality Summary:**\n\n"
                for table, ql in results.items():
                    worst_col = min(
                        ql["column_completeness"].items(),
                        key=lambda x: x[1]["completeness_percent"],
                    )
                    answer += (
                        f"**{table}** → {ql['total_rows']} rows | "
                        f"Worst column: `{worst_col[0]}` "
                        f"({worst_col[1]['completeness_percent']}% complete)\n"
                    )

            elif "related" in q or "lineage" in q:
                rel = get_relationships()
                answer = ""
                for table in tables:
                    if table in q:
                        answer = f"🔗 Tables related to **{table}**: {', '.join(rel.get(table, []))}"
                        break
                if not answer:
                    answer = "Mention a table to see its relationships."

            elif "sql" in q or "query" in q:
                if "revenue" in q:
                    answer = "Here is a suggested SQL query for monthly revenue:\n```sql\n" \
                              + get_sql_suggestion("monthly_revenue") + "\n```"
                elif "top" in q:
                    answer = "Here is a suggested SQL query for top customers:\n```sql\n" \
                              + get_sql_suggestion("top_customers") + "\n```"
                else:
                    answer = "Ask specifically: 'monthly revenue' or 'top customers'."

            elif "explain like i'm 5" in q:
                answer = (
                    "Think of your database like a big notebook:\n"
                    "- **customers** = people who buy things\n"
                    "- **orders** = what they bought\n"
                    "- **payments** = how they paid"
                )

            else:
                answer = (
                    "I can help with:\n"
                    "- Explain a table (e.g., 'Explain orders')\n"
                    "- Data quality (e.g., 'Show quality issues')\n"
                    "- Relationships (e.g., 'What is related to orders?')\n"
                    "- SQL (e.g., 'Give monthly revenue SQL')\n"
                    "- Or say: 'Explain like I'm 5'"
                )

            st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
