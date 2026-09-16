"""Tests for builtin_tools package."""

import json
import os
import tempfile
from pathlib import Path

import pytest
import respx
from httpx import Response

from openjarvis.builtin_tools import create_builtin_registry


@pytest.fixture
def registry():
    """Create a full builtin registry."""
    return create_builtin_registry()


class TestDatetimeTools:
    def test_get_current_datetime(self, registry):
        result = registry.execute({"name": "get_current_datetime", "arguments": {}})
        assert "2026" in result or "2027" in result
        assert "(" in result  # contains weekday

    def test_date_arithmetic(self, registry):
        result = registry.execute({
            "name": "date_arithmetic",
            "arguments": {"date_str": "2026-08-13", "days": 1}
        })
        assert "2026-08-14" in result

    def test_format_datetime(self, registry):
        result = registry.execute({
            "name": "format_datetime",
            "arguments": {"date_str": "2026-08-13T10:30:00", "fmt": "%B %d, %Y"}
        })
        assert "August" in result and "13" in result and "2026" in result

    def test_days_between(self, registry):
        result = registry.execute({
            "name": "days_between",
            "arguments": {"date_a": "2026-08-13", "date_b": "2026-08-20"}
        })
        assert result == 7


class TestMathTools:
    def test_evaluate_expression(self, registry):
        result = registry.execute({
            "name": "evaluate_expression",
            "arguments": {"expression": "2**10 + 1"}
        })
        assert result == "1025"

    def test_evaluate_expression_complex(self, registry):
        result = registry.execute({
            "name": "evaluate_expression",
            "arguments": {"expression": "(5 + 3) * 2 - 1"}
        })
        assert result == "15"

    def test_convert_units(self, registry):
        result = registry.execute({
            "name": "convert_units",
            "arguments": {"value": 5, "from_unit": "km", "to_unit": "m"}
        })
        assert "5000" in result

    def test_prime_factorize(self, registry):
        result = registry.execute({
            "name": "prime_factorize",
            "arguments": {"n": 60}
        })
        assert result == [2, 2, 3, 5]

    def test_prime_factorize_prime(self, registry):
        result = registry.execute({
            "name": "prime_factorize",
            "arguments": {"n": 7}
        })
        assert result == [7]

    def test_solve_equation(self, registry):
        pytest.importorskip("sympy")
        result = registry.execute({
            "name": "solve_equation",
            "arguments": {"equation": "x**2 - 4", "variable": "x"}
        })
        assert "2" in result and "-2" in result


class TestFileTools:
    def test_write_and_read_file(self, registry):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            temp_path = f.name

        try:
            # Write
            result = registry.execute({
                "name": "write_file",
                "arguments": {"path": temp_path, "content": "Hello, World!"}
            })
            assert "Successfully wrote to" in result

            # Read
            result = registry.execute({
                "name": "read_file",
                "arguments": {"path": temp_path}
            })
            assert "Hello, World!" in result
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_list_directory(self, registry):
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test1.txt").write_text("content1")
            Path(tmpdir, "test2.txt").write_text("content2")

            result = registry.execute({
                "name": "list_directory",
                "arguments": {"path": tmpdir, "pattern": "*.txt"}
            })
            assert isinstance(result, list)
            assert len(result) == 2

    def test_file_info(self, registry):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            result = registry.execute({
                "name": "file_info",
                "arguments": {"path": temp_path}
            })
            assert isinstance(result, dict)
            assert "size_bytes" in result
            assert "type" in result
            assert result["type"] == "file"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_search_in_files(self, registry):
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.txt").write_text("hello world\nfoo bar")

            result = registry.execute({
                "name": "search_in_files",
                "arguments": {"path": tmpdir, "pattern": "hello"}
            })
            assert isinstance(result, list)
            assert len(result) > 0
            assert result[0]["match"] == "hello"

    def test_search_dir_and_file(self, registry):
        with tempfile.TemporaryDirectory() as tmpdir:
            sub = Path(tmpdir) / "pkg"
            sub.mkdir()
            (sub / "mod_a.py").write_text("def target_function():\n    return 42\n")
            (sub / "mod_b.py").write_text("# No target here\n")

            matches = registry.execute({
                "name": "search_dir",
                "arguments": {"search_term": "target_function", "dir_path": tmpdir}
            })
            assert len(matches) == 1
            assert "mod_a.py" in matches[0]["file"]

            file_matches = registry.execute({
                "name": "search_file",
                "arguments": {"search_term": "target_function", "file_path": str(sub / "mod_a.py")}
            })
            assert len(file_matches) == 1
            assert file_matches[0]["line"] == 1

    def test_find_file(self, registry):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "apple.py").write_text("")
            (Path(tmpdir) / "banana.py").write_text("")

            results = registry.execute({
                "name": "find_file",
                "arguments": {"file_name": "apple*.py", "dir_path": tmpdir}
            })
            assert len(results) == 1
            assert "apple.py" in results[0]


class TestDataTools:
    def test_parse_json(self, registry):
        json_str = '{"key": "value", "num": 42}'
        result = registry.execute({
            "name": "parse_json",
            "arguments": {"json_str": json_str}
        })
        parsed = json.loads(result)
        assert parsed["key"] == "value"
        assert parsed["num"] == 42

    def test_jq_query(self, registry):
        json_str = '{"users": [{"name": "Alice"}, {"name": "Bob"}]}'
        result = registry.execute({
            "name": "jq_query",
            "arguments": {"json_str": json_str, "path": "users.0.name"}
        })
        assert "Alice" in result

    def test_parse_csv(self, registry):
        csv_str = "name,age\nAlice,30\nBob,25"
        result = registry.execute({
            "name": "parse_csv",
            "arguments": {"csv_str": csv_str}
        })
        assert "Alice" in result
        assert "30" in result
        assert "|" in result  # markdown table format

    def test_regex_search(self, registry):
        result = registry.execute({
            "name": "regex_search",
            "arguments": {"pattern": r"\d+", "text": "abc123def456"}
        })
        assert isinstance(result, list)
        assert "123" in result

    def test_regex_replace(self, registry):
        result = registry.execute({
            "name": "regex_replace",
            "arguments": {
                "pattern": r"\d+",
                "replacement": "X",
                "text": "abc123def456"
            }
        })
        assert result == "abcXdefX"

    def test_sql_query(self, registry):
        setup = """
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);
        INSERT INTO users (name, age) VALUES ('Alice', 30), ('Bob', 25);
        """
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as db_file:
            db_path = db_file.name

        try:
            registry.execute({
                "name": "sql_query",
                "arguments": {"query": setup, "db_path": db_path}
            })
            res = registry.execute({
                "name": "sql_query",
                "arguments": {"query": "SELECT name, age FROM users ORDER BY age DESC;", "db_path": db_path}
            })
            assert "Alice" in res
            assert "30" in res
            assert "Bob" in res
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)


class TestMemoryTools:
    def test_store_and_recall_note(self, registry):
        registry.execute({
            "name": "store_note",
            "arguments": {"key": "test_key", "content": "test content"}
        })

        result = registry.execute({
            "name": "recall_note",
            "arguments": {"key": "test_key"}
        })
        assert result == "test content"

    def test_list_notes(self, registry):
        registry.execute({
            "name": "store_note",
            "arguments": {"key": "note1", "content": "content1"}
        })
        registry.execute({
            "name": "store_note",
            "arguments": {"key": "note2", "content": "content2"}
        })

        result = registry.execute({
            "name": "list_notes",
            "arguments": {}
        })
        assert isinstance(result, list)
        assert "note1" in result

    def test_delete_note(self, registry):
        registry.execute({
            "name": "store_note",
            "arguments": {"key": "to_delete", "content": "content"}
        })

        registry.execute({
            "name": "delete_note",
            "arguments": {"key": "to_delete"}
        })

        result = registry.execute({
            "name": "recall_note",
            "arguments": {"key": "to_delete"}
        })
        assert "not found" in result.lower()


class TestCodeTools:
    def test_run_python(self, registry):
        result = registry.execute({
            "name": "run_python",
            "arguments": {"code": "print('Hello from Python')"}
        })
        assert "Hello from Python" in result

    def test_run_python_arithmetic(self, registry):
        result = registry.execute({
            "name": "run_python",
            "arguments": {"code": "print(2 + 2)"}
        })
        assert "4" in result

    def test_lint_python(self, registry):
        result = registry.execute({
            "name": "lint_python",
            "arguments": {"code": "x = 1\ny = 2"}
        })
        assert "OK" in result

    def test_lint_python_invalid(self, registry):
        result = registry.execute({
            "name": "lint_python",
            "arguments": {"code": "x = "}
        })
        assert "Error" in result or "Syntax" in result

    def test_run_pytest(self, registry):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_sample.py"
            test_file.write_text("def test_ok():\n    assert 1 + 1 == 2\n")
            res = registry.execute({
                "name": "run_pytest",
                "arguments": {"test_path": str(test_file)}
            })
            assert "Exit code: 0" in res
            assert "1 passed" in res


class TestWebTools:
    def test_fetch_url_invalid(self, registry):
        result = registry.execute({
            "name": "fetch_url",
            "arguments": {"url": "not-a-url"}
        })
        assert "Error" in result or "must start with" in result

    def test_search_web(self, registry):
        result = registry.execute({
            "name": "search_web",
            "arguments": {"query": "Python programming", "num_results": 3}
        })
        assert isinstance(result, list)
        if result and "error" not in result[0]:
            assert "title" in result[0] or "url" in result[0]

    @respx.mock
    def test_http_request(self, registry):
        respx.get("https://api.example.com/data").mock(
            return_value=Response(200, json={"status": "ok"})
        )
        res = registry.execute({
            "name": "http_request",
            "arguments": {"url": "https://api.example.com/data"}
        })
        assert res.get("status_code") == 200
        assert res.get("body") == {"status": "ok"}

    def test_parse_openapi_spec(self, registry):
        spec = """
        openapi: 3.0.0
        info:
          title: Sample API
          version: 1.0.0
        paths:
          /status:
            get:
              summary: Check status
        """
        res = registry.execute({
            "name": "parse_openapi_spec",
            "arguments": {"spec_text": spec}
        })
        assert res.get("title") == "Sample API"
        assert res.get("total_endpoints") == 1


class TestRegistryOptions:
    def test_exclude_code_tools(self):
        registry = create_builtin_registry(exclude={"code_tools"})
        assert "run_python" not in registry._tools
        assert "run_shell" not in registry._tools
        assert "lint_python" not in registry._tools
        assert "evaluate_expression" in registry._tools  # math_tools still there

    def test_include_only_math(self):
        registry = create_builtin_registry(include={"math_tools"})
        assert "evaluate_expression" in registry._tools
        assert "read_file" not in registry._tools
        assert "store_note" not in registry._tools

    def test_exclude_multiple(self):
        registry = create_builtin_registry(exclude={"code_tools", "web_tools"})
        assert "run_python" not in registry._tools
        assert "fetch_url" not in registry._tools
        assert "evaluate_expression" in registry._tools


class TestSchemaGeneration:
    def test_to_openai_format(self, registry):
        schema = registry.to_openai_format()
        assert isinstance(schema, list)
        assert len(schema) > 0

        # Check first item structure
        first = schema[0]
        assert "type" in first
        assert first["type"] == "function"
        assert "function" in first
        assert "name" in first["function"]
        assert "description" in first["function"]
        assert "parameters" in first["function"]
