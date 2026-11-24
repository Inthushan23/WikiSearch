from config import TOOLS_PATH


QDRANT_URL: str = "http://localhost:6333"
COLLECTION_NAME: str = "col_wiki_titles"  # Collection's name in Qdrant

# Paths
WIKI_TOOL_DIR: str = TOOLS_PATH / "wiki_tool"
# WIKI_FILE_PATH : str = WIKI_TOOL_DIR / "data" / "wiki_titles"
WIKI_FILE_PATH: str = WIKI_TOOL_DIR / "data" / "wiki_sample"

WIKI_TOOL_DIR: str = TOOLS_PATH / "wiki_tool"
# WIKI_FILE_PATH : str = WIKI_TOOL_DIR / "data" / "wiki_titles"
WIKI_FILE_PATH: str = WIKI_TOOL_DIR / "data" / "paris_articles_titles.txt"

# RAG
VEC_SIZE: int = 1024
RAG_THRESHOLD: float = 0.6
RAG_RETRIEVE_LIMIT: int = 10

# Encoder
ENCODER_MODEL: str = "BAAI/bge-m3"  # Model from Hugging face

MAX_WORKERS: int = 3

CONTENT_LENGTH_THRESH: int = (
    2000  # Seuil au dessus du quel la taille du contexte est réduit
)
