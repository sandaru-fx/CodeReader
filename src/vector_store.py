import logging
import os
from typing import List, Generator
from pathlib import Path

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_core.documents import Document

from src.config import CHROMA_DB_DIR
from src.utils import delete_directory

logger = logging.getLogger(__name__)

# Map file extensions to LangChain Languages
EXTENSION_TO_LANGUAGE = {
    '.py': Language.PYTHON,
    '.js': Language.JS,
    '.jsx': Language.JS,
    '.ts': Language.TS,
    '.tsx': Language.TS,
    '.java': Language.JAVA,
    '.cpp': Language.CPP,
    '.go': Language.GO,
    '.rs': Language.RUST,
    '.php': Language.PHP,
    '.rb': Language.RUBY,
    '.kt': Language.KOTLIN,
    '.scala': Language.SCALA,
    '.html': Language.HTML,
    '.md': Language.MARKDOWN,
}

def load_documents_from_files(files: List[Path]) -> List[Document]:
    """
    Loads content from the given list of files and returns a list of LangChain Documents.
    """
    documents = []
    for file_path in files:
        try:
            # Try reading with utf-8, ignore errors if binary creeps in (though we filtered)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if not content.strip():
                continue
                
            # Add metadata
            metadata = {
                "source": str(file_path),
                "filename": file_path.name,
                "extension": file_path.suffix.lower()
            }
            
            documents.append(Document(page_content=content, metadata=metadata))
            
        except Exception as e:
            logger.warning(f"Failed to read file {file_path}: {e}")
            
    return documents

def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Splits documents into chunks based on their language.
    """
    all_chunks = []
    
    # Process documents by language to use appropriate splitters
    docs_by_lang = {}
    generic_docs = []
    
    for doc in documents:
        ext = doc.metadata.get("extension", "")
        lang = EXTENSION_TO_LANGUAGE.get(ext)
        
        if lang:
            if lang not in docs_by_lang:
                docs_by_lang[lang] = []
            docs_by_lang[lang].append(doc)
        else:
            generic_docs.append(doc)
            
    # Language-specific splitting
    for lang, docs in docs_by_lang.items():
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=lang, 
            chunk_size=2000, 
            chunk_overlap=200
        )
        chunks = splitter.split_documents(docs)
        all_chunks.extend(chunks)
        
    # Generic splitting for others
    if generic_docs:
        generic_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000, 
            chunk_overlap=200
        )
        chunks = generic_splitter.split_documents(generic_docs)
        all_chunks.extend(chunks)
        
    return all_chunks

def create_vector_store(chunks: List[Document], api_key: str) -> Chroma:
    """
    Creates (or updates) a Chroma vector store with the given chunks.
    """
    if not chunks:
        logger.warning("No chunks to store.")
        return None
        
    try:
        if not api_key:
            raise ValueError("Google API Key is required for embeddings.")
            
        # Initialize Embeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        
        # Create Vector Store
        # We use a persistent directory
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(CHROMA_DB_DIR)
        )
        
        logger.info(f"Vector store created at {CHROMA_DB_DIR} with {len(chunks)} chunks.")
        return vector_store
        
    except Exception as e:
        logger.error(f"Failed to create vector store: {e}")
        raise e

def process_repo_to_vector_store(files: List[Path], api_key: str):
    """
    Orchestrates the flow: Load -> Chunk -> Store
    """
    logger.info("Loading documents...")
    documents = load_documents_from_files(files)
    
    logger.info(f"Loaded {len(documents)} documents. Chunking...")
    chunks = chunk_documents(documents)
    
    logger.info(f"Created {len(chunks)} chunks. Creating vector store...")
    create_vector_store(chunks, api_key)
    
    return True
