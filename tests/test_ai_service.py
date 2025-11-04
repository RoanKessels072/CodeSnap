from unittest.mock import patch, MagicMock
from src.services.ai_service import get_ai_assistant_feedback, generate_ai_rival

class TestAIAssistantService:
    @patch('services.ai_assistant_service.client.models.generate_content')
    def test_get_ai_assistant_feedback_success(self, mock_generate):
        mock_response = MagicMock()
        mock_response.text = "# Next step: Add return statement\n# - Check for edge cases"
        mock_generate.return_value = mock_response
        
        result = get_ai_assistant_feedback(
            code="def add(a, b): pass",
            language="python",
            exercise_name="Add Numbers",
            description="Add two numbers",
            reference_solution="def add(a, b): return a + b"
        )
        
        assert "Next step" in result
        mock_generate.assert_called_once()

    @patch('services.ai_assistant_service.client.models.generate_content')
    def test_get_ai_assistant_feedback_strips_code_blocks(self, mock_generate):
        mock_response = MagicMock()
        mock_response.text = "```python\n# Comment\n```"
        mock_generate.return_value = mock_response
        
        result = get_ai_assistant_feedback(
            code="code",
            language="python",
            exercise_name="Test",
            description="Test",
            reference_solution="solution"
        )
        
        assert "```" not in result
        assert "# Comment" in result

    @patch('services.ai_assistant_service.client.models.generate_content')
    def test_get_ai_assistant_feedback_with_language_tag(self, mock_generate):
        mock_response = MagicMock()
        mock_response.text = "```javascript\nconsole.log('test');\n```"
        mock_generate.return_value = mock_response
        
        result = get_ai_assistant_feedback(
            code="code",
            language="javascript",
            exercise_name="Test",
            description="Test",
            reference_solution="solution"
        )
        
        assert "```" not in result
        assert "console.log('test');" in result

    @patch('services.ai_assistant_service.client.models.generate_content')
    def test_generate_ai_rival_easy_difficulty(self, mock_generate):
        mock_response = MagicMock()
        mock_response.text = "def add(a, b):\n    return a + b + 1  # Intentional mistake"
        mock_generate.return_value = mock_response
        
        result = generate_ai_rival(
            language="python",
            exercise_name="Add Numbers",
            description="Add two numbers",
            difficulty="easy"
        )
        
        assert "def add" in result
        mock_generate.assert_called_once()

    @patch('services.ai_assistant_service.client.models.generate_content')
    def test_generate_ai_rival_medium_difficulty(self, mock_generate):
        mock_response = MagicMock()
        mock_response.text = "function reverse(str) { return str.split('').reverse().join(''); }"
        mock_generate.return_value = mock_response
        
        result = generate_ai_rival(
            language="javascript",
            exercise_name="Reverse String",
            description="Reverse a string",
            difficulty="medium"
        )
        
        assert "function reverse" in result
        mock_generate.assert_called_once()

    @patch('services.ai_assistant_service.client.models.generate_content')
    def test_generate_ai_rival_hard_difficulty(self, mock_generate):
        mock_response = MagicMock()
        mock_response.text = "```python\ndef fibonacci(n):\n    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)\n```"
        mock_generate.return_value = mock_response
        
        result = generate_ai_rival(
            language="python",
            exercise_name="Fibonacci",
            description="Calculate fibonacci",
            difficulty="hard"
        )
        
        assert "```" not in result
        assert "def fibonacci" in result

    @patch('services.ai_assistant_service.client.models.generate_content')
    def test_generate_ai_rival_strips_trailing_newlines(self, mock_generate):
        mock_response = MagicMock()
        mock_response.text = "code\n\n\n"
        mock_generate.return_value = mock_response
        
        result = generate_ai_rival(
            language="python",
            exercise_name="Test",
            description="Test",
            difficulty="easy"
        )
        
        assert result == "code"

    @patch('services.ai_assistant_service.client.models.generate_content')
    def test_ai_assistant_includes_all_context(self, mock_generate):
        mock_response = MagicMock()
        mock_response.text = "feedback"
        mock_generate.return_value = mock_response
        
        get_ai_assistant_feedback(
            code="test_code",
            language="python",
            exercise_name="Test Exercise",
            description="Test Description",
            reference_solution="test_solution"
        )
        
        call_args = mock_generate.call_args
        prompt = call_args[1]['contents'][0]
        
        assert "test_code" in prompt
        assert "python" in prompt
        assert "Test Exercise" in prompt
        assert "Test Description" in prompt
        assert "test_solution" in prompt

    @patch('services.ai_assistant_service.client.models.generate_content')
    def test_ai_rival_includes_difficulty_context(self, mock_generate):
        mock_response = MagicMock()
        mock_response.text = "code"
        mock_generate.return_value = mock_response
        
        generate_ai_rival(
            language="javascript",
            exercise_name="Test",
            description="Description",
            difficulty="medium"
        )
        
        call_args = mock_generate.call_args
        prompt = call_args[1]['contents'][0]
        
        assert "medium" in prompt
        assert "javascript" in prompt
        assert "Test" in prompt