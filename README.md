# mcp-serv

## Overview

This project aims to provide an **assistant agent** that can answer **general-knowledge questions** with **grounding in Wikipedia**. A local **LLM** (via **Ollama**) drives a **LangGraph** workflow; supporting code fetches and normalizes Wikipedia content, optionally indexes article titles and embeddings in **Qdrant** for retrieval, and exposes the agent over a small **FastAPI** HTTP API (and an optional CLI).

The Wikipedia side is implemented with **Wikipedia-API** (live summaries / text) and tooling under `src/agents/tools/wiki_tool/` to build and query a vector store when you need scale or semantic search over titles.

## Requirements

- **Python** 3.12+ (see `.python-version` if you use pyenv / uv)
- **[Ollama](https://ollama.com/)** running locally, with the model configured in `src/config.py` (default: `phi3-expert:latest`)
- **[Qdrant](https://qdrant.tech/)** (optional, only for the wiki vector store pipeline), default URL `http://localhost:6333`

## Repository structure

Paths below are relative to the repository root. Omitted: `.venv/`, `__pycache__/`, build artifacts, and `qdrant_storage/` (local Qdrant data; see `.gitignore`).

```
wikipedia-agent/
├── src/
│   ├── api/
│   │   └── endpoints.py     # FastAPI app: /health, /ask
│   ├── agents/
│   │   ├── agent_state.py   # LangGraph state (messages, etc.)
│   │   ├── graph_agent.py   # Graph definition + compiled graph (Ollama)
│   │   ├── io.py            # CLI conversation, formatting helpers
│   │   ├── tools/
│   │   │   └── wiki_tool/   # Wikipedia + Qdrant pipeline
│   │   │       ├── client.py
│   │   │       ├── config.py
│   │   │       ├── wiki_utils.py
│   │   │       ├── main.py
│   │   │       ├── data/    # e.g. wiki_sample, wiki_titles (title lists)
│   │   │       ├── domain/
│   │   │       │   └── wiki_search.py   # Wikipedia client (thread-local)
│   │   │       └── scripts/
│   │   │           ├── build_vectorstore.py
│   │   │           └── test.py
│   │   └── utils/
│   │       ├── checking.py
│   │       ├── cli_responses.py
│   │       ├── loader_utils/
│   │       │   ├── load_data.py
│   │       │   └── load_model.py
│   │       └── transform_utils/
│   │           ├── encoder.py
│   │           └── process_data.py
│   ├── app.py               
│   └── config.py            # Model URL, paths, tool root
├── main.py                  
├── Makefile
├── pyproject.toml
├── requirements.txt
├── uv.lock
├── .gitignore
├── .python-version
└── README.md
```

## Setup

Create and activate a virtual environment, then install the project in editable mode so `src.*` imports resolve correctly.

**Using uv (recommended):**

```powershell
uv venv
.venv\Scripts\Activate.ps1
uv pip install -e .
```

**Using pip:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

Lockfile users can sync from `uv.lock`:

```powershell
uv sync
```

A legacy `requirements.txt` exists for Makefile-based installs; prefer `pyproject.toml` / `uv.lock` for a single source of truth.

### NLTK data (wiki / text processing)

If you use modules that load NLTK stopwords, download the corpus once:

```powershell
python -c "import nltk; nltk.download('stopwords')"
```

## Run the HTTP API

From the **repository root** (so `src` is importable):

```powershell
uvicorn src.api.endpoints:agent_app --reload --host 127.0.0.1 --port 8000
```

Endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check |
| `POST` | `/ask` | Runs the compiled LangGraph with the user message body |

Ollama URL and model name are set in `src/config.py` (`AGENT_URL`, `MODEL`).

## CLI conversation (optional)

```powershell
python -m src.app
```

This runs the interactive flow wired in `src/app.py` / `src/agents/io.py`.

## Wiki tool: build Qdrant embeddings

Script: `src/agents/tools/wiki_tool/scripts/build_vectorstore.py`

It reads title lists from paths configured in `src/agents/tools/wiki_tool/config.py` (`WIKI_FILE_PATH`), fetches Wikipedia summaries, encodes them with the configured sentence-transformers model, and upserts vectors into Qdrant.

Ensure Qdrant is up and paths / `COLLECTION_NAME` / `ENCODER_MODEL` match your environment. Run from repo root with the venv activated, for example:

```powershell
python src/agents/tools/wiki_tool/scripts/build_vectorstore.py
```

## Development

- Install in editable mode (`pip install -e .` or `uv pip install -e .`) before running tests or scripts that import `src.*`.
- On Windows, the Makefile `install` target uses `uv` and `requirements.txt`; adjust if you standardize on `uv sync` only.

## License

Add a `LICENSE` file when you choose a license for this repository.
