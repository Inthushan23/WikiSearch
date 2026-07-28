# mcp-serv

## Overview

`mcp-serv` is a local assistant that answers general-knowledge questions with grounding in Wikipedia.

A local LLM (via **Ollama**) drives a **LangGraph** agent. The agent can call a Wikipedia tool that:

1. Retrieves candidate article titles from a **Qdrant** vector store (RAG over title embeddings).
2. Fetches matching page content from Wikipedia (**Wikipedia-API**).
3. Returns that content to the LLM as tool output.

The HTTP surface is a small **FastAPI** API. An optional CLI talks to the same API.

## Requirements

- **Python** 3.12+ (see `.python-version`)
- **[Ollama](https://ollama.com/)** running locally, with the model configured in `src/config.py` (default: `model-expert:latest` at `http://localhost:11434`)
- **[Qdrant](https://qdrant.tech/)** for the wiki RAG pipeline (default: `http://localhost:6333`)

## Architecture

```
User → FastAPI /ask → LangGraph
                         │
                         ▼
                   response (ChatOllama + tools)
                         │
            ┌────────────┴────────────┐
            │ tool_calls?             │ no
            ▼                         ▼
         tools (ToolNode)            END
            │
            ▼
    wikipedia_search(query)
            │
            ▼
    rag_search → Qdrant titles → Wikipedia page text
            │
            └──────────► response (again)
```

Key pieces:

| Piece | Role |
|-------|------|
| `src/agents/graph_agent.py` | Compiled LangGraph: `response` ↔ `tools` loop with `MemorySaver` checkpointing |
| `src/agents/tools/wiki_tool/main.py` | LangChain `@tool` `wikipedia_search` |
| `src/agents/tools/wiki_tool/domain/ai/rag.py` | Vector query against Qdrant (`col_wiki_titles`) |
| `src/agents/tools/wiki_tool/domain/search/wiki_search.py` | Title → Wikipedia content fetch |
| `src/api/endpoints.py` | FastAPI app (`/health`, `/ask`) |

## Repository structure

Paths relative to the repository root. Omitted: `.venv/`, `__pycache__/`, build artifacts, and `qdrant_storage/`.

```
mcp-serv/
├── src/
│   ├── api/
│   │   └── endpoints.py          # FastAPI: GET /health, POST /ask
│   ├── agents/
│   │   ├── agent_state.py        # LangGraph state (messages, …)
│   │   ├── graph_agent.py        # Graph + Ollama tool-calling agent
│   │   ├── io.py                 # Question formatting + CLI conversation
│   │   ├── tools/
│   │   │   └── wiki_tool/        # Wikipedia + Qdrant RAG
│   │   │       ├── main.py       # wikipedia_search tool
│   │   │       ├── client.py     # Qdrant client
│   │   │       ├── config.py     # Collection, encoder, RAG thresholds
│   │   │       ├── wiki_utils.py
│   │   │       ├── data/         # Title lists (wiki_sample, wiki_titles)
│   │   │       ├── domain/
│   │   │       │   ├── ai/
│   │   │       │   │   ├── rag.py
│   │   │       │   │   └── build_vectorstore.py
│   │   │       │   ├── search/
│   │   │       │   │   ├── wiki_search.py
│   │   │       │   │   └── wiki_fetch.py
│   │   │       │   └── wiki_search.py
│   │   │       └── scripts/
│   │   │           ├── build_vectorstore.py
│   │   │           ├── update_vectorstore.py
│   │   │           └── test.py
│   │   └── utils/
│   │       ├── checking.py
│   │       ├── cli_responses.py
│   │       ├── loader_utils/
│   │       └── transform_utils/
│   ├── app.py                    # CLI entrypoint (python -m src.app)
│   └── config.py                 # MODEL, AGENT_URL, URL, paths
├── main.py
├── Makefile
├── pyproject.toml
├── requirements.txt
├── uv.lock
├── .python-version
└── README.md
```

## Setup

Create and activate a virtual environment, then install the project in editable mode so `src.*` imports resolve.

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

A legacy `requirements.txt` exists for Makefile-based installs; prefer `pyproject.toml` / `uv.lock`.

### NLTK data

Text normalization uses French stopwords. Download once if needed:

```powershell
python -c "import nltk; nltk.download('stopwords')"
```

## Configuration

Edit `src/config.py`:

| Variable | Default | Meaning |
|----------|---------|---------|
| `MODEL` | `model-expert:latest` | Ollama model name |
| `AGENT_URL` | `http://localhost:11434` | Ollama base URL |
| `URL` | `http://localhost:8000` | FastAPI base URL (CLI client) |

Wiki / RAG settings live in `src/agents/tools/wiki_tool/config.py`:

| Variable | Default | Meaning |
|----------|---------|---------|
| `QDRANT_URL` | `http://localhost:6333` | Qdrant endpoint |
| `COLLECTION_NAME` | `col_wiki_titles` | Vector collection |
| `WIKI_FILE_PATH` | `…/data/wiki_sample` | Title list used to build embeddings |
| `ENCODER_MODEL` | `BAAI/bge-m3` | Sentence-transformers model |
| `RAG_THRESHOLD` | `0.6` | Minimum similarity score |
| `RAG_RETRIEVE_LIMIT` | `10` | Max titles retrieved |

## Run the HTTP API

From the **repository root**, with the venv activated:

```powershell
uvicorn src.api.endpoints:agent_app --reload --host 127.0.0.1 --port 8000
```

Endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check (`{"status": "200"}`) |
| `POST` | `/ask?user_req=…` | Runs the compiled LangGraph; returns `{"response": "…"}` |

Example:

```powershell
curl -X POST "http://127.0.0.1:8000/ask?user_req=Qui%20est%20Faker%20%3F"
```

Ollama must be running and the configured model available before calling `/ask`.

## CLI conversation (optional)

With the API already running:

```powershell
python -m src.app
```

Commands in the CLI:

- `/help` — show help
- `/bye` — exit

## Wiki tool: build Qdrant embeddings

Before the agent can ground answers via RAG, build (or rebuild) the vector store.

Script: `src/agents/tools/wiki_tool/scripts/build_vectorstore.py`

It reads titles from `WIKI_FILE_PATH`, fetches Wikipedia summaries, encodes them with `ENCODER_MODEL`, and upserts points into Qdrant (`COLLECTION_NAME`).

Ensure Qdrant is up, then from the repo root:

```powershell
python src/agents/tools/wiki_tool/scripts/build_vectorstore.py
```

Related scripts under `src/agents/tools/wiki_tool/scripts/`:

- `update_vectorstore.py` — update existing embeddings
- `test.py` — quick checks

If the collection does not exist yet, `rag_query` will attempt to create/populate it via `create_update_embeddings` on first use (this can be slow).

## Development

- Install in editable mode (`pip install -e .` or `uv pip install -e .`) before running the API, CLI, or scripts that import `src.*`.
- On Windows, the Makefile `install` target uses `uv` and `requirements.txt`; prefer `uv sync` / `uv pip install -e .` when possible.

## License

Add a `LICENSE` file when you choose a license for this repository.
