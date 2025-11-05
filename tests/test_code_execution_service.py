import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from unittest.mock import patch, MagicMock, mock_open, call
import subprocess

class TestCodeExecutionService:
    @patch('services.code_execution_service.os.path.exists')
    @patch('services.code_execution_service.os.unlink')
    @patch('services.code_execution_service.subprocess.run')
    @patch('services.code_execution_service.tempfile.NamedTemporaryFile')
    def test_execute_python_success(self, mock_tempfile, mock_run, mock_unlink, mock_exists):
        from services.code_execution_service import execute_code
        
        mock_file = MagicMock()
        mock_file.name = 'test_temp.py'
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file
        
        mock_result = MagicMock()
        mock_result.stdout = b'Hello, World!'
        mock_result.stderr = b''
        mock_run.return_value = mock_result
        
        mock_exists.return_value = True
        
        code = "print('Hello, World!')"
        result = execute_code(code, "python")
        
        assert result["output"] == "Hello, World!"
        assert result["error"] is None
        mock_file.write.assert_called_once_with(code)
        mock_file.close.assert_called_once()

    @patch('services.code_execution_service.os.path.exists')
    @patch('services.code_execution_service.os.unlink')
    @patch('services.code_execution_service.subprocess.run')
    @patch('services.code_execution_service.tempfile.NamedTemporaryFile')
    def test_execute_python_no_output(self, mock_tempfile, mock_run, mock_unlink, mock_exists):
        from services.code_execution_service import execute_code
        
        mock_file = MagicMock()
        mock_file.name = 'test_temp.py'
        mock_tempfile.return_value = mock_file
        
        mock_result = MagicMock()
        mock_result.stdout = b''
        mock_result.stderr = b''
        mock_run.return_value = mock_result
        
        mock_exists.return_value = True
        
        code = "x = 5"
        result = execute_code(code, "python")
        
        assert result["output"] == "(no output)"
        assert result["error"] is None

    @patch('services.code_execution_service.os.path.exists')
    @patch('services.code_execution_service.os.unlink')
    @patch('services.code_execution_service.subprocess.run')
    @patch('services.code_execution_service.tempfile.NamedTemporaryFile')
    def test_execute_python_error(self, mock_tempfile, mock_run, mock_unlink, mock_exists):
        from services.code_execution_service import execute_code
        
        mock_file = MagicMock()
        mock_file.name = 'test_temp.py'
        mock_tempfile.return_value = mock_file
        
        mock_result = MagicMock()
        mock_result.stdout = b''
        mock_result.stderr = b'NameError: name "undefined_variable" is not defined'
        mock_run.return_value = mock_result
        
        mock_exists.return_value = True
        
        code = "print(undefined_variable)"
        result = execute_code(code, "python")
        
        assert result["output"] == "(no output)"
        assert result["error"] is not None
        assert "NameError" in result["error"]

    @patch('services.code_execution_service.os.path.exists')
    @patch('services.code_execution_service.os.unlink')
    @patch('services.code_execution_service.subprocess.run')
    @patch('services.code_execution_service.tempfile.NamedTemporaryFile')
    def test_execute_python_syntax_error(self, mock_tempfile, mock_run, mock_unlink, mock_exists):
        from services.code_execution_service import execute_code
        
        mock_file = MagicMock()
        mock_file.name = 'test_temp.py'
        mock_tempfile.return_value = mock_file
        
        mock_result = MagicMock()
        mock_result.stdout = b''
        mock_result.stderr = b'SyntaxError: unterminated string literal'
        mock_run.return_value = mock_result
        
        mock_exists.return_value = True
        
        code = "print('unclosed string"
        result = execute_code(code, "python")
        
        assert result["error"] is not None
        assert "SyntaxError" in result["error"]

    @patch('services.code_execution_service.os.path.exists')
    @patch('services.code_execution_service.os.unlink')
    @patch('services.code_execution_service.subprocess.run')
    @patch('services.code_execution_service.tempfile.NamedTemporaryFile')
    def test_execute_javascript_success(self, mock_tempfile, mock_run, mock_unlink, mock_exists):
        from services.code_execution_service import execute_code
        
        mock_file = MagicMock()
        mock_file.name = 'test_temp.js'
        mock_tempfile.return_value = mock_file
        
        mock_result = MagicMock()
        mock_result.stdout = b'Hello, World!'
        mock_result.stderr = b''
        mock_run.return_value = mock_result
        
        mock_exists.return_value = True
        
        code = "console.log('Hello, World!');"
        result = execute_code(code, "javascript")
        
        assert result["output"] == "Hello, World!"
        assert result["error"] is None

    @patch('services.code_execution_service.os.path.exists')
    @patch('services.code_execution_service.os.unlink')
    @patch('services.code_execution_service.subprocess.run')
    @patch('services.code_execution_service.tempfile.NamedTemporaryFile')
    def test_execute_javascript_no_output(self, mock_tempfile, mock_run, mock_unlink, mock_exists):
        from services.code_execution_service import execute_code
        
        mock_file = MagicMock()
        mock_file.name = 'test_temp.js'
        mock_tempfile.return_value = mock_file
        
        mock_result = MagicMock()
        mock_result.stdout = b''
        mock_result.stderr = b''
        mock_run.return_value = mock_result
        
        mock_exists.return_value = True
        
        code = "var x = 5;"
        result = execute_code(code, "javascript")
        
        assert result["output"] == "(no output)"
        assert result["error"] is None

    @patch('services.code_execution_service.os.path.exists')
    @patch('services.code_execution_service.os.unlink')
    @patch('services.code_execution_service.subprocess.run')
    @patch('services.code_execution_service.tempfile.NamedTemporaryFile')
    def test_execute_javascript_error(self, mock_tempfile, mock_run, mock_unlink, mock_exists):
        from services.code_execution_service import execute_code
        
        mock_file = MagicMock()
        mock_file.name = 'test_temp.js'
        mock_tempfile.return_value = mock_file
        
        mock_result = MagicMock()
        mock_result.stdout = b''
        mock_result.stderr = b'ReferenceError: undefinedVariable is not defined'
        mock_run.return_value = mock_result
        
        mock_exists.return_value = True
        
        code = "console.log(undefinedVariable);"
        result = execute_code(code, "javascript")
        
        assert result["output"] == "(no output)"
        assert result["error"] is not None

    def test_execute_unsupported_language(self):
        from services.code_execution_service import execute_code
        
        code = "puts 'Hello'"
        result = execute_code(code, "ruby")
        
        assert result["output"] == ""
        assert result["error"] == "Unsupported language: ruby"

    @patch('services.code_execution_service.os.path.exists')
    @patch('services.code_execution_service.os.unlink')
    @patch('services.code_execution_service.subprocess.run')
    @patch('services.code_execution_service.tempfile.NamedTemporaryFile')
    def test_execute_code_timeout(self, mock_tempfile, mock_run, mock_unlink, mock_exists):
        from services.code_execution_service import execute_code
        
        mock_file = MagicMock()
        mock_file.name = 'test_temp.py'
        mock_tempfile.return_value = mock_file
        
        mock_run.side_effect = subprocess.TimeoutExpired('python', 5)
        mock_exists.return_value = True
        
        code = "while True: pass"
        result = execute_code(code, "python")
        
        assert result["error"] is not None
        assert "timed out" in result["error"].lower()

    def test_sanitize_error_with_paths(self):
        from services.code_execution_service import sanitize_error
        
        error = 'File "/usr/local/lib/python3.9/site.py", line 10, in <module>'
        sanitized = sanitize_error(error)
        
        assert "<path>" in sanitized
        assert "/usr/local/lib" not in sanitized

    def test_sanitize_error_with_tempfile(self):
        from services.code_execution_service import sanitize_error
        
        error = 'File "tmpabc123.py", line 5'
        sanitized = sanitize_error(error)
        
        assert "<tempfile>" in sanitized
        assert "tmpabc123.py" not in sanitized

    def test_sanitize_error_with_windows_paths(self):
        from services.code_execution_service import sanitize_error
        
        error = 'File "C:\\Users\\test\\file.py", line 1'
        sanitized = sanitize_error(error)
        
        assert "<path>" in sanitized
        assert "C:\\Users" not in sanitized

    def test_sanitize_error_empty(self):
        from services.code_execution_service import sanitize_error
        
        sanitized = sanitize_error("")
        assert sanitized == ""

    def test_sanitize_error_multiline(self):
        from services.code_execution_service import sanitize_error
        
        error = """Traceback (most recent call last):
  File "/tmp/test.py", line 1, in <module>
    print(x)
NameError: name 'x' is not defined"""
        
        sanitized = sanitize_error(error)
        assert "<path>" in sanitized
        assert "/tmp/test.py" not in sanitized
        assert "NameError" in sanitized