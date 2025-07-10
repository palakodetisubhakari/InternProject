import streamlit as st
import pandas as pd
import openai
import io

st.set_page_config(page_title="AI PFMEA Generator", layout="wide")
st.title("🤖 AI PFMEA Generator")
st.markdown("Generate a detailed PFMEA table using OpenAI GPT-4.")

# Inputs
openai_api_key = st.text_input("🔑 OpenAI API Key", type="password")
process_name = st.text_input("🏭 Process Name")
equipment = st.text_input("🛠️ Equipment Involved")
special_notes = st.text_area("📌 Special Considerations")
markdown_examples = st.text_area("📎 Paste Previous PFMEA Markdown Table (optional)")

if st.button("🚀 Generate PFMEA"):
    if not all([openai_api_key, process_name, equipment]):
        st.warning("Please fill in the required fields.")
        st.stop()

    pfmea_columns = (
        "station number | process name | process elements | Requirements | "
        "Potential Failure Modes | Potential effect of line | Potential effect of system | "
        "Severity | Class | Potential casual mechanisms | "
        "Current process management Prevention | Frequency of Occurrence | "
        "Current process control detection | Detection | RPN | Recommended activities"
    )

    prompt = f"""
You are an expert in automotive manufacturing PFMEA.
Generate a detailed PFMEA table for the following process:

Process Name: {process_name}
Equipment Involved: {equipment}
Special Considerations: {special_notes}

Structure the PFMEA as a markdown table with the following columns:
{pfmea_columns}

Generate at least 9 rows.

{f'Examples:\n{markdown_examples}' if markdown_examples else ''}
"""

    try:
        client = openai.OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        content = response.choices[0].message.content
        lines = content.strip().split("\n")
        table_lines = [line for line in lines if "|" in line]
        header_line = table_lines[0]
        headers = [h.strip() for h in header_line.split("|")[1:-1]]
        sep_index = next(i for i, l in enumerate(table_lines) if "---" in l)
        data_lines = table_lines[sep_index + 1:]
        data = [line.strip().split("|")[1:-1] for line in data_lines]

        expected_columns = [col.strip() for col in pfmea_columns.split("|")]
        for i in range(len(data)):
            if len(data[i]) < len(expected_columns):
                data[i].extend([''] * (len(expected_columns) - len(data[i])))
            data[i] = data[i][:len(expected_columns)]

        df = pd.DataFrame(data, columns=expected_columns)
        st.success("✅ PFMEA Generated Successfully!")
        st.dataframe(df, use_container_width=True)

        output = io.BytesIO()
        df.to_excel(output, index=False, sheet_name="PFMEA")
        st.download_button(
            label="📥 Download PFMEA as Excel",
            data=output.getvalue(),
            file_name="PFMEA_Output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception as e:
        st.error(f"❌ Error generating PFMEA: {e}")
