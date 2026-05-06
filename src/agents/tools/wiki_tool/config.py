from src.config import TOOLS_PATH


QDRANT_URL : str = "http://localhost:6333"
COLLECTION_NAME : str = "col_wiki_titles" # Collection's name in Qdrant

# Paths
WIKI_TOOL_DIR : str = TOOLS_PATH / "wiki_tool"
# WIKI_FILE_PATH : str = WIKI_TOOL_DIR / "data" / "wiki_titles" 
WIKI_FILE_PATH : str = WIKI_TOOL_DIR / "data" / "wiki_sample"


VEC_SIZE : int = 1024

ENCODER_MODEL : str = "BAAI/bge-m3" # Model from Hugging face

MAX_WORKERS : int = 10