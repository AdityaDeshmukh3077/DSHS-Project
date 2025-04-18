from llm import generatePromptForDischargedPatient
from utils import checkIfPatientDischarged, checkIfPatientExpectedToBeDischarged, checkIfPatientNotesContainDischargeSummary

    
def generatePrompt(data, include_name=False, instructions=None):
    patientDischarged = checkIfPatientDischarged(data)
    patientExpectedToBeDischarged = checkIfPatientExpectedToBeDischarged(data)
    
    if (not patientDischarged and not patientExpectedToBeDischarged) :
        return False,"The patient is not expected to be discharged. Please do not generate a discharge summary."
    elif (not patientDischarged and patientExpectedToBeDischarged) :
        return False,"Please wait for patient to be discharged before generating a discharge summary."
    elif (patientDischarged) :
        return True, generatePromptForDischargedPatient(data, include_name, instructions)
