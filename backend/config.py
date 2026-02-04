import logging
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

LOG_LEVEL = logging.INFO
AI_API_KEY = os.getenv("AI_API_KEY")
AI_PROXY_URL = os.getenv("AI_PROXY_URL")
AI_API_TIMEOUT = 120

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_DIR = Path(os.getenv("RESULTS_DIR"))
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR")
ALLOWED_FILE_EXTENSIONS : set = set(os.getenv("ALLOWED_FILE_EXTENSIONS").split(","))

EMBEDDING_MODEL = "text-embedding-3-small"
#EMBEDDING_MODEL = "qwen3-embedding-0.6b"

#MAIN_MODEL = "openai/gpt-4.1-mini"
MAIN_MODEL = "gpt-4.1-mini"
DEFAULT_ROLES = ["backend", "frontend", "QA", "analyst", "PM", "DevOps", "architect", "UX/UI designer"]
#DEFAULT_ESTIMATION_MODELS = ["openai/gpt-4.1-mini", "qwen/qwen3-max", "deepseek/deepseek-v3.2"]
DEFAULT_ESTIMATION_MODELS = ["gpt-4.1-mini", "qwen3-max", "llama-4-scout"] # "gpt-5-mini"

SIMILARITY_THRESHOLD = 0.68