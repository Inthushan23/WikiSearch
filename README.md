# WikiSearch

**A fully local, Wikipedia-grounded question-answering assistant.**
A local LLM (Ollama) orchestrated by a LangGraph agent retrieves relevant Wikipedia articles through semantic search (Qdrant + BGE-M3) before answering, so responses are grounded in real sources instead of the model's memory alone.

## Features

- **Local-first**: the LLM runs through Ollama, the vector store through Qdrant.
- **Agentic tool calling**: a LangGraph agent decides when a Wikipedia lookup is needed, calls the tool, and loops until it can answer.
- **Semantic title retrieval (RAG)**: article titles are embedded with `BAAI/bge-m3` (multilingual) and stored in Qdrant; a similarity threshold filters out weak matches.
- **Live page content**: once titles are selected, the page content is fetched from Wikipedia and passed to the LLM as tool output.
- **Conversation memory**: LangGraph `MemorySaver` checkpointing keeps context across turns.
- **Three interfaces**: Chainlit chat UI, REST API (FastAPI) and a terminal CLI.
- **Data tooling**: scripts to build and update the vector store, and a Wikipedia category crawler to collect article titles.

## Architecture

```
            ┌─────────────┐
 User ────▶ │  Interface  │  Chainlit UI · CLI · REST (FastAPI)
            └──────┬──────┘
                   ▼
            ┌─────────────┐
            │  LangGraph  │◀───────────────────────────┐
            │   agent     │                            │
            │ (ChatOllama)│                            │
            └──────┬──────┘                            │
        tool call? │                                   │
          yes ▼    └── no ──▶ final answer             │
       ┌──────────────┐                                │
       │ ToolNode     │                                │
       │ wikipedia_   │──▶ Qdrant (title embeddings)   │
       │ search       │──▶ Wikipedia-API (page content)│
       └──────┬───────┘                                │
              └──────────── tool output ───────────────┘
```

## Project structure

```
wikipedia-agent/
├── README.md
├── Makefile
├── pyproject.toml
├── requirements.txt
├── uv.lock
├── main.py
├── auth.yaml
├── chainlit.md                 # Chainlit welcome page
├── models/
│   └── Modelfile.txt           # Ollama model definition
└── src/
    ├── config.py               # Model, Ollama and API URLs
    ├── api/
    │   ├── endpoints.py        # FastAPI: GET /health, POST /ask
    │   └── schemas.py          # Request/response schemas
    ├── cli/
    │   └── cli.py              # Terminal client
    ├── ui/
    │   └── ui.py               # Chainlit front end
    ├── agents/
    │   ├── agent_state.py      # LangGraph state
    │   ├── graph_agent.py      # Graph + Ollama tool-calling agent
    │   ├── graphs_manager.py   # Graph management
    │   ├── io.py               # Question formatting
    │   └── tools/
    │       └── wiki_tool/
    │           ├── client.py   # Qdrant client
    │           ├── config.py   # Collection, encoder, RAG thresholds
    │           ├── main.py     # wikipedia_search tool
    │           ├── wiki_utils.py
    │           ├── data/       # Title lists
    │           ├── domain/
    │           │   ├── ai/
    │           │   │   ├── build_vectorstore.py
    │           │   │   └── rag.py
    │           │   ├── search/
    │           │   │   ├── wiki_fetch.py
    │           │   │   └── wiki_search.py
    │           │   └── wiki_search.py
    │           └── scripts/
    │               ├── build_vectorstore.py
    │               ├── update_vectorstore.py
    │               ├── process_csv.py
    │               └── wikipedia_category_crawler.py
    └── utils/
        ├── checking.py
        ├── cli_responses.py
        ├── loader_utils/
        └── transform_utils/
```

## Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** (recommended package manager)
- **[Ollama](https://ollama.com/)** running locally (default: `http://localhost:11434`)
- **[Qdrant](https://qdrant.tech/)** (default: `http://localhost:6333`), e.g. via Docker:

  ```bash
  docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant
  ```

## Installation

```bash
git clone https://github.com/Inthushan23/WikiSearch.git
cd WikiSearch
uv sync
```

Without uv:

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
pip install -e .
```

Text normalization uses NLTK stopwords (French). Download them once:

```bash
python -c "import nltk; nltk.download('stopwords')"
```

## Configuration

**`src/config.py`**

| Variable      | Default                    | Description                        |
| ------------- | -------------------------- | ---------------------------------- |
| `AGENT_URL` | `http://localhost:11434` | Ollama base URL                    |
| `URL`       | `http://localhost:8000`  | FastAPI base URL (used by the CLI) |

**`src/agents/tools/wiki_tool/config.py`**

| Variable          | Default                   | Description                   |
| ----------------- | ------------------------- | ----------------------------- |
| `QDRANT_URL`    | `http://localhost:6333` | Qdrant endpoint               |
| `ENCODER_MODEL` | `BAAI/bge-m3`           | Sentence-transformers encoder |

## Usage

### 1. Build the vector store (first run)

```bash
uv run python src/agents/tools/wiki_tool/scripts/build_vectorstore.py
```

Reads titles from `WIKI_FILE_PATH`, fetches Wikipedia summaries, encodes them with `ENCODER_MODEL` and upserts them into Qdrant. If the collection is missing, the first query creates and populates it automatically.

Other scripts in `src/agents/tools/wiki_tool/scripts/`:

- `update_vectorstore.py`: refresh existing embeddings
- `wikipedia_category_crawler.py`: collect article titles from Wikipedia categories
- `process_csv.py`: process CSV title lists

### 2. Start the API

The Chainlit front end and the CLI both rely on the API, so start it first (from the repository root):

```bash
uv run uvicorn src.api.endpoints:agent_app --reload --host 127.0.0.1 --port 8000
```

| Method   | Path                 | Description                                    |
| -------- | -------------------- | ---------------------------------------------- |
| `GET`  | `/health`          | Liveness check                                 |
| `POST` | `/ask?user_req=…` | Runs the agent, returns `{"response": "…"}` |

### 3. Launch the Chainlit front end

In a second terminal:

```bash
uv run chainlit run src/ui/ui.py -w --port 8001
```

Then open **http://localhost:8001**. The `-w` flag enables auto-reload on file changes.

## Tech stack

Python · LangGraph · LangChain · Ollama · Qdrant · sentence-transformers (BGE-M3) · Wikipedia-API · FastAPI · Chainlit · uv
