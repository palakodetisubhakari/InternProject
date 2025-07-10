import streamlit as st
import pandas as pd
import openai
import io
import os

# Load OpenAI API Key from secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# UI setup
st.set_page_config(page_title="AI PFMEA Generator", layout="wide")
st.title("🤖 AI PFMEA Generator")
st.markdown("Generate a detailed PFMEA table using OpenAI GPT-4 and examples from `PFMEA.xlsx`.")

# Load and slice Excel file (rows 9 to 35 → index 8 to 34)
try:
    df_example = pd.read_excel("PFMEA.xlsx", engine="openpyxl").iloc[8:35]
    markdown_examples = df_example.to_markdown(index=False)
except Exception as e:
    markdown_examples = ""
    st.warning(f"⚠️ Could not load PFMEA example file: {e}")

# Input fields
process_name = st.text_input("🏗️ Process Name")
equipment = st.text_input("🛠️ Equipment Involved")
special_notes = st.text_area("📌 Special Considerations")

# Generate PFMEA
if st.button("🚀 Generate PFMEA") and process_name and equipment:
    pfmea_columns = (
        "station number | process name | process elements | Requirements | Potential Failure Modes | "
        "Potential effect of line | Potential effect of system | Severity | Class | "
        "Potential casual mechanisms | Current process management Prevention | "
        "Frequency of Occurrence | Current process control detection | Detection | RPN | Recommended activities"
    )

    prompt = f"""
You are an expert in automotive manufacturing PFMEA.
Generate a detailed PFMEA table for the following process:

Process Name: {process_name}
Equipment Involved: {equipment}
Special Considerations: {special_notes}

Structure the PFMEA as a markdown table with the following columns:
{pfmea_columns}

Generate at least 10 rows.

Examples:
{markdown_examples}
"""

    with st.spinner("Generating PFMEA..."):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        content = response.choices[0].message["content"]
        st.markdown("### 📝 Generated PFMEA Table")
        st.markdown(content)

        # Convert to Excel
        table_lines = [line for line in content.split("\n") if "|" in line]
        header = [col.strip() for col in table_lines[0].split("|")[1:-1]]
        data_rows = [[cell.strip() for cell in row.split("|")[1:-1]] for row in table_lines[2:]]

        df_result = pd.DataFrame(data_rows, columns=header)
        output = io.BytesIO()
        df_result.to_excel(output, index=False, engine="openpyxl")
        output.seek(0)

        st.download_button("📥 Download PFMEA Excel", output, file_name="PFMEA_Generated.xlsx")
