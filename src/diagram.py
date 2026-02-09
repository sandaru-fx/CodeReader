import logging
from typing import List, Dict
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

DIAGRAM_PROMPT = """You are a Senior Software Architect. 
Your goal is to generate a Mermaid.js flowchart that represents the architecture of the provided codebase.

Tech Stack: {tech_stack}
File Structure:
{file_structure}

Instructions:
1. Analyze the file structure and tech stack to understand the flow.
2. Create a high-level architecture diagram (Flowchart or C4 model style).
3. Use Mermaid.js syntax (graph TD or graph LR).
4. Group related components (e.g., Frontend, Backend, Database) using subgraphs if applicable.
5. **IMPORTANT**: Output ONLY the Mermaid code. Do not include markdown code blocks (```mermaid), explanations, or any other text. Just the code.
6. Keep the node labels concise.
"""

def generate_architecture_diagram(files: List[Path], tech_stack: Dict, api_key: str) -> str:
    """
    Generates a Mermaid.js diagram code based on the repository file structure.
    """
    try:
        if not api_key:
            return "graph TD; A[Error: No API Key] --> B[Please enter API Key];"

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.2
        )

        # Format file list into a tree-like string or just a list
        # Limiting to top 50 files to avoid token limits if the repo is huge, 
        # picking most relevant ones (source code)
        relevant_files = [str(f.name) for f in files if f.suffix not in ['.txt', '.md', '.gitignore']][:50]
        file_structure_str = "\n".join(relevant_files)
        
        tech_stack_str = f"Languages: {', '.join(tech_stack.get('languages', []))}, Frameworks: {', '.join(tech_stack.get('frameworks', []))}"

        prompt = ChatPromptTemplate.from_template(DIAGRAM_PROMPT)
        chain = prompt | llm | StrOutputParser()

        mermaid_code = chain.invoke({
            "tech_stack": tech_stack_str,
            "file_structure": file_structure_str
        })

        # Cleanup: Remove markdown code blocks if the LLM adds them despite instructions
        mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()
        
        return mermaid_code

    except Exception as e:
        logger.error(f"Error generating diagram: {e}")
        return f"graph TD; A[Error] --> B[{str(e)}];"
