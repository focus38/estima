import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

AI_API_KEY = os.getenv("AI_API_KEY")
AI_PROXY_URL = os.getenv("AI_PROXY_URL")

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR")
ALLOWED_FILE_EXTENSIONS : set = set(os.getenv("ALLOWED_FILE_EXTENSIONS").split(","))
