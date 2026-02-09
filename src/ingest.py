import git
import logging
import os
from pathlib import Path
from collections import Counter
from src.utils import create_unique_temp_dir, delete_directory

logger = logging.getLogger(__name__)

# Extensions to process (allowing a broad range of code files)
# Instead of an allowlist, let's use a denylist for safety, but maybe an allowlist is safer for RAG?
# Valid code extensions for our purpose:
VALID_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp', 
    '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala', '.html', '.css', 
    '.sql', '.sh', '.bat', '.json', '.yaml', '.yml', '.md', '.txt'
}

# Directories to ignore
IGNORE_DIRS = {
    '.git', '.vscode', '.idea', '__pycache__', 'node_modules', 'venv', 'env', 
    'dist', 'build', 'target', 'bin', 'obj', 'migrations'
}

# Specific files to ignore
IGNORE_FILES = {
    'package-lock.json', 'yarn.lock', 'poetry.lock', 'Pipfile.lock', 'composer.lock', 
    '.DS_Store', 'thumbs.db'
}

def clone_repository(repo_url: str) -> Path:
    """
    Clones a GitHub repository to a unique temporary directory.
    """
    try:
        target_dir = create_unique_temp_dir()
        logger.info(f"Cloning {repo_url} into {target_dir}...")
        git.Repo.clone_from(repo_url, target_dir, depth=1)
        logger.info("Cloning completed successfully.")
        return target_dir
    except Exception as e:
        logger.error(f"Failed to clone repository: {e}")
        if 'target_dir' in locals():
            delete_directory(target_dir)
        raise e

def is_valid_file(file_path: Path) -> bool:
    """
    Checks if a file is valid for ingestion based on extension and name.
    """
    # Check if in ignored directory
    for part in file_path.parts:
        if part in IGNORE_DIRS:
            return False
            
    # Check filename
    if file_path.name in IGNORE_FILES:
        return False
        
    # Check extension
    # We accept files with valid extensions OR common text files like Dockerfile
    if file_path.suffix.lower() in VALID_EXTENSIONS:
        return True
        
    if file_path.name in ['Dockerfile', 'Makefile', 'Jenkinsfile']:
        return True
        
    return False

def get_repo_files(repo_path: Path) -> list[Path]:
    """
    Recursively gets all valid files in the repository.
    """
    files = []
    try:
        for item in repo_path.rglob("*"):
            if item.is_file() and is_valid_file(item):
                files.append(item)
    except Exception as e:
        logger.error(f"Error traversing directory {repo_path}: {e}")
    return files

def get_repo_stats(repo_path: Path) -> dict:
    """
    Calculates statistics for the repository (Language breakdown).
    
    Returns:
        dict: A dictionary containing 'total_files', 'languages' (percentage breakdown).
    """
    files = get_repo_files(repo_path)
    if not files:
        return {"total_files": 0, "languages": {}}

    extension_counts = Counter()
    for file in files:
        ext = file.suffix.lower()
        if not ext:
            if file.name in ['Dockerfile', 'Makefile', 'Jenkinsfile']:
                ext = file.name
            else:
                ext = 'Other'
        extension_counts[ext] += 1
        
    total_files = len(files)
    stats = {
        "total_files": total_files,
        "languages": {k: round((v / total_files) * 100, 2) for k, v in extension_counts.items()}
    }
    
    return stats
