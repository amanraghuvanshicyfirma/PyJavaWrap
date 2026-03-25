"""
Tests for pyjavawrap.main — CLI orchestration and file generation.
"""
import os
import json
import shutil
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from pyjavawrap.main import main

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_SPEC_PATH = os.path.join(FIXTURES_DIR, "sample_openapi.json")


# ── Helpers ──────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_output(tmp_path):
    """Provide a temporary output directory and clean up after."""
    output_dir = tmp_path / "generated_java"
    yield str(output_dir)


def mock_generate_code(prompt):
    """Return deterministic Java stubs based on prompt content."""
    if "POJO" in prompt:
        return "public class MockModel {\n    private int id;\n}"
    else:
        return "public class MockClient {\n    public void callApi() {}\n}"


# ── CLI argument parsing ─────────────────────────────────────────────────────

class TestCLI:

    @patch("pyjavawrap.main.LLMEngine")
    @patch("sys.argv", ["main", SAMPLE_SPEC_PATH, "--output", "test_out"])
    def test_creates_output_directory(self, MockLLM, tmp_path):
        output = str(tmp_path / "test_out")
        mock_llm = MagicMock()
        mock_llm.generate_code.side_effect = mock_generate_code
        mock_llm.get_java_prompt.return_value = "Generate POJO"
        MockLLM.return_value = mock_llm

        with patch("sys.argv", ["main", SAMPLE_SPEC_PATH, "--output", output]):
            main()

        assert os.path.isdir(output)

    @patch("pyjavawrap.main.LLMEngine")
    def test_creates_model_subdirectory(self, MockLLM, tmp_output):
        mock_llm = MagicMock()
        mock_llm.generate_code.side_effect = mock_generate_code
        mock_llm.get_java_prompt.return_value = "Generate POJO"
        MockLLM.return_value = mock_llm

        with patch("sys.argv", ["main", SAMPLE_SPEC_PATH, "--output", tmp_output]):
            main()

        assert os.path.isdir(os.path.join(tmp_output, "model"))


# ── File generation ──────────────────────────────────────────────────────────

class TestFileGeneration:

    @patch("pyjavawrap.main.LLMEngine")
    def test_generates_dto_files(self, MockLLM, tmp_output):
        mock_llm = MagicMock()
        mock_llm.generate_code.side_effect = mock_generate_code
        mock_llm.get_java_prompt.return_value = "Generate POJO"
        MockLLM.return_value = mock_llm

        with patch("sys.argv", ["main", SAMPLE_SPEC_PATH, "--output", tmp_output]):
            main()

        model_dir = os.path.join(tmp_output, "model")
        assert os.path.isfile(os.path.join(model_dir, "User.java"))
        assert os.path.isfile(os.path.join(model_dir, "Item.java"))

    @patch("pyjavawrap.main.LLMEngine")
    def test_generates_client_file(self, MockLLM, tmp_output):
        mock_llm = MagicMock()
        mock_llm.generate_code.side_effect = mock_generate_code
        mock_llm.get_java_prompt.return_value = "Generate POJO"
        MockLLM.return_value = mock_llm

        with patch("sys.argv", ["main", SAMPLE_SPEC_PATH, "--output", tmp_output]):
            main()

        # Title is "Sample Python API" → SamplePythonAPIClient.java
        assert os.path.isfile(os.path.join(tmp_output, "SamplePythonAPIClient.java"))

    @patch("pyjavawrap.main.LLMEngine")
    def test_dto_files_contain_package_declaration(self, MockLLM, tmp_output):
        mock_llm = MagicMock()
        mock_llm.generate_code.return_value = "public class Stub {}"
        mock_llm.get_java_prompt.return_value = "Generate POJO"
        MockLLM.return_value = mock_llm

        with patch("sys.argv", [
            "main", SAMPLE_SPEC_PATH,
            "--output", tmp_output,
            "--package", "com.test.api",
        ]):
            main()

        user_file = os.path.join(tmp_output, "model", "User.java")
        with open(user_file, "r") as f:
            content = f.read()
        assert "package com.test.api.model;" in content

    @patch("pyjavawrap.main.LLMEngine")
    def test_client_file_contains_package_declaration(self, MockLLM, tmp_output):
        mock_llm = MagicMock()
        mock_llm.generate_code.return_value = "public class Stub {}"
        mock_llm.get_java_prompt.return_value = "Generate Client"
        MockLLM.return_value = mock_llm

        with patch("sys.argv", [
            "main", SAMPLE_SPEC_PATH,
            "--output", tmp_output,
            "--package", "com.test.api",
        ]):
            main()

        client_file = os.path.join(tmp_output, "SamplePythonAPIClient.java")
        with open(client_file, "r") as f:
            content = f.read()
        assert "package com.test.api;" in content

    @patch("pyjavawrap.main.LLMEngine")
    def test_skips_package_when_already_present(self, MockLLM, tmp_output):
        mock_llm = MagicMock()
        mock_llm.generate_code.return_value = "package com.existing;\npublic class Stub {}"
        mock_llm.get_java_prompt.return_value = "Generate POJO"
        MockLLM.return_value = mock_llm

        with patch("sys.argv", ["main", SAMPLE_SPEC_PATH, "--output", tmp_output]):
            main()

        user_file = os.path.join(tmp_output, "model", "User.java")
        with open(user_file, "r") as f:
            content = f.read()
        # Should NOT prepend another package declaration
        assert content.count("package") == 1


# ── LLM interaction ─────────────────────────────────────────────────────────

class TestLLMInteraction:

    @patch("pyjavawrap.main.LLMEngine")
    def test_calls_llm_for_each_schema_and_client(self, MockLLM, tmp_output):
        mock_llm = MagicMock()
        mock_llm.generate_code.return_value = "public class Stub {}"
        mock_llm.get_java_prompt.return_value = "prompt"
        MockLLM.return_value = mock_llm

        with patch("sys.argv", ["main", SAMPLE_SPEC_PATH, "--output", tmp_output]):
            main()

        # 2 schemas (User, Item) + 1 client = at least 3 calls
        assert mock_llm.generate_code.call_count >= 3

    @patch("pyjavawrap.main.LLMEngine")
    def test_get_java_prompt_called_with_dto_type(self, MockLLM, tmp_output):
        mock_llm = MagicMock()
        mock_llm.generate_code.return_value = "public class Stub {}"
        mock_llm.get_java_prompt.return_value = "prompt"
        MockLLM.return_value = mock_llm

        with patch("sys.argv", ["main", SAMPLE_SPEC_PATH, "--output", tmp_output]):
            main()

        # Verify at least one call used type_name="DTO"
        dto_calls = [
            c for c in mock_llm.get_java_prompt.call_args_list
            if c.kwargs.get("type_name") == "DTO" or (len(c.args) > 1 and c.args[1] == "DTO")
        ]
        assert len(dto_calls) >= 1

    @patch("pyjavawrap.main.LLMEngine")
    def test_get_java_prompt_called_with_client_type(self, MockLLM, tmp_output):
        mock_llm = MagicMock()
        mock_llm.generate_code.return_value = "public class Stub {}"
        mock_llm.get_java_prompt.return_value = "prompt"
        MockLLM.return_value = mock_llm

        with patch("sys.argv", ["main", SAMPLE_SPEC_PATH, "--output", tmp_output]):
            main()

        # Verify at least one call used type_name="Client"
        client_calls = [
            c for c in mock_llm.get_java_prompt.call_args_list
            if c.kwargs.get("type_name") == "Client" or (len(c.args) > 1 and c.args[1] == "Client")
        ]
        assert len(client_calls) >= 1
