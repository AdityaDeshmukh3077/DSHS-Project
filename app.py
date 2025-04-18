import streamlit as st
import json
import logging
from llm import generateResponse
from preprocessing import generatePrompt

# ---------------------- Logging Configuration ----------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("discharge_summary.log"),
        logging.StreamHandler()  # Optional: allows logs to appear in terminal
    ]
)

# ---------------------- Page Config ----------------------
st.set_page_config(page_title="Discharge Summary Generator", layout="wide")

# ---------------------- Header Section ----------------------
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
    
    col1, col2 = st.columns(2)
    with col1:
        include_name = st.checkbox("Include patient name in summary", value=False)
    with col2:
        use_rag = st.checkbox("Use sample discharge summaries to generate patient discharge summary", value=False)


    # File Upload Section
    st.subheader("📁 Upload JSON File")
    json_file = st.file_uploader("Choose a JSON file", type=["json"])

    if json_file:
        try:
            data = json.load(json_file)
            st.success("File uploaded successfully!")
            logging.info("JSON file uploaded and parsed successfully.")
            callLLM, prompt = generatePrompt(data, include_name, instructions)

            if not callLLM:
                st.warning("⚠️ Summary generation halted:")
                st.text_area("Message:", value=prompt, height=150, disabled=True)
                logging.warning("Summary generation halted: %s", prompt)
            else:
                # Prompt Viewer and Editor
                st.subheader("🧐 Prompt Preview & Editor")
                updatedPrompt = st.text_area("Prompt Used to Generate Discharge Summary:", value=prompt, height=300)

                # Generate Button - Centered
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    generate_clicked = st.button("📝 Generate Summary", use_container_width=True)

                # Generate Prompt or Summary
                if generate_clicked:
                    logging.info("Prompt Sent to LLM:\n%s", updatedPrompt)
                    response = generateResponse(updatedPrompt, use_rag)
                    logging.info("Response from LLM:\n%s", response)
                    st.subheader("📄 Generated Discharge Summary")
                    st.markdown(response)
        except json.JSONDecodeError as e:
            st.error("Invalid JSON file. Please check the format and try again.")
            logging.error("JSON decode error: %s", str(e))
        except Exception as e:
            st.error("An unexpected error occurred.")
            logging.exception("Unexpected error:")
