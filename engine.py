import os
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader, UnstructuredPowerPointLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

def process_documents(uploaded_files):
    all_docs = []
    for f in uploaded_files:
        temp_path = f"temp_{f.name}"
        with open(temp_path, "wb") as buffer:
            buffer.write(f.getbuffer())
        
        if f.name.endswith(".pdf"):
            loader = PyPDFLoader(temp_path)
        else:
            loader = UnstructuredPowerPointLoader(temp_path)
            
        all_docs.extend(loader.load())
        os.remove(temp_path)
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(all_docs)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_documents(chunks, embeddings)

def get_rag_chain(vectorstore, api_key, help_me_mode=False):
    # Fixed model name and parameter
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)
    
    if help_me_mode:
        persona = (
            "You are 'Macha' in 'HELP ME' mode. A junior is panicking because the exam is tomorrow. "
            "Explain concepts using simple analogies (cricket, food, movies). "
            "Keep it very simple, use short points, and bold the EXACT keywords needed for marks."
        )
    else:
        persona = (
            "You are 'Macha', a legendary senior who got an S-grade. "
            "Provide accurate, structured, and professional academic answers based on the context."
        )

    system_prompt = f"{persona} \n\nContext: {{context}}"
    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{input}")])
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(vectorstore.as_retriever(), combine_docs_chain)