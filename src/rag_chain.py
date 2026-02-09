import logging
from typing import List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.config import CHROMA_DB_DIR

logger = logging.getLogger(__name__)

# System prompt for the Senior Developer bot
SYSTEM_PROMPT = """You are a Senior Software Engineer acting as a code assistant. 
Your goal is to explain the code from the provided repository context and answer user questions accurately.

Context from the repository:
{context}

---

Instructions:
1. Use only the provided context to answer. If the answer isn't in the context, say you don't know based on the current files.
2. Provide code snippets where relevant to explain logic.
3. Be concise and professional.
4. Mention the file names when referring to specific code.

Question: {question}
"""

def get_rag_chain(api_key: str):
    """
    Sets up and returns the RAG chain.
    """
    try:
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.2
        )
        
        # Initialize Embeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        
        # Load Vector Store
        vector_store = Chroma(
            persist_directory=str(CHROMA_DB_DIR),
            embedding_function=embeddings
        )
        
        # Define Retriever
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        # Define Prompt
        prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
        
        # helper to format docs
        def format_docs(docs):
            return "\n\n".join(f"--- File: {doc.metadata.get('source', 'Unknown')} ---\n{doc.page_content}" for doc in docs)
        
        # Build Chain
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        return rag_chain
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG chain: {e}")
        raise e

def ask_question(question: str, api_key: str) -> str:
    """
    Invokes the RAG chain with a user question.
    """
    try:
        chain = get_rag_chain(api_key)
        response = chain.invoke(question)
        return response
    except Exception as e:
        logger.error(f"Error asking question: {e}")
        return f"Sorry, I encountered an error: {str(e)}"
