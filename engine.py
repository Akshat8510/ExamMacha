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
# In engine.py

# In engine.py

def get_rag_chain(vectorstore, api_key, help_me_mode=False):
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)
    
    persona = (
        "You are 'Macha', a legendary senior. \n"
        "You are looking at two things: 1) The user's NOTES and 2) Extra information found from the INTERNET.\n"
        "If the answer is in the NOTES, use that first. If it's not, look at the INTERNET data provided in the user's message.\n"
        "ONLY if both are empty, say: 'Macha can't find this in your notes or the web.'\n"
        "Don't be a robot—if the internet info is there, USE IT to answer the junior!"
    )
    
    if help_me_mode:
        persona += "\nExplain using funny analogies like we are in the canteen."

    # Note: We keep the system prompt but make it more flexible
    system_prompt = f"{persona} \n\nNOTES CONTEXT: {{context}}"
    
    from langchain_core.prompts import ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{input}")])
    
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.chains import create_retrieval_chain
    
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(vectorstore.as_retriever(), combine_docs_chain)