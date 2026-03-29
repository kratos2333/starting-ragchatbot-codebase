# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the backend server (from repo root)
cd backend && uv run uvicorn app:app --reload --port 8000

# Or use the convenience script
./run.sh
```

The app serves the frontend statically from the FastAPI backend. Access at `http://localhost:8000`; API docs at `http://localhost:8000/docs`.

**Required**: Set `ANTHROPIC_API_KEY` in a `.env` file in the `backend/` directory (see `.env.example`).

## Architecture

This is a **RAG chatbot** for querying course documents. The backend is FastAPI (Python), the frontend is vanilla JS, and the AI layer uses Anthropic Claude with tool-use for retrieval.

### Request flow

```
Frontend (index.html/script.js)
  → POST /api/query  { query, session_id }
  → RAGSystem.query()
      → AIGenerator sends query + tools to Claude
      → Claude calls CourseSearchTool (tool_use)
      → VectorStore searches ChromaDB collections
      → AIGenerator sends tool results back to Claude
      → Claude produces final answer
  ← { answer, sources, session_id }
```

### Key backend modules

| File | Responsibility |
|------|---------------|
| `app.py` | FastAPI routes, static file serving, lifespan startup |
| `rag_system.py` | Orchestrates the full RAG loop (tool execution, source tracking) |
| `ai_generator.py` | Anthropic API wrapper; handles multi-turn tool-use loop |
| `vector_store.py` | ChromaDB with two collections: `course_catalog` and `course_content` |
| `document_processor.py` | Parses `.txt` course files and chunks them sentence-aware |
| `search_tools.py` | Defines the `CourseSearchTool` that Claude can invoke |
| `session_manager.py` | In-memory conversation history (lost on restart) |
| `config.py` | All tuneable constants (model, chunk size, max results, etc.) |

### ChromaDB collections

- `course_catalog` — one entry per course with metadata (title, lesson count)
- `course_content` — chunked lesson text with `course_name`, `lesson_number`, `source` metadata

Both use SentenceTransformers (`all-MiniLM-L6-v2`) for local embeddings (no external API call).

### Course document ingestion

On startup, `app.py` calls `rag_system.add_course_folder("../docs")`. The `DocumentProcessor` parses `.txt` files expecting the pattern `Lesson N:` headings to split content. The ChromaDB data persists to `backend/chroma_db/` (gitignored).

### Tool-use pattern

`AIGenerator.generate_response()` runs a loop: send messages → if response has `tool_use` blocks → execute each tool via `RAGSystem._execute_tool()` → append results as `tool_result` messages → re-send to Claude → repeat until a `stop_reason` of `end_turn`.
