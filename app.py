import streamlit as st
import json
import logging
from llm import generateResponse
from preprocessing import generatePrompt

# Page Config
st.set_page_config(page_title="Discharge Summary Generator", layout="wide")

# Header Section
st.markdown("""
    <h1 style='text-align: center;'>🏥 Discharge Summary Generator</h1>
    <p style='text-align: center;'>Upload a patient record in JSON format to generate a structured discharge summary.</p>
""", unsafe_allow_html=True)

# Wider layout using columns
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    # Instruction Input
    st.subheader("✏️ Instructions for Summary Generation")
    instructions = st.text_area("Enter any specific instructions to follow while generating the discharge summary:")

    # Checkbox for including patient name
    st.markdown("<div style='text-align: center; font-weight: bold;'>", unsafe_allow_html=True)
    include_name = st.checkbox("Include patient name in summary", value=False)
    st.markdown("</div>", unsafe_allow_html=True)

    # File Upload Section
    st.subheader("📁 Upload JSON File")
    json_file = st.file_uploader("Choose a JSON file", type=["json"])

    if json_file:
        try:
            data = json.load(json_file)
            st.success("File uploaded successfully!")
            callLLM, prompt = generatePrompt(data, include_name, instructions)

            if not callLLM:
                st.warning("⚠️ Summary generation halted:")
                st.text_area("Message:", value=prompt, height=150, disabled=True)
            else:
                # Prompt Viewer and Editor
                st.subheader("🧠 Prompt Preview & Editor")
                updatedPrompt = st.text_area("Prompt Used to Generate Discharge Summary:", value=prompt, height=300)

                # Generate Button - Centered
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    generate_clicked = st.button("📝 Generate Summary", use_container_width=True)

                # Generate Prompt or Summary
                if generate_clicked:
                    logging.info("Prompt Sent to LLM:\n%s", updatedPrompt)
                    response = generateResponse(updatedPrompt)
                    logging.info("Response from LLM:\n%s", response)
                    st.subheader("📄 Generated Discharge Summary")
                    st.markdown(response)
        except json.JSONDecodeError:
            st.error("Invalid JSON file. Please check the format and try again.")