from src.services.code_execution_service import execute_code, sanitize_error

class TestCodeExecutionService:
    def test_execute_python_success(self):
        code = "print('Hello, World!')"
        result = execute_code(code, "python")
        
        assert result["output"] == "Hello, World!"
        assert result["error"] is None

    def test_execute_python_no_output(self):
        code = "x = 5"
        result = execute_code(code, "python")
        
        assert result["output"] == "(no output)"
        assert result["error"] is None

    def test_execute_python_error(self):
        code = "print(undefined_variable)"
        result = execute_code(code, "python")
        
        assert result["output"] == "(no output)"
        assert result["error"] is not None
        assert "NameError" in result["error"]

    def test_execute_python_syntax_error(self):
        code = "print('unclosed string"
        result = execute_code(code, "python")
        
        assert result["error"] is not None
        assert "SyntaxError" in result["error"]

    def test_execute_javascript_success(self):
        code = "console.log('Hello, World!');"
        result = execute_code(code, "javascript")
        
        assert result["output"] == "Hello, World!"
        assert result["error"] is None

    def test_execute_javascript_no_output(self):
        code = "var x = 5;"
        result = execute_code(code, "javascript")
        
        assert result["output"] == "(no output)"
        assert result["error"] is None

    def test_execute_javascript_error(self):
        code = "console.log(undefinedVariable);"
        result = execute_code(code, "javascript")
        
        assert result["output"] == "(no output)"
        assert result["error"] is not None

    def test_execute_unsupported_language(self):
        code = "puts 'Hello'"
        result = execute_code(code, "ruby")
        
        assert result["output"] == ""
        assert result["error"] == "Unsupported language: ruby"

    def test_sanitize_error_with_paths(self):
        error = 'File "/usr/local/lib/python3.9/site.py", line 10, in <module>'
        sanitized = sanitize_error(error)
        
        assert "<path>" in sanitized
        assert "/usr/local/lib" not in sanitized

    def test_sanitize_error_with_tempfile(self):
        error = 'File "tmpabc123.py", line 5'
        sanitized = sanitize_error(error)
        
        assert "<tempfile>" in sanitized
        assert "tmpabc123.py" not in sanitized

    def test_sanitize_error_with_windows_paths(self):
        error = 'File "C:\\Users\\test\\file.py", line 1'
        sanitized = sanitize_error(error)
        
        assert "<path>" in sanitized
        assert "C:\\Users" not in sanitized

    def test_sanitize_error_empty(self):
        sanitized = sanitize_error("")
        assert sanitized == ""

    def test_sanitize_error_multiline(self):
        error = """Traceback (most recent call last):
  File "/tmp/test.py", line 1, in <module>
    print(x)
NameError: name 'x' is not defined"""
        
        sanitized = sanitize_error(error)
        assert "<path>" in sanitized
        assert "/tmp/test.py" not in sanitized
        assert "NameError" in sanitized

    def test_execute_code_timeout(self):
        code = "while True: pass"
        result = execute_code(code, "python")
        
        assert result["error"] is not None or result["output"] == "(no output)"