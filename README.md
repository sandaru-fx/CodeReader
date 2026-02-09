# CodeReader (Repo Chat AI) 🤖

CodeReader is a RAG-based application that allows users to chat with any GitHub repository. It uses **Google Gemini** for generation and **ChromaDB** for vector storage, providing a seamless way to understand complex codebases.

## 🚀 Features

- **Chat with Code**: Paste a GitHub URL and ask questions about the code.
- **RAG Powered**: Uses Retrieval-Augmented Generation to fetch relevant code chunks.
- **Tech Stack Analysis**: Automatically detects languages and dependencies.
- **Diagram Generation**: (Coming Soon) Visualizes the architecture using Mermaid.js.

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, LangChain
- **AI Engine**: Google Gemini 1.5 Flash (via `langchain-google-genai`)
- **Vector DB**: ChromaDB (Local Persistence)
- **Frontend**: Streamlit
- **Utilities**: GitPython

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sandaru-fx/CodeReader.git
   cd CodeReader
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## 📝 Usage

1. Open the app in your browser.
2. Enter your **Google API Key** in the sidebar.
3. Paste a **GitHub Repository URL**.
4. Click "Process Repo" (Ingestion).
5. Start chatting!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
