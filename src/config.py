from pathlib import Path


# URLs
MODEL = "model-expert:latest"
# AGENT_URL = "http://localhost:11434"
AGENT_URL = "https://wells-stopped-polyester-style.trycloudflare.com"

URL = "http://localhost:8000" # fastapi server


# Paths
ROOT_PATH = Path(__file__).parent.parent
SRC_PATH = ROOT_PATH / "src"

TOOLS_PATH = SRC_PATH / "agents" / "tools"

RESPONCE_LATENCY : float = 0.075
