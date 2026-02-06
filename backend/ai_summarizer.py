import os
import json
from groq import Groq

# -----------------------------
# PATHS (your existing structure)
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
METADATA_DIR = os.path.join(BASE_DIR, "metadata")
AI_DOCS_DIR = os.path.join(BASE_DIR, "ai_docs")

# Ensure ai_docs folder exists
os.makedirs(AI_DOCS_DIR, exist_ok=True)

# -----------------------------
# INITIALIZE GROQ CLIENT (SAFE WAY)
# -----------------------------
# 🔹 Put your key in an environment variable instead of hard-coding it
# In PowerShell run once:
# setx GROQ_API_KEY "your_real_key_here"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def generate_table_summary(table_name):
    # Load metadata and quality files
    meta_path = os.path.join(METADATA_DIR, f"{table_name}.json")
    quality_path = os.path.join(METADATA_DIR, f"{table_name}_quality.json")

    metadata = load_json(meta_path)
    quality = load_json(quality_path)

    prompt = f"""
You are a data documentation assistant.

Here is technical metadata for table: {table_name}
Columns: {metadata['columns']}
Primary Keys: {metadata['primary_keys']}

Here is data quality information:
{quality}

Generate:
1) A clear business-friendly summary of what this table represents.
2) Key columns and their likely business meaning.
3) Any data quality risks or caveats.
4) How analysts should typically use this table.

Write this in clean, readable Markdown with headings and bullet points.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",   # Active Groq model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    summary = response.choices[0].message.content

    # Save as Markdown
    md_path = os.path.join(AI_DOCS_DIR, f"{table_name}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"✅ AI summary generated for {table_name}")
    return summary

def generate_all_summaries():
    tables = [
        f.replace(".json", "")
        for f in os.listdir(METADATA_DIR)
        if f.endswith(".json") and not f.endswith("_quality.json")
    ]

    summaries = {}

    for table in tables:
        summaries[table] = generate_table_summary(table)

    print("✅ AI summaries generated for all tables.")
    return summaries
