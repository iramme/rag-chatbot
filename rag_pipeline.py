import os
import time
import gc
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

load_dotenv()

# ---------- 1. CHARGEMENT DES PDFs ----------
def load_pdfs(pdf_folder="pdfs_projet/"):
    documents = []
    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(pdf_folder, file))
            documents.extend(loader.load())
    print(f"✅ {len(documents)} pages chargées")
    return documents

# ---------- 2. DÉCOUPAGE EN CHUNKS ----------
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(documents)
    print(f"✅ {len(chunks)} chunks créés")
    return chunks

# ---------- 3. EMBEDDINGS ----------
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

# ---------- 4. VECTORSTORE ----------
def create_vectorstore(chunks):
    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="chroma_db"
    )
    print("✅ Base vectorielle créée")
    return vectorstore

def load_vectorstore():
    embeddings = get_embeddings()
    vectorstore = Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings
    )
    return vectorstore

# ---------- 5. FERMER VECTORSTORE ----------
def close_vectorstore(chain):
    try:
        if hasattr(chain, 'retriever'):
            vs = chain.retriever.vectorstore
            if hasattr(vs, '_client'):
                vs._client.close()
            del vs
        gc.collect()
        time.sleep(1)
    except Exception as e:
        print(f"Close warning: {e}")
        gc.collect()
        time.sleep(1)

# ---------- 6. LLM ----------
def get_llm():
    return ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.2
    )

# ---------- 7. PROMPT ----------
def get_prompt():
    template = """
    You are a helpful assistant that answers questions based on the provided documents.
    Use ONLY the context below to answer. If the answer is not in the context, say:
    "I don't find this information in the provided documents."
    Always mention the source page at the end of your answer.

    Context:
    {context}

    Question: {question}

    Answer:
    """
    return PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

# ---------- 8. RAG CHAIN ----------
def build_rag_chain(vectorstore):
    llm = get_llm()
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": get_prompt()}
    )
    return chain

# ---------- 9. INITIALISATION ----------
def initialize_rag(pdf_folder="pdfs_projet/", rebuild=False):
    if rebuild or not os.path.exists("chroma_db"):
        print("🔄 Construction de la base vectorielle...")
        docs = load_pdfs(pdf_folder)
        chunks = split_documents(docs)
        vectorstore = create_vectorstore(chunks)
    else:
        print("📂 Chargement de la base vectorielle existante...")
        vectorstore = load_vectorstore()
    chain = build_rag_chain(vectorstore)
    return chain

# ---------- 10. QUESTION ----------
def ask_question(chain, question):
    result = chain({"query": question})
    answer = result["result"]
    sources = result["source_documents"]
    source_info = []
    for doc in sources:
        page = doc.metadata.get("page", "?")
        source = doc.metadata.get("source", "?")
        source_info.append(
            f"{os.path.basename(source)} — Page {page + 1}"
        )
    return answer, list(set(source_info))