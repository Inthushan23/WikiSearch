from pathlib import Path


# URLs
MODEL = "model-expert:latest"
OLLAMA_URL = "http://localhost:11434"
URL = "http://localhost:8000"  # fastapi server


# Paths
ROOT_PATH = Path(__file__).parent.parent
SRC_PATH = ROOT_PATH / "src"

TOOLS_PATH = SRC_PATH / "agents" / "tools"

RESPONCE_LATENCY: float = 0.075
