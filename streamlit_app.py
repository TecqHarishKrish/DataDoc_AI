import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Backend API URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ----------------- UI CONFIG -----------------
st.set_page_config(
    page_title="DataDoc AI",
    layout="wide",
    page_icon="🤖"
)

# Custom CSS for better styling
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

# ----------------- API HELPER FUNCTIONS -----------------
def get_tables():
    """Fetch tables from backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/tables")
        if response.status_code == 200:
            return response.json().get("tables", [])
        else:
            st.error(f"Failed to fetch tables: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return []

def get_table_metadata(table_name):
    """Fetch table metadata from backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/tables/{table_name}/metadata")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch metadata: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching metadata: {str(e)}")
        return None

def get_table_quality(table_name):
    """Fetch table quality metrics from backend API"""
    try:
        response = requests.get(f"{BACKEND_URL}/tables/{table_name}/quality")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch quality metrics: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching quality metrics: {str(e)}")
        return None

def generate_table_summary(table_name):
    """Generate AI summary for table"""
    try:
        response = requests.post(f"{BACKEND_URL}/tables/{table_name}/summary")
        if response.status_code == 200:
            return response.json().get("summary", "")
        else:
            st.error(f"Failed to generate summary: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

def refresh_metadata():
    """Refresh metadata for all tables"""
    try:
        response = requests.post(f"{BACKEND_URL}/refresh-metadata")
        if response.status_code == 200:
            return response.json().get("message", "")
        else:
            st.error(f"Failed to refresh metadata: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error refreshing metadata: {str(e)}")
        return None

def refresh_quality():
    """Refresh quality metrics for all tables"""
    try:
        response = requests.post(f"{BACKEND_URL}/refresh-quality")
        if response.status_code == 200:
            return response.json().get("message", "")
        else:
            st.error(f"Failed to refresh quality: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error refreshing quality: {str(e)}")
        return None

def check_backend_health():
    """Check if backend is healthy"""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.header("⚙️ Controls")
    
    # Check backend health
    health = check_backend_health()
    if health:
        st.success("✅ Backend Connected")
        st.info(f"Database: {health.get('database', 'Unknown')}")
    else:
        st.error("❌ Backend Disconnected")
        st.info("Make sure backend is running")
    
    st.divider()
    
    # Refresh buttons
    if st.button("🔄 Refresh Metadata"):
        with st.spinner("Refreshing metadata..."):
            result = refresh_metadata()
            if result:
                st.success(result)
    
    if st.button("🔄 Refresh Quality"):
        with st.spinner("Refreshing quality metrics..."):
            result = refresh_quality()
            if result:
                st.success(result)
    
    st.divider()
    
    # Tables list
    st.subheader("📚 Available Tables")
    tables = get_tables()
    if tables:
        selected_table = st.selectbox("Select a table:", tables)
    else:
        st.warning("No tables found")
        selected_table = None
    
    st.divider()
    
    # Hint questions
    st.subheader("💡 Quick Actions")
    if selected_table:
        if st.button(f"📖 Explain {selected_table}"):
            st.session_state.show_explanation = selected_table
        if st.button(f"📊 Quality Report for {selected_table}"):
            st.session_state.show_quality = selected_table
        if st.button(f"🤖 AI Summary for {selected_table}"):
            st.session_state.generate_summary = selected_table
    
    if st.button("🧹 Clear Cache"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# ----------------- MAIN UI -----------------
st.title("🤖 DataDoc AI — Intelligent Data Dictionary")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm DataDoc AI. Select a table from the sidebar to explore your database 😊"}
    ]

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Handle auto-actions from sidebar buttons
if selected_table:
    # Show table explanation
    if st.session_state.get("show_explanation") == selected_table:
        with st.chat_message("assistant"):
            with st.spinner(f"Analyzing {selected_table}..."):
                metadata = get_table_metadata(selected_table)
                if metadata:
                    explanation = f"""
## 📋 Table: {selected_table.upper()}

**Row Count:** {metadata.get('row_count', 'N/A')}

### 🔑 Primary Keys
{', '.join(metadata.get('primary_keys', [])) if metadata.get('primary_keys') else 'None'}

### 📊 Columns
| Column | Type | Nullable | Max Length |
|--------|------|----------|------------|
"""
                    for col in metadata.get('columns', []):
                        explanation += f"| {col['column_name']} | {col['data_type']} | {col['is_nullable']} | {col.get('max_length', 'N/A')} |\n"
                    
                    st.write(explanation)
                    st.session_state.messages.append({"role": "assistant", "content": explanation})
        
        st.session_state.show_explanation = None
    
    # Show quality report
    elif st.session_state.get("show_quality") == selected_table:
        with st.chat_message("assistant"):
            with st.spinner(f"Analyzing quality for {selected_table}..."):
                quality = get_table_quality(selected_table)
                if quality:
                    report = f"""
## 📊 Data Quality Report: {selected_table.upper()}

**Total Rows:** {quality.get('total_rows', 'N/A')}

### 📈 Column Completeness
| Column | Complete | Missing | % Complete |
|--------|----------|---------|------------|
"""
                    for col_name, metrics in quality.get('column_completeness', {}).items():
                        complete = metrics['non_null_count']
                        missing = metrics['total_count'] - complete
                        percent = metrics['completeness_percent']
                        report += f"| {col_name} | {complete} | {missing} | {percent}% |\n"
                    
                    st.write(report)
                    st.session_state.messages.append({"role": "assistant", "content": report})
        
        st.session_state.show_quality = None
    
    # Generate AI summary
    elif st.session_state.get("generate_summary") == selected_table:
        with st.chat_message("assistant"):
            with st.spinner(f"Generating AI summary for {selected_table}..."):
                summary = generate_table_summary(selected_table)
                if summary:
                    st.write(summary)
                    st.session_state.messages.append({"role": "assistant", "content": summary})
        
        st.session_state.generate_summary = None

# ----------------- CHAT INPUT -----------------
user_query = st.chat_input("Ask about your database...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):
            q = user_query.lower()
            answer = ""
            
            # Simple keyword-based responses
            if selected_table and selected_table.lower() in q:
                if "explain" in q or "describe" in q:
                    metadata = get_table_metadata(selected_table)
                    if metadata:
                        answer = f"**{selected_table.upper()}** contains {metadata.get('row_count', 'N/A')} rows with columns like {', '.join([col['column_name'] for col in metadata.get('columns', [])[:5]])}..."
                elif "quality" in q:
                    quality = get_table_quality(selected_table)
                    if quality:
                        worst_col = min(quality.get('column_completeness', {}).items(), 
                                      key=lambda x: x[1]['completeness_percent'])
                        answer = f"**{selected_table}** has {quality.get('total_rows', 'N/A')} rows. The column with lowest completeness is `{worst_col[0]}` at {worst_col[1]['completeness_percent']}%."
                elif "summary" in q or "ai" in q:
                    answer = generate_table_summary(selected_table) or "Failed to generate AI summary."
            elif "tables" in q:
                tables = get_tables()
                answer = f"Available tables: {', '.join(tables)}" if tables else "No tables found."
            elif "health" in q or "status" in q:
                health = check_backend_health()
                if health:
                    answer = f"✅ Backend is healthy. Database: {health.get('database', 'Unknown')}"
                else:
                    answer = "❌ Backend is not responding."
            else:
                answer = (
                    "I can help you with:\n"
                    "- Table explanations (select a table and ask 'explain [table_name]')\n"
                    "- Data quality analysis (ask 'quality of [table_name]')\n"
                    "- AI summaries (ask 'summarize [table_name]')\n"
                    "- List all tables (ask 'what tables are available')\n"
                    "- Check system health (ask 'system status')"
                )
            
            st.write(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})
