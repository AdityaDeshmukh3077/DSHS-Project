from openai import OpenAI
from utils import checkIfPatientNotesContainDischargeSummary, processDRG, processDiagnoses, processEncounters, processFlowsheets, processFollowUpCare, processImaging, processLabs, processLifestyleModifications, processMedOrders, processNotes, processPatientDemopgraphics, processWardRoundNotes
import json

def generatePatientSummaryForDischargedPatient(data, include_name):
    patientDischargeNotesPresent = checkIfPatientNotesContainDischargeSummary(data)
    patientDemographicsPresent, patientDemographicsSummary = processPatientDemopgraphics(data)
    diagnosesPresent, diagnosesSummary = processDiagnoses(data)
    encountersPresent, encountersSummary = processEncounters(data)
    drgPresent, drgSummary = processDRG(data)
    flowsheetsPresent, flowsheetsSummary = processFlowsheets(data)
    imagingPresent, imagingSummary = processImaging(data)
    labsPresent, labsSummary = processLabs(data)
    medOrdersPresent, medOrdersSummary = processMedOrders(data)
    notesPresent, notesSummary = processNotes(data)
    wardRoundNotesPresent, wardRoundNotesSummary = processWardRoundNotes(data)
    followUpCarePresent, followUpCareSummary = processFollowUpCare(data)
    lifestyleModificationsPresent, lifestyleModificationsSummary = processLifestyleModifications(data)

    summary = ""
    
    if not patientDischargeNotesPresent:
        summary += "The final patient discharge notes are not present for the particular patient. This needs to be highlighted in the discharge summary at the top as a warning. Follow the same font and style as the rest of the text \n\n"
    if include_name and patientDemographicsPresent:
        summary += f"{patientDemographicsSummary}\n\n"
    if diagnosesPresent:
        summary += f"{diagnosesSummary}\n\n"
    if encountersPresent:
        summary += f"{encountersSummary}\n\n"
    if drgPresent:
        summary += f"{drgSummary}\n\n"
    if flowsheetsPresent:
        summary += f"{flowsheetsSummary}\n\n"
    if imagingPresent:
        summary += f"{imagingSummary}\n\n"
    if labsPresent:
        summary += f"{labsSummary}\n\n"
    if medOrdersPresent:
        summary += f"{medOrdersSummary}\n\n"
    if notesPresent:
        summary += f"{notesSummary}\n\n"
    if wardRoundNotesPresent:
        summary += f"{wardRoundNotesSummary}\n\n"
    if followUpCarePresent:
        summary += f"{followUpCareSummary}\n\n"
    if lifestyleModificationsPresent:
        summary += f"{lifestyleModificationsSummary}\n\n"

    return summary.strip()

def generatePromptForDischargedPatient(data, include_name, instructions) :
    
    with open('config.json', 'r') as f:
        config = json.load(f)
        generalInstructions = config.get('general_instructions', '')
    
    prompt = "You are a clinical assistant responsible for drafting a detailed hospital discharge summary. Use only the patient data provided below. Your output must follow the instructions and formatting guidelines outlined after the patient data. \n\n"
    prompt += generatePatientSummaryForDischargedPatient(data, include_name)
    if (instructions is not None) :
        prompt += "The following instructions need to be followed. Overrule the general instructions if you have to. "
        prompt += instructions
        prompt += "\n\n"
    prompt += generalInstructions
    return prompt

def generateResponse(prompt) :
    
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
    chat_completion = client.chat.completions.create(
    messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="default",
    )
    
    return chat_completion.choices[0].message.content