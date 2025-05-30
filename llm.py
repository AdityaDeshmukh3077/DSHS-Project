from openai import OpenAI
from utils import checkIfPatientNotesContainDischargeSummary, processDRG, processDiagnoses, processEncounters, processFlowsheets, processFollowUpCare, processImaging, processLabs, processLifestyleModifications, processMedOrders, processNotes, processPatientDemopgraphics, processWardRoundNotes
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
import os

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
    
    prompt = "You are a junior clinical assistant on an internal medicine ward, responsible for drafting accurate and comprehensive hospital discharge summaries. Your summary will be reviewed by attending physicians, shared with the patient’s primary care provider, and used for clinical handover. It must clearly communicate the patient’s course of treatment, clinical status at discharge, and follow-up plan. Base your summary solely on the patient data provided below, and adhere strictly to the formatting and clinical documentation guidelines that follow.\n\n"
    prompt += generatePatientSummaryForDischargedPatient(data, include_name)
    if instructions and instructions.strip() :
        prompt += "\n\n The following instructions need to be followed. Overrule the general instructions if you have to. "
        prompt += instructions
        prompt += "\n\n"
    prompt += generalInstructions
    return prompt

def generateResponse(prompt, use_rag=False) :
    
    if(not use_rag):
        return basicLLMResponse(prompt)
    else:
        return useRAGBasedLLMResponse(prompt)
    
def load_summaries_from_folder(folder_path):
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read().strip()
                if content:
                    documents.append(Document(page_content=content, metadata={"source": filename}))
    return documents

def useRAGBasedLLMResponse(prompt, folder_path="sample_discharge_summaries"):
    documents = load_summaries_from_folder(folder_path)

    if not documents:
        raise ValueError("No valid .txt files found in the folder or the files are empty.")
    embedding_model = HuggingFaceEmbeddings(
        model_name="pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"
    )
    vectorstore = FAISS.from_documents(documents, embedding_model)
    llm = ChatOpenAI(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",
        model_name="default",
        temperature=0
    )
    retriever = vectorstore.as_retriever()
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False
    )
    return rag_chain.run(prompt)

def basicLLMResponse(prompt):
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