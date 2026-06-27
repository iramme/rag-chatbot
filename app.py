import streamlit as st
import os
from rag_pipeline import initialize_rag, ask_question

# ---------- CONFIG PAGE ----------
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="💬",
    layout="wide"
)

# ---------- STYLE CSS MODERNE ----------
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset et style global */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: #0a0e1a;
    }
    
    /* Animation des points de fond */
    .bg-animation {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 0;
        overflow: hidden;
        background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 50%, #0a0e1a 100%);
    }
    
    .dot {
        position: absolute;
        width: 4px;
        height: 4px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        animation: float 15s infinite ease-in-out;
    }
    
    @keyframes float {
        0%, 100% {
            transform: translate(0, 0) scale(1);
            opacity: 0.3;
        }
        25% {
            transform: translate(100px, -50px) scale(1.5);
            opacity: 0.8;
        }
        50% {
            transform: translate(-50px, 100px) scale(0.8);
            opacity: 0.5;
        }
        75% {
            transform: translate(50px, -100px) scale(1.2);
            opacity: 0.7;
        }
    }
    
    /* Contenu principal au-dessus du fond */
    .main-content {
        position: relative;
        z-index: 1;
    }
    
    /* Titres */
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }
    
    .subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.6);
        font-weight: 300;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Conteneur des messages */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px !important;
        padding: 16px 20px !important;
        margin-bottom: 12px !important;
    }
    
    /* Message utilisateur */
    .stChatMessage.user {
        background: rgba(99, 102, 241, 0.15) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
    }
    
    /* Message assistant */
    .stChatMessage.assistant {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Avatar des messages */
    .stChatMessage .avatar {
        background: linear-gradient(135deg, #6366f1, #a855f7) !important;
        border-radius: 50%;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
    }
    
    .stChatMessage.user .avatar {
        background: linear-gradient(135deg, #8b5cf6, #ec4899) !important;
    }
    
    /* Input chat */
    .stChatInput {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 8px 16px !important;
    }
    
    .stChatInput input {
        background: transparent !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stChatInput input::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
    }
    
    /* Sidebar */
    .css-1d391kg, .css-163i41n {
        background: rgba(10, 14, 26, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: white !important;
    }
    
    /* Uploader */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px dashed rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    
    .stFileUploader .st-emotion-cache-1ibsh2c {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    /* Boutons */
    .stButton button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        padding: 8px 24px !important;
        width: 100% !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3) !important;
    }
    
    /* Source box */
    .source-box {
        background: rgba(255, 255, 255, 0.05) !important;
        border-left: 3px solid #6366f1 !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        margin-top: 8px !important;
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 0.9rem !important;
    }
    
    /* Answer box */
    .answer-box {
        background: rgba(99, 102, 241, 0.1) !important;
        border-left: 3px solid #6366f1 !important;
        padding: 15px !important;
        border-radius: 8px !important;
        margin-top: 10px !important;
        color: white !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        color: rgba(255, 255, 255, 0.7) !important;
        background: transparent !important;
        border: none !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 8px !important;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
    }
    
    /* Info box */
    .stAlert {
        background: rgba(99, 102, 241, 0.1) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 12px !important;
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Success box */
    .stAlert[data-baseweb="notification"] {
        background: rgba(52, 211, 153, 0.1) !important;
        border: 1px solid rgba(52, 211, 153, 0.2) !important;
        color: rgba(255, 255, 255, 0.8) !important;
    }
    
    /* Spinner */
    .stSpinner {
        border-color: #6366f1 !important;
    }
    
    /* Scrollbar personnalisée */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(99, 102, 241, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(99, 102, 241, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# ---------- ANIMATION DES POINTS ----------
st.markdown("""
<div class="bg-animation">
    <div class="dot" style="left: 10%; animation-delay: 0s; animation-duration: 12s;"></div>
    <div class="dot" style="left: 20%; top: 20%; animation-delay: 1s; animation-duration: 14s;"></div>
    <div class="dot" style="left: 30%; top: 60%; animation-delay: 2s; animation-duration: 16s;"></div>
    <div class="dot" style="left: 45%; top: 10%; animation-delay: 0.5s; animation-duration: 13s;"></div>
    <div class="dot" style="left: 55%; top: 70%; animation-delay: 1.5s; animation-duration: 15s;"></div>
    <div class="dot" style="left: 70%; top: 30%; animation-delay: 2.5s; animation-duration: 11s;"></div>
    <div class="dot" style="left: 80%; top: 80%; animation-delay: 3s; animation-duration: 17s;"></div>
    <div class="dot" style="left: 90%; top: 15%; animation-delay: 0.8s; animation-duration: 14s;"></div>
    <div class="dot" style="left: 15%; top: 85%; animation-delay: 1.8s; animation-duration: 13s;"></div>
    <div class="dot" style="left: 60%; top: 5%; animation-delay: 2.2s; animation-duration: 16s;"></div>
    <div class="dot" style="left: 40%; top: 45%; animation-delay: 3.5s; animation-duration: 12s;"></div>
    <div class="dot" style="left: 75%; top: 55%; animation-delay: 0.3s; animation-duration: 15s;"></div>
    <div class="dot" style="left: 5%; top: 35%; animation-delay: 1.2s; animation-duration: 18s;"></div>
    <div class="dot" style="left: 95%; top: 65%; animation-delay: 2.8s; animation-duration: 14s;"></div>
    <div class="dot" style="left: 25%; top: 50%; animation-delay: 0.7s; animation-duration: 13s;"></div>
    <div class="dot" style="width: 6px; height: 6px; left: 50%; top: 40%; animation-delay: 1.5s; animation-duration: 20s;"></div>
    <div class="dot" style="width: 3px; height: 3px; left: 35%; top: 25%; animation-delay: 2s; animation-duration: 11s;"></div>
    <div class="dot" style="width: 5px; height: 5px; left: 65%; top: 75%; animation-delay: 0.5s; animation-duration: 16s;"></div>
</div>
""", unsafe_allow_html=True)

# ---------- CONTENU PRINCIPAL ----------
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ---------- TITRE ----------
st.markdown('<div class="main-title">RAG Document Chatbot</div>', 
            unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask questions about your PDF documents</div>', 
            unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### 📁 Document Management")
    
    # Upload PDF
    uploaded_files = st.file_uploader(
        "Upload your PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        os.makedirs("pdfs", exist_ok=True)
        for file in uploaded_files:
            with open(f"pdfs/{file.name}", "wb") as f:
                f.write(file.getbuffer())
        st.success(f"✅ {len(uploaded_files)} PDF(s) uploaded!")
    
    # Bouton pour construire la base
    if st.button("Build Knowledge Base", type="primary"):
        with st.spinner("Building vector database..."):
            st.session_state.chain = initialize_rag(rebuild=True)
            st.session_state.ready = True
        st.success("✅ Knowledge base ready!")
    
    st.divider()
    st.markdown("### How it works")
    st.markdown("""
    1. Upload your PDFs
    2. Build the knowledge base
    3. Ask your questions
    4. Get answers with sources
    """)

# ---------- INITIALISATION ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ready" not in st.session_state:
    st.session_state.ready = False
if "chain" not in st.session_state:
    # Charger si la base existe déjà
    if os.path.exists("chroma_db"):
        st.session_state.chain = initialize_rag()
        st.session_state.ready = True

# ---------- CHAT HISTORY ----------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("Sources"):
                for src in message["sources"]:
                    st.markdown(f'<div class="source-box">{src}</div>', 
                                unsafe_allow_html=True)

# ---------- CHAT INPUT ----------
if not st.session_state.ready:
    st.info("Please upload PDFs and click 'Build Knowledge Base' to start.")
else:
    if prompt := st.chat_input("Ask a question about your documents..."):
        
        # Message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Réponse du chatbot
        with st.chat_message("assistant"):
            with st.spinner("Searching documents..."):
                answer, sources = ask_question(st.session_state.chain, prompt)
            
            st.markdown(answer)
            
            if sources:
                with st.expander("Sources"):
                    for src in sources:
                        st.markdown(f'<div class="source-box">{src}</div>', 
                                    unsafe_allow_html=True)
        
        # Sauvegarder dans l'historique
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })

st.markdown('</div>', unsafe_allow_html=True)