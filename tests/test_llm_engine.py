"""
Tests for pyjavawrap.llm_engine — Ollama communication and prompt building.
"""
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from pyjavawrap.llm_engine import LLMEngine


# ── Fixture ──────────────────────────────────────────────────────────────────

@pytest.fixture
def engine():
    """Return an LLMEngine with default config."""
    with patch.dict(os.environ, {
        "OLLAMA_URL": "http://localhost:11434/api/generate",
        "OLLAMA_MODEL": "gpt-oss-cloud:120b",
    }):
        return LLMEngine()


@pytest.fixture
def sample_schema():
    return json.dumps({
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
        },
        "required": ["id", "name"],
        "type": "object",
    }, indent=2)


@pytest.fixture
def sample_paths():
    return json.dumps({
        "/users/{user_id}": {
            "get": {
                "summary": "Get User",
                "operationId": "get_user",
            }
        }
    }, indent=2)


# ── Initialization ───────────────────────────────────────────────────────────

class TestInit:

    def test_default_url(self, engine):
        assert engine.url == "http://localhost:11434/api/generate"

    def test_default_model(self, engine):
        assert engine.model == "gpt-oss-cloud:120b"

    def test_custom_env_vars(self):
        with patch.dict(os.environ, {
            "OLLAMA_URL": "http://custom:9999/api/generate",
            "OLLAMA_MODEL": "qwen-coder-3-next",
        }):
            e = LLMEngine()
            assert e.url == "http://custom:9999/api/generate"
            assert e.model == "qwen-coder-3-next"


# ── Prompt generation ────────────────────────────────────────────────────────

class TestGetJavaPrompt:

    def test_dto_prompt_contains_schema(self, engine, sample_schema):
        prompt = engine.get_java_prompt(sample_schema, type_name="DTO")
        assert "integer" in prompt
        assert "string" in prompt

    def test_dto_prompt_mentions_pojo(self, engine, sample_schema):
        prompt = engine.get_java_prompt(sample_schema, type_name="DTO")
        assert "POJO" in prompt

    def test_dto_prompt_mentions_jackson(self, engine, sample_schema):
        prompt = engine.get_java_prompt(sample_schema, type_name="DTO")
        assert "Jackson" in prompt

    def test_client_prompt_contains_paths(self, engine, sample_paths):
        prompt = engine.get_java_prompt(sample_paths, type_name="Client")
        assert "get_user" in prompt

    def test_client_prompt_mentions_spring(self, engine, sample_paths):
        prompt = engine.get_java_prompt(sample_paths, type_name="Client")
        assert "Spring Boot" in prompt

    def test_client_prompt_mentions_type_safe(self, engine, sample_paths):
        prompt = engine.get_java_prompt(sample_paths, type_name="Client")
        assert "type-safe" in prompt

    def test_default_type_is_dto(self, engine, sample_schema):
        prompt = engine.get_java_prompt(sample_schema)  # no type_name
        assert "POJO" in prompt


# ── Code generation (mocked Ollama) ──────────────────────────────────────────

class TestGenerateCode:

    @patch("pyjavawrap.llm_engine.requests.post")
    def test_successful_generation(self, mock_post, engine):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": "public class User { private int id; }"
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = engine.generate_code("Generate a User class")
        assert "public class User" in result

    @patch("pyjavawrap.llm_engine.requests.post")
    def test_sends_correct_payload(self, mock_post, engine):
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": ""}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        engine.generate_code("test prompt")

        call_args = mock_post.call_args
        payload = call_args.kwargs.get("json") or call_args[1].get("json")
        assert payload["model"] == "gpt-oss-cloud:120b"
        assert payload["prompt"] == "test prompt"
        assert payload["stream"] is False

    @patch("pyjavawrap.llm_engine.requests.post")
    def test_empty_response_field(self, mock_post, engine):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = engine.generate_code("test")
        assert result == ""

    @patch("pyjavawrap.llm_engine.requests.post")
    def test_connection_error_returns_message(self, mock_post, engine):
        mock_post.side_effect = ConnectionError("Connection refused")

        result = engine.generate_code("test")
        assert "Error communicating with Ollama" in result
        assert "Connection refused" in result

    @patch("pyjavawrap.llm_engine.requests.post")
    def test_http_error_returns_message(self, mock_post, engine):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("500 Server Error")
        mock_post.return_value = mock_response

        result = engine.generate_code("test")
        assert "Error communicating with Ollama" in result
