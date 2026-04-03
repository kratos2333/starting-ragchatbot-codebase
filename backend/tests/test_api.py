"""
API endpoint tests for the RAG chatbot.

Each test class covers one endpoint family.  All tests use the `client`
fixture (from conftest.py) which is backed by a lightweight test app and a
fully-mocked RAGSystem — no real database, embeddings, or API calls are made.
"""

import pytest


class TestQueryEndpoint:
    """Tests for POST /api/query"""

    def test_returns_200_with_answer_and_session(self, client):
        response = client.post("/api/query", json={"query": "What is Python?"})
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Here is the answer."
        assert isinstance(data["session_id"], str)
        assert len(data["session_id"]) > 0

    def test_auto_creates_session_when_none_provided(self, client, mock_rag_system):
        """When no session_id is in the request a new one is created."""
        response = client.post("/api/query", json={"query": "What is Python?"})
        assert response.status_code == 200
        # The mock session_manager.create_session() returns "session_1"
        assert response.json()["session_id"] == "session_1"
        mock_rag_system.session_manager.create_session.assert_called_once()

    def test_uses_provided_session_id(self, client, mock_rag_system):
        """When a session_id is supplied it is passed through unchanged."""
        response = client.post(
            "/api/query",
            json={"query": "What is Python?", "session_id": "my-existing-session"},
        )
        assert response.status_code == 200
        assert response.json()["session_id"] == "my-existing-session"
        # create_session should NOT have been called
        mock_rag_system.session_manager.create_session.assert_not_called()
        # query should have received the explicit session id
        mock_rag_system.query.assert_called_once_with(
            "What is Python?", "my-existing-session"
        )

    def test_returns_sources_list(self, client):
        response = client.post("/api/query", json={"query": "Tell me about Course A"})
        assert response.status_code == 200
        sources = response.json()["sources"]
        assert isinstance(sources, list)
        assert len(sources) == 1
        assert sources[0]["label"] == "Course A - Lesson 1"
        assert sources[0]["url"] is None

    def test_missing_query_field_returns_422(self, client):
        """Pydantic validation rejects requests without the required `query` field."""
        response = client.post("/api/query", json={})
        assert response.status_code == 422

    def test_empty_query_string_is_accepted(self, client):
        """An empty string is a valid (if unusual) query value."""
        response = client.post("/api/query", json={"query": ""})
        assert response.status_code == 200

    def test_rag_exception_returns_500(self, client, mock_rag_system):
        """Unhandled errors from the RAG system surface as HTTP 500."""
        mock_rag_system.query.side_effect = RuntimeError("embedding failure")
        response = client.post("/api/query", json={"query": "crash?"})
        assert response.status_code == 500
        assert "embedding failure" in response.json()["detail"]


class TestCoursesEndpoint:
    """Tests for GET /api/courses"""

    def test_returns_200_with_course_stats(self, client):
        response = client.get("/api/courses")
        assert response.status_code == 200
        data = response.json()
        assert data["total_courses"] == 2
        assert "Course A" in data["course_titles"]
        assert "Course B" in data["course_titles"]

    def test_course_titles_is_a_list(self, client):
        response = client.get("/api/courses")
        assert isinstance(response.json()["course_titles"], list)

    def test_analytics_exception_returns_500(self, client, mock_rag_system):
        mock_rag_system.get_course_analytics.side_effect = Exception("db unavailable")
        response = client.get("/api/courses")
        assert response.status_code == 500
        assert "db unavailable" in response.json()["detail"]

    def test_empty_catalog_returns_zero_courses(self, client, mock_rag_system):
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 0,
            "course_titles": [],
        }
        response = client.get("/api/courses")
        assert response.status_code == 200
        data = response.json()
        assert data["total_courses"] == 0
        assert data["course_titles"] == []


class TestSessionEndpoint:
    """Tests for DELETE /api/session/{session_id}"""

    def test_clear_session_returns_200(self, client):
        response = client.delete("/api/session/session_42")
        assert response.status_code == 200

    def test_clear_session_response_body(self, client):
        response = client.delete("/api/session/session_42")
        data = response.json()
        assert data["cleared"] is True
        assert data["session_id"] == "session_42"

    def test_clear_session_calls_session_manager(self, client, mock_rag_system):
        client.delete("/api/session/my-session-id")
        mock_rag_system.session_manager.clear_session.assert_called_once_with(
            "my-session-id"
        )

    def test_clear_session_with_different_ids(self, client, mock_rag_system):
        """Session ID is passed through verbatim regardless of its format."""
        for session_id in ["abc-123", "session_99", "some-uuid-here"]:
            mock_rag_system.session_manager.clear_session.reset_mock()
            response = client.delete(f"/api/session/{session_id}")
            assert response.status_code == 200
            assert response.json()["session_id"] == session_id
            mock_rag_system.session_manager.clear_session.assert_called_once_with(
                session_id
            )
