from qdrant_client import QdrantClient

from .config import QDRANT_URL


qdrant_cli = QdrantClient(url=QDRANT_URL)  # client
