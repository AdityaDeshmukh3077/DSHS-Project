from typing import Dict, Tuple

def checkIfPatientDischarged(data):
    return "discharge_date" in data.get("patient_demographics", {})

def checkIfPatientExpectedToBeDischarged(data):
    return "expected_discharge_date" in data.get("patient_demographics", {})

def checkIfPatientNotesContainDischargeSummary(data):
    return any(
        note.get("note_type") == "Discharge Summary"
        for note in data.get("notes", [])
    )

def processPatientDemopgraphics(data) -> Tuple[bool, str]:
    demo = data.get("patient_demographics", {})
    if not demo:
        return False, "Patient demographic information is missing."
    name = demo.get("name", "Unknown")
    age = demo.get("age", "Unknown")
    gender = demo.get("gender", "Unknown")
    admission_date = demo.get("admission_date", "Unknown")

    if checkIfPatientDischarged(data):
        discharge_info = demo.get("discharge_date")
        discharge_text = f"and was discharged on {discharge_info}."
    elif checkIfPatientExpectedToBeDischarged(data):
        discharge_info = demo.get("expected_discharge_date", "Unknown")
        discharge_text = f"and is expected to be discharged on {discharge_info}."
    else:
        discharge_text = "and there is no discharge information available."

    return True, f"The patient is a {age}-year-old {gender} who was admitted on {admission_date} {discharge_text} The patient's name is {name}."

def processDiagnoses(data: Dict) -> Tuple[bool, str]:
    diagnoses = data.get("diagnoses")
    if diagnoses:
        diag_str = "; ".join(
            [f"{d.get('description', 'Unknown')} (Code: {d.get('diagnosis_code', 'N/A')}) diagnosed on {d.get('date', 'N/A')}" for d in diagnoses]
        )
        return True, f"The patient received the following diagnoses: {diag_str}."
    else:
        return False, "No diagnoses were recorded for this patient."

def processEncounters(data: Dict) -> Tuple[bool, str]:
    encounters = data.get("encounters")
    if encounters:
        encounter_str = "; ".join(
            [f"On {e.get('date', 'Unknown')}, a {e.get('type', 'Unknown')} was conducted for {e.get('reason') or e.get('description') or e.get('findings') or 'unspecified reasons'}" for e in encounters]
        )
        return True, f"The patient had the following encounters during the stay: {encounter_str}."
    else:
        return False, "No encounter information was found for this patient."

def processDRG(data: Dict) -> Tuple[bool, str]:
    drg = data.get("drg")
    if drg:
        return True, f"The patient was classified under DRG code {drg.get('code', 'N/A')}, which corresponds to {drg.get('description', 'no description provided')}."
    else:
        return False, "No DRG classification was recorded for this patient."

def processFlowsheets(data: Dict) -> Tuple[bool, str]:
    flowsheets = data.get("flowsheets")
    if flowsheets:
        flow_str = "; ".join(
            [
                f"On {f.get('date', 'Unknown')} at {f.get('time', '')}, the recorded vital signs were: Temperature {f.get('temperature')}, Heart Rate {f.get('heart_rate')}, Blood Pressure {f.get('blood_pressure')}, Respiratory Rate {f.get('respiratory_rate')}, and Oxygen Saturation {f.get('oxygen_saturation')}"
                for f in flowsheets
            ]
        )
        return True, f"The patient's vital signs during the hospital stay were as follows: {flow_str}."
    else:
        return False, "No vital sign data was recorded for this patient."

def processImaging(data: Dict) -> Tuple[bool, str]:
    imaging = data.get("imaging")
    if imaging:
        img_str = "; ".join(
            [f"On {i.get('date', 'Unknown')}, a {i.get('type', 'Unknown')} was performed which showed: {i.get('findings', 'No findings recorded')}" for i in imaging]
        )
        return True, f"The patient underwent the following imaging studies: {img_str}."
    else:
        return False, "No imaging studies were recorded for this patient."

def processLabs(data: Dict) -> Tuple[bool, str]:
    labs = data.get("labs")
    if labs:
        lab_str = "; ".join(
            [f"On {l.get('date', 'Unknown')}, the following lab results were obtained: " + ", ".join(f"{t.get('name')}: {t.get('result')}" for t in l.get('tests', [])) for l in labs]
        )
        return True, f"The patient had the following laboratory results: {lab_str}."
    else:
        return False, "No lab results were found for this patient."

def processMedOrders(data: Dict) -> Tuple[bool, str]:
    meds = data.get("med_orders")
    if meds:
        med_str = "; ".join(
            [f"On {m.get('date', 'Unknown')}, {m.get('medication', 'an unnamed medication')} was administered at a dose of {m.get('dose', 'no dose specified')}, with a frequency of {m.get('frequency', 'no frequency specified')}" for m in meds]
        )
        return True, f"The following medications were ordered and administered: {med_str}."
    else:
        return False, "No medication orders were found for this patient."

def processNotes(data: Dict) -> Tuple[bool, str]:
    notes = data.get("notes")
    if notes:
        note_str = "; ".join(
            [f"On {n.get('date', 'Unknown')}, a {n.get('note_type', 'note')} was recorded. Content: {n.get('content', '')}" for n in notes]
        )
        return True, f"The following clinical notes were recorded: {note_str}."
    else:
        return False, "No clinical notes were recorded for this patient."

def processWardRoundNotes(data: Dict) -> Tuple[bool, str]:
    wrn = data.get("ward_round_notes")
    if wrn:
        wrn_str = "; ".join(
            [f"On {n.get('date', 'Unknown')} at {n.get('time', '')}, the following note was made: {n.get('note', '')}" for n in wrn]
        )
        return True, f"Ward round notes include the following entries: {wrn_str}."
    else:
        return False, "No ward round notes were available for this patient."

def processFollowUpCare(data: Dict) -> Tuple[bool, str]:
    follow_up = data.get("follow_up_care")
    if follow_up:
        fu_str = "; ".join(
            [f"{f.get('type', 'Follow-up care')} was recommended with the following instructions: {f.get('details', '')}" for f in follow_up]
        )
        return True, f"The patient received the following follow-up care instructions: {fu_str}."
    else:
        return False, "No follow-up care instructions were provided for this patient."

def processLifestyleModifications(data: Dict) -> Tuple[bool, str]:
    mods = data.get("lifestyle_modifications")
    if mods:
        mod_str = "; ".join(
            [f"The patient was advised to follow this lifestyle change: {m.get('recommendation', 'Lifestyle change')} — {m.get('details', '')}" for m in mods]
        )
        return True, f"The following lifestyle modifications were recommended: {mod_str}."
    else:
        return False, "No lifestyle modifications were documented for this patient."