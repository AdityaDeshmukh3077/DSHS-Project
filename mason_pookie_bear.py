import streamlit as st
import json
import openai
import os
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Medical Discharge Summary Generator", layout="wide")

# App title and description
st.title("Medical Discharge Summary Generator")
st.markdown("""
This application generates comprehensive discharge summaries from patient data JSON files using OpenAI.
Upload a patient JSON file to get started.
""")

# Set the API key for OpenAI
api_key = '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'
model_choice = 'gpt-4o'

# Initialize the OpenAI client with the API key
client = openai.OpenAI(api_key=api_key)

# Create a directory for saving discharge summaries if it doesn't exist
if not os.path.exists("discharge_summaries"):
    os.makedirs("discharge_summaries")

# File uploader
uploaded_file = st.file_uploader("Upload Patient JSON File", type=["json"])

def generate_discharge_summary(patient_data, model):
    """Generate discharge summary using OpenAI's API"""
    
    # Construct a prompt with specific instructions
    prompt = f"""
    You are a clinical assistant responsible for drafting a detailed hospital discharge summary. 
    Use only the patient data provided below. Your output must follow the instructions and formatting guidelines outlined here.
    {json.dumps(patient_data, indent=2)}
    
    ---

    INSTRUCTIONS (READ CAREFULLY):

    1. Clarity and Completeness:  
    - Write in formal clinical language using full paragraphs.  
    - Ensure the summary includes all necessary information, flowing logically from admission through to discharge and follow-up.  

    2. Specificity:  
    - Follow-up plans must be patient-specific, detailed, and clinically appropriate.  
    - Include any test results pending at discharge, referral instructions, medication monitoring, and any relevant red flags for community care teams.

    3. Safety:  
    - If the clinical data suggests that the patient is not stable for discharge, do not write a discharge letter.  
    - Instead, return the following message exactly as written:  
        "Patient not safe for discharge based on provided data."
        
    4. Data Privacy:  
    - Do not include any personally identifiable information (e.g., name, date of birth, ID numbers), even if it appears in the input.  
    - Refer to the individual only as "the patient."

    ---

    FORMAT AND STRUCTURE:

    Write each of the following sections as a *clearly labeled header, followed by a **detailed paragraph* (no bullet points, no lists). The style should mirror that of formal clinical documentation.

    *Reason for Admission:*  
    Describe the patient's presenting complaint, background history, and the reason for hospital admission.

    *Hospital Course:*  
    Provide a thorough narrative of the inpatient stay. Include clinical assessments, investigations, interventions, treatment response, complications (if any), and the patient's clinical progress.

    *Diagnosis:*  
    State the final diagnosis or diagnoses determined during admission. Include differential diagnoses that were ruled out if relevant.

    *Condition on Discharge:*  
    Summarize the patient's clinical and functional status at the time of discharge. Include mobility, vital signs stability, cognitive status (if relevant), and any persisting symptoms.

    *Medications on Discharge:*  
    Describe the discharge medications using complete sentences. Mention new medications started, existing medications continued, and any that were discontinued or modified, along with the rationale if appropriate.

    *Follow-Up and Recommendations:*  
    Provide a comprehensive follow-up plan. Include specific outpatient appointments, referrals to other services, pending investigations, medication monitoring requirements, and safety netting instructions.

    ---

    """
    
    try:
        # Call the OpenAI API using the initialized client
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a medical expert specialized in creating comprehensive and accurate discharge summaries from patient data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent output
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating discharge summary: {str(e)}"

# Function to save the discharge summary to a text file
def save_discharge_summary(summary, uploaded_filename):
    """Save the discharge summary to a text file named after the uploaded file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Extract the base name of the uploaded file without extension
    base_filename = os.path.splitext(uploaded_filename)[0]
    
    # Create filename
    filename = f"discharge_summaries/discharge_summary_{base_filename}.txt"
    
    # Save the file
    with open(filename, "w") as f:
        f.write(summary)
    
    return filename

# Process the uploaded file when available
if uploaded_file is not None:
    try:
        # Load the patient data from the JSON file
        patient_data = json.load(uploaded_file)
        
        # Display basic patient info
        if "patient_demographics" in patient_data:
            demographics = patient_data["patient_demographics"]
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Patient Overview")
                if "patient_name" in demographics:
                    st.write(f"**Name:** {demographics['patient_name']}")
                if "mrn" in demographics:
                    st.write(f"**MRN:** {demographics['mrn']}")
                if "date_of_birth" in demographics:
                    st.write(f"**DOB:** {demographics['date_of_birth']}")
        
        # Generate button
        if st.button("Generate Discharge Summary"):
            with st.spinner("Generating discharge summary..."):
                discharge_summary = generate_discharge_summary(patient_data, model_choice)
                
                # Save the discharge summary to a file named after the uploaded file
                saved_file = save_discharge_summary(discharge_summary, uploaded_file.name)
                
                # Display the summary
                st.markdown("## Generated Discharge Summary")
                st.markdown(discharge_summary)
                
                # Provide feedback about the saved file
                st.success(f"Discharge summary automatically saved to: {saved_file}")
                
                # Add a download button for the summary
                st.download_button(
                    label="Download Discharge Summary",
                    data=discharge_summary,
                    file_name=f"discharge_summary_{os.path.splitext(uploaded_file.name)[0]}.md",
                    mime="text/markdown"
                )
                
    except json.JSONDecodeError:
        st.error("Error: Invalid JSON file. Please upload a properly formatted JSON file.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")