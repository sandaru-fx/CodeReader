import os
from pathlib import Path

# Base directory for the project
BASE_DIR = Path(__file__).parent.parent

# Directory to store cloned repositories using standard temp location or local 'temp' folder
# For an "official" standalone app, using a dedicated temp folder within the project 
# or system temp is fine. Let's use a local 'temp' folder for easier debugging for now.
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# ChromaDB persistence directory
CHROMA_DB_DIR = BASE_DIR / "chroma_db"
