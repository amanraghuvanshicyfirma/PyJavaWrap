"""
Tests for pyjavawrap.parser — OpenAPI spec parsing.
"""
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from pyjavawrap.parser import OpenAPIParser

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_SPEC_PATH = os.path.join(FIXTURES_DIR, "sample_openapi.json")


# ── Fixture ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_spec():
    """Load the fixture spec once for reuse."""
    with open(SAMPLE_SPEC_PATH, "r") as f:
        return json.load(f)


@pytest.fixture
def parser_from_file():
    """Return a parser loaded from the local fixture file."""
    p = OpenAPIParser(SAMPLE_SPEC_PATH)
    p.load_spec()
    return p


# ── Loading ──────────────────────────────────────────────────────────────────

class TestLoadSpec:

    def test_load_from_file(self, parser_from_file, sample_spec):
        """Parser should load a local JSON file correctly."""
        assert parser_from_file.spec == sample_spec

    def test_load_from_file_sets_spec(self, parser_from_file):
        """spec must not be empty after loading."""
        assert parser_from_file.spec != {}

    @patch("pyjavawrap.parser.requests.get")
    def test_load_from_url(self, mock_get, sample_spec):
        """Parser should fetch and parse JSON from a URL."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_spec
        mock_get.return_value = mock_response

        p = OpenAPIParser("http://localhost:8000/openapi.json")
        p.load_spec()

        mock_get.assert_called_once_with("http://localhost:8000/openapi.json")
        assert p.spec == sample_spec

    def test_load_nonexistent_file_raises(self):
        """Loading a path that doesn't exist should raise."""
        p = OpenAPIParser("nonexistent_file.json")
        with pytest.raises(FileNotFoundError):
            p.load_spec()


# ── Schema extraction ────────────────────────────────────────────────────────

class TestGetSchemas:

    def test_returns_all_schemas(self, parser_from_file):
        schemas = parser_from_file.get_schemas()
        assert "User" in schemas
        assert "Item" in schemas

    def test_schema_count(self, parser_from_file):
        assert len(parser_from_file.get_schemas()) == 2

    def test_user_schema_has_required_fields(self, parser_from_file):
        user = parser_from_file.get_schemas()["User"]
        assert "id" in user["properties"]
        assert "username" in user["properties"]
        assert "email" in user["properties"]

    def test_item_schema_has_optional_description(self, parser_from_file):
        item = parser_from_file.get_schemas()["Item"]
        desc = item["properties"]["description"]
        # description has a default of null → optional
        assert desc.get("default") is None

    def test_empty_spec_returns_empty_schemas(self):
        p = OpenAPIParser.__new__(OpenAPIParser)
        p.spec = {}
        assert p.get_schemas() == {}


# ── Path extraction ──────────────────────────────────────────────────────────

class TestGetPaths:

    def test_returns_all_paths(self, parser_from_file):
        paths = parser_from_file.get_paths()
        assert "/users/{user_id}" in paths
        assert "/users/" in paths
        assert "/items/" in paths

    def test_path_count(self, parser_from_file):
        assert len(parser_from_file.get_paths()) == 3

    def test_get_user_path_has_get_method(self, parser_from_file):
        paths = parser_from_file.get_paths()
        assert "get" in paths["/users/{user_id}"]

    def test_create_user_path_has_post_method(self, parser_from_file):
        paths = parser_from_file.get_paths()
        assert "post" in paths["/users/"]

    def test_empty_spec_returns_empty_paths(self):
        p = OpenAPIParser.__new__(OpenAPIParser)
        p.spec = {}
        assert p.get_paths() == {}


# ── Metadata ─────────────────────────────────────────────────────────────────

class TestMetadata:

    def test_get_title(self, parser_from_file):
        assert parser_from_file.get_title() == "Sample Python API"

    def test_get_version(self, parser_from_file):
        assert parser_from_file.get_version() == "1.0.0"

    def test_title_default_when_missing(self):
        p = OpenAPIParser.__new__(OpenAPIParser)
        p.spec = {}
        assert p.get_title() == "FastAPIClient"

    def test_version_default_when_missing(self):
        p = OpenAPIParser.__new__(OpenAPIParser)
        p.spec = {}
        assert p.get_version() == "1.0.0"
