"""
Shared fixtures for the RAG chatbot test suite.

We build a standalone FastAPI test app that mirrors the routes in app.py but
without the static-file mount (which requires a ../frontend directory that
doesn't exist in the test environment).  A mocked RAGSystem is injected so
no real ChromaDB, embeddings, or Anthropic API calls are made.
"""

import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import List, Optional


# ---------------------------------------------------------------------------
# Pydantic models (mirrors app.py)
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class Source(BaseModel):
    label: str
    url: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]
    session_id: str


class CourseStats(BaseModel):
    total_courses: int
    course_titles: List[str]


# ---------------------------------------------------------------------------
# Test app factory
# ---------------------------------------------------------------------------

def create_test_app(rag_system) -> FastAPI:
    """
    Return a FastAPI app that exposes the same API routes as app.py but:
      - omits the static-file mount (not needed / not available in tests)
      - uses the supplied *rag_system* object instead of initialising a real one
    """
    app = FastAPI(title="RAG System (test)")

    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id
            if not session_id:
                session_id = rag_system.session_manager.create_session()
            answer, sources = rag_system.query(request.query, session_id)
            return QueryResponse(answer=answer, sources=sources, session_id=session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"],
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/session/{session_id}")
    async def clear_session(session_id: str):
        rag_system.session_manager.clear_session(session_id)
        return {"cleared": True, "session_id": session_id}

    return app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_rag_system():
    """Fully-mocked RAGSystem with sensible default return values."""
    rag = MagicMock()

    # session_manager behaviour
    rag.session_manager.create_session.return_value = "session_1"

    # query() returns (answer, sources)
    rag.query.return_value = (
        "Here is the answer.",
        [{"label": "Course A - Lesson 1", "url": None}],
    )

    # get_course_analytics() returns a dict
    rag.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["Course A", "Course B"],
    }

    return rag


@pytest.fixture
def client(mock_rag_system):
    """Synchronous TestClient backed by the test app with a mocked RAGSystem."""
    app = create_test_app(mock_rag_system)
    return TestClient(app)
