import streamlit as st
import pandas as pd
import io
from openai import OpenAI
import os

# Use stored secret
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)

# Page config
st.set_page_config(page_title="AI PFMEA Generator", layout="wide")
st.title("🤖 AI PFMEA Generator")
st.markdown("Generate a detailed PFMEA table using OpenAI GPT-4 and examples from `PFMEA.xlsx`.")

# Input fields
process_name = st.text_input("🏭 Process Name")
equipment = st.text_input("🛠️ Equipment Involved")
special_notes = st.text_area("📌 Special Considerations")

# Load examples from PFMEA.xlsx (rows 9 to 35 only)
markdown_examples = ""
try:
    df_examples = pd.read_excel("PFMEA.xlsx", skiprows=8, nrows=27)  # Rows 9 to 35 (1-based indexing)
    markdown_examples = df_examples.to_markdown(index=False)
except Exception as e:
    st.warning(f"⚠️ Could not load PFMEA example file: {e}")

# Define PFMEA columns
pfmea_columns = """station number | process name | process elements | Requirements | Potential Failure Modes | Potential effect of line | Potential effect of system | Severity | Class | Potential casual mechanisms | Current process management Prevention | Frequency of Occurrence | Current process control detection | Detection | RPN | Recommended activities"""

# Generate PFMEA
if st.button("🚀 Generate PFMEA"):
    if not process_name or not equipment:
        st.error("Please enter the Process Name and Equipment.")
    else:
        with st.spinner("Generating PFMEA..."):

            prompt = f"""
You are an expert in automotive manufacturing PFMEA.
Generate a detailed PFMEA table for the following process:

Process Name: {process_name}
Equipment Involved: {equipment}
Special Considerations: {special_notes}

Structure the PFMEA as a markdown table with the following columns:
{pfmea_columns}

Generate at least 10 rows.

{f'Examples:\n{markdown_examples}' if markdown_examples else ''}
"""

            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                content = response.choices[0].message.content

                # Parse markdown table
                lines = content.strip().split("\n")
                table_lines = [line for line in lines if "|" in line]

                header_line = table_lines[0]
                headers = [h.strip() for h in header_line.split("|")[1:-1]]

                separator_index = -1
                for i, line in enumerate(table_lines):
                    if set(line.strip()) <= set("-|: "):
                        separator_index = i
                        break

                data_rows = table_lines[separator_index + 1:]
                data = [row.strip().split("|")[1:-1] for row in data_rows]
                data = [[cell.strip() for cell in row] for row in data]

                df = pd.DataFrame(data, columns=headers)
                st.success("✅ PFMEA Table Generated")
                st.dataframe(df)

                # Export to Excel
                output = io.BytesIO()
                df.to_excel(output, index=False, sheet_name="PFMEA")
                st.download_button("📥 Download Excel", output.getvalue(), file_name="PFMEA_Output.xlsx")

            except Exception as e:
                st.error(f"❌ Error generating PFMEA: {e}")
