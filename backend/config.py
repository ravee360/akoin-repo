import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Model name (default fallback)
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")

# Optional: vector DB path
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma_db")

# Optional: PDF path (falls back to first PDF in backend/data)
DATA_PATH = os.getenv("DATA_PATH")
