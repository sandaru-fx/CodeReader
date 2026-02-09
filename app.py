import streamlit as st

st.set_page_config(page_title="Repo Chat AI", layout="wide")

st.title("Repo Chat AI 🤖")
st.write("Chat with your GitHub repository using Gemini & RAG.")

# Sidebar
with st.sidebar:
    st.header("Settings")
    repo_url = st.text_input("GitHub Repo URL")
    api_key = st.text_input("Google API Key", type="password")
    if st.button("Process Repo"):
        st.write("Processing... (Not implemented yet)")

# Main Chat
st.chat_message("assistant").write("Hello! Paste a GitHub URL to start chatting.")
