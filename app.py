import streamlit as st
import os
import tempfile
from pathlib import Path

from src.ingest import clone_repository, get_repo_stats
from src.vector_store import process_repo_to_vector_store
from src.rag_chain import ask_question
from src.analysis import analyze_tech_stack
from src.utils import delete_directory

# Page Config
st.set_page_config(
    page_title="CodeReader AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Next Level" UI
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    .stTextInput > div > div > input {
        background-color: #161b22;
        color: #c9d1d9;
        border: 1px solid #30363d;
    }
    .stButton > button {
        background-color: #238636;
        color: white;
        border: none;
        border-radius: 6px;
    }
    .stButton > button:hover {
        background-color: #2ea043;
    }
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #30363d;
    }
    h1, h2, h3 {
        color: #58a6ff !important;
    }
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "repo_processed" not in st.session_state:
    st.session_state.repo_processed = False
if "repo_stats" not in st.session_state:
    st.session_state.repo_stats = {}
if "tech_stack" not in st.session_state:
    st.session_state.tech_stack = {}

st.title("🤖 CodeReader AI")
st.caption("Chat with any GitHub Repository using Gemini Pro")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_key = st.text_input("Google API Key", type="password", help="Get yours at makersuite.google.com")
    repo_url = st.text_input("GitHub Repo URL")
    
    process_btn = st.button("🚀 Ingest Repository", use_container_width=True)
    
    if st.session_state.repo_processed:
        st.divider()
        st.header("📊 Repository Stats")
        
        # Tech Stack Display
        ts = st.session_state.tech_stack
        if ts.get("languages"):
            st.markdown(f"**Languages:** {', '.join(ts['languages'])}")
        if ts.get("frameworks"):
            st.markdown(f"**Frameworks:** {', '.join(ts['frameworks'])}")
            
        # File Stats
        stats = st.session_state.repo_stats
        st.metric("Total Files", stats.get("total_files", 0))
        
        if stats.get("languages"):
            st.markdown("### Language Breakdown")
            st.bar_chart(stats["languages"])

# --- Main Logic ---

if process_btn and repo_url and api_key:
    if not api_key.startswith("AI"):
        st.error("Invalid API Key format.")
    else:
        with st.status("Processing Repository...", expanded=True) as status:
            try:
                # 1. Clone
                status.write("📥 Cloning repository...")
                repo_path = clone_repository(repo_url)
                
                # 2. Analyze
                status.write("🔍 Analyzing tech stack...")
                st.session_state.repo_stats = get_repo_stats(repo_path)
                st.session_state.tech_stack = analyze_tech_stack(repo_path)
                
                # 3. Vectorize
                status.write("🧠 Building knowledge base (this may take a while)...")
                # Need to get list of files first
                from src.ingest import get_repo_files
                files = get_repo_files(repo_path)
                process_repo_to_vector_store(files, api_key)
                
                # 4. Cleanup
                # status.write("🧹 Cleaning up temp files...")
                # delete_directory(repo_path)
                # Note: We might want to keep it if we implement specific file lookup later
                
                st.session_state.repo_processed = True
                status.update(label="✅ Repository Processed Successfully!", state="complete", expanded=False)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
                status.update(label="❌ Processing Failed", state="error")

# --- Chat Interface ---

if st.session_state.repo_processed:
    # Display Chat History
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask a question about the codebase..."):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Answer
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = ask_question(prompt, api_key)
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error calling AI: {e}")

else:
    # Empty State
    st.info("👈 Please enter a GitHub URL and API Key in the sidebar to get started.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏗️ How it works")
        st.markdown("""
        1. **Clone**: We pull the code to a temporary sandbox.
        2. **Split**: Code is chunked by function/class structure.
        3. **Embed**: Google Gemini turns code into meaning vectors.
        4. **Chat**: You ask, we retrieve relevant context and explain.
        """)
    with col2:
        st.info("💡 **Tip:** Use a specific question like 'How does authentication work?' for best results.")
