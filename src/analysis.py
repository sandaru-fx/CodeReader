import json
from pathlib import Path

def analyze_tech_stack(repo_path: Path) -> dict:
    """
    Analyzes the repository to identify the tech stack and dependencies.
    """
    tech_stack = {
        "languages": [],
        "frameworks": [],
        "dependencies": []
    }
    
    # Check for package.json (Node.js)
    package_json = repo_path / "package.json"
    if package_json.exists():
        try:
            with open(package_json, 'r') as f:
                data = json.load(f)
                tech_stack["languages"].append("JavaScript/TypeScript")
                
                deps = data.get("dependencies", {})
                dev_deps = data.get("devDependencies", {})
                
                # Check for common frameworks
                if "react" in deps: tech_stack["frameworks"].append("React")
                if "next" in deps: tech_stack["frameworks"].append("Next.js")
                if "vue" in deps: tech_stack["frameworks"].append("Vue.js")
                if "express" in deps: tech_stack["frameworks"].append("Express.js")
                
                # List top dependencies
                tech_stack["dependencies"].extend(list(deps.keys())[:10])
        except Exception:
            pass

    # Check for requirements.txt (Python)
    req_txt = repo_path / "requirements.txt"
    if req_txt.exists():
        try:
            with open(req_txt, 'r') as f:
                tech_stack["languages"].append("Python")
                content = f.read().lower()
                
                if "django" in content: tech_stack["frameworks"].append("Django")
                if "flask" in content: tech_stack["frameworks"].append("Flask")
                if "fastapi" in content: tech_stack["frameworks"].append("FastAPI")
                if "streamlit" in content: tech_stack["frameworks"].append("Streamlit")
                
                # Add first few lines as deps
                lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith('#')]
                tech_stack["dependencies"].extend(lines[:10])
        except Exception:
            pass
            
    # Check for pom.xml (Java) - Simple check
    if (repo_path / "pom.xml").exists():
        tech_stack["languages"].append("Java")
        tech_stack["frameworks"].append("Spring Boot (Likely)")

    # Deduplicate
    tech_stack["languages"] = list(set(tech_stack["languages"]))
    tech_stack["frameworks"] = list(set(tech_stack["frameworks"]))
    
    return tech_stack
