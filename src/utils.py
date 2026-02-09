import shutil
import uuid
import logging
from pathlib import Path
from src.config import TEMP_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_unique_temp_dir() -> Path:
    """
    Creates a unique temporary directory for a repository clone.
    Returns the Path object to the created directory.
    """
    session_id = str(uuid.uuid4())
    repo_path = TEMP_DIR / session_id
    repo_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created temporary directory: {repo_path}")
    return repo_path

def delete_directory(path: Path):
    """
    Safely deletes a directory and its contents.
    """
    if path.exists() and path.is_dir():
        try:
            # On Windows, sometimes git files are read-only, which causes shutil.rmtree to fail.
            # We might need an onerror handler, but let's try standard first.
            def on_rm_error(func, path, exc_info):
                import stat
                # Make writable and try again
                os.chmod(path, stat.S_IWRITE)
                func(path)

            shutil.rmtree(path, onerror=on_rm_error)
            logger.info(f"Deleted directory: {path}")
        except Exception as e:
            logger.error(f"Error deleting directory {path}: {e}")
