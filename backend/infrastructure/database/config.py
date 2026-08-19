import os
from pathlib import Path
from dotenv import load_dotenv

# app/backend/
BACKEND_DIR = Path(__file__).resolve().parent

# -app/
BASE_DIR = BACKEND_DIR.parent

# loads -> app/backend/.env
ENV_PATH = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Database file details
DB_NAME = os.getenv("DATABASE", "health_tracker.db")
DB_PATH = BACKEND_DIR / DB_NAME
DB_URL = f"sqlite:///{DB_PATH}"


