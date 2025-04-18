import json
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
from preprocessing import generatePrompt

def embed_documents(documents):
    # Make sure all inputs are Document objects
    if isinstance(documents[0], str):
        documents = [Document(page_content=doc) for doc in documents]

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(documents, embedding_model)
    return vectorstore

# 3. Set up local LLM (LM Studio with OpenAI-compatible API)
def load_local_llm():
    return ChatOpenAI(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio", 
        model_name="default",
        temperature=0
    )

# 4. Run the full RAG query
def generate_discharge_summary(vectorstore, llm):
    retriever = vectorstore.as_retriever()
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False
    )

    query = """
    Generate a discharge summary for this patient including:
    - Hospital Course
    - Major Events
    - Significant Labs and Imaging
    - Medications
    - Discharge Plan

    Use a clear, professional tone suitable for clinical documentation.
    """

    result = rag_chain.run(query)
    return result

# 5. Main
if __name__ == "__main__":
    print("Loading and processing patient notes...")
    with open("data.json", "r") as json_file:
        data = json.load(json_file)
    flag , chunks = generatePrompt(data)

    print("Embedding and indexing chunks...")
    vectorstore = embed_documents(chunks)

    print("Loading local LLM from LM Studio...")
    llm = load_local_llm()

    print("Generating discharge summary...")
    summary = generate_discharge_summary(vectorstore, llm)

    print("\nDischarge Summary:\n")
    print(summary)
