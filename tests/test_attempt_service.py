import pytest
import json
from unittest.mock import patch, MagicMock
from src.services.attempt_service import (
    create_attempt,
    grade_submission,
    run_temp_file,
    extract_test_results,
    calculate_stars,
    grade_python_attempt,
    run_pylint,
    grade_javascript_attempt,
    run_eslint
)
from src.models.exercise import Exercise
from src.models.attempt import Attempt

class TestAttemptService:
    def test_create_attempt_exercise_not_found(self, test_db):
        with pytest.raises(ValueError, match="Exercise with id 99999 not found"):
            create_attempt(test_db, 1, 99999, "code")

    @patch('services.attempt_service.grade_submission')
    def test_create_attempt_success(self, mock_grade, test_db, sample_user, sample_exercise):
        mock_grade.return_value = {"style_score": 8, "stars": 2}
        
        attempt = create_attempt(test_db, sample_user.id, sample_exercise.id, "def test(): pass")
        
        assert attempt is not None
        assert attempt.user_id == sample_user.id
        assert attempt.exercise_id == sample_exercise.id
        assert attempt.score == 8
        assert attempt.stars == 2

    def test_grade_submission_python(self, test_db, sample_exercise):
        sample_exercise.language = "python"
        
        with patch('services.attempt_service.grade_python_attempt') as mock:
            mock.return_value = {"style_score": 10, "stars": 3}
            result = grade_submission("code", sample_exercise)
            
            assert result["style_score"] == 10
            assert result["stars"] == 3
            mock.assert_called_once()

    def test_grade_submission_javascript(self, test_db, sample_exercise):
        sample_exercise.language = "javascript"
        
        with patch('services.attempt_service.grade_javascript_attempt') as mock:
            mock.return_value = {"style_score": 10, "stars": 3}
            result = grade_submission("code", sample_exercise)
            
            assert result["style_score"] == 10
            assert result["stars"] == 3
            mock.assert_called_once()

    def test_grade_submission_unsupported_language(self, test_db, sample_exercise):
        sample_exercise.language = "ruby"
        
        with pytest.raises(ValueError, match="Unsupported language: ruby"):
            grade_submission("code", sample_exercise)

    def test_extract_test_results_success(self):
        output = "Test 1: PASSED\nTest 2: FAILED\nRESULTS: 3/5"
        passed, total = extract_test_results(output, 5)
        
        assert passed == 3
        assert total == 5

    def test_extract_test_results_no_results(self):
        output = "Some other output"
        passed, total = extract_test_results(output, 5)
        
        assert passed == 0
        assert total == 5

    def test_extract_test_results_empty_output(self):
        passed, total = extract_test_results("", 5)
        
        assert passed == 0
        assert total == 5

    def test_extract_test_results_invalid_format(self):
        output = "RESULTS: invalid"
        passed, total = extract_test_results(output, 5)
        
        assert passed == 0
        assert total == 5

    def test_calculate_stars_all_tests_failed(self):
        stars = calculate_stars(0.5, 10.0)
        assert stars == 0

    def test_calculate_stars_all_passed_high_style(self):
        stars = calculate_stars(1.0, 8.5)
        assert stars == 3

    def test_calculate_stars_all_passed_medium_style(self):
        stars = calculate_stars(1.0, 7.0)
        assert stars == 2

    def test_calculate_stars_all_passed_low_style(self):
        stars = calculate_stars(1.0, 5.0)
        assert stars == 1

    @patch('subprocess.run')
    def test_run_temp_file_success(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="output",
            stderr="",
            returncode=0
        )
        
        result = run_temp_file(["python", "temp.py"], "print('test')", ".py")
        
        assert result is not None
        assert result.stdout == "output"

    @patch('subprocess.run')
    def test_run_temp_file_timeout(self, mock_run):
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 5)
        
        result = run_temp_file(["python", "temp.py"], "while True: pass", ".py")
        assert result is None

    @patch('subprocess.run')
    def test_run_temp_file_exception(self, mock_run):
        mock_run.side_effect = Exception("Test error")
        
        result = run_temp_file(["python", "temp.py"], "code", ".py")
        assert result is None

    @patch('services.attempt_service.run_temp_file')
    @patch('services.attempt_service.run_pylint')
    def test_grade_python_attempt_all_pass(self, mock_pylint, mock_run):
        mock_run.return_value = MagicMock(stdout="Test 1: PASSED\nRESULTS: 1/1")
        mock_pylint.return_value = (10.0, "Perfect!")
        
        test_cases = [{"args": [1, 2], "expected": 3}]
        result = grade_python_attempt("def add(a, b): return a + b", "add", json.dumps(test_cases))
        
        assert result["tests_passed"] == 1
        assert result["tests_total"] == 1
        assert result["test_pass_rate"] == 1.0
        assert result["style_score"] == 10.0
        assert result["stars"] == 3

    @patch('services.attempt_service.run_temp_file')
    @patch('services.attempt_service.run_pylint')
    def test_grade_python_attempt_partial_pass(self, mock_pylint, mock_run):
        mock_run.return_value = MagicMock(stdout="Test 1: PASSED\nTest 2: FAILED\nRESULTS: 1/2")
        mock_pylint.return_value = (8.0, "Good")
        
        test_cases = [{"args": [1], "expected": 1}, {"args": [2], "expected": 2}]
        result = grade_python_attempt("code", "func", json.dumps(test_cases))
        
        assert result["tests_passed"] == 1
        assert result["tests_total"] == 2
        assert result["test_pass_rate"] == 0.5
        assert result["stars"] == 0

    @patch('services.attempt_service.run_temp_file')
    @patch('services.attempt_service.run_pylint')
    def test_grade_python_attempt_no_output(self, mock_pylint, mock_run):
        mock_run.return_value = None
        mock_pylint.return_value = (0.0, "")
        
        test_cases = [{"args": [], "expected": 1}]
        result = grade_python_attempt("code", "func", json.dumps(test_cases))
        
        assert result["tests_passed"] == 0
        assert result["stars"] == 0

    @patch('services.attempt_service.run_temp_file')
    def test_run_pylint_success(self, mock_run):
        mock_run.return_value = MagicMock(stdout="Your code has been rated at 8.5/10")
        
        score, feedback = run_pylint("def test(): pass")
        
        assert score == 8.5
        assert "8.5/10" in feedback

    @patch('services.attempt_service.run_temp_file')
    def test_run_pylint_no_score(self, mock_run):
        mock_run.return_value = MagicMock(stdout="No score found")
        
        score, feedback = run_pylint("code")
        
        assert score == 0.0

    @patch('services.attempt_service.run_temp_file')
    def test_run_pylint_none_result(self, mock_run):
        mock_run.return_value = None
        
        score, feedback = run_pylint("code")
        
        assert score == 0.0
        assert feedback == ""

    @patch('services.attempt_service.run_temp_file')
    @patch('services.attempt_service.run_eslint')
    def test_grade_javascript_attempt_all_pass(self, mock_eslint, mock_run):
        mock_run.return_value = MagicMock(stdout="Test 1: PASSED\nRESULTS: 1/1")
        mock_eslint.return_value = (10.0, "{}")
        
        test_cases = [{"args": [1, 2], "expected": 3}]
        result = grade_javascript_attempt("function add(a, b) { return a + b; }", "add", json.dumps(test_cases))
        
        assert result["tests_passed"] == 1
        assert result["tests_total"] == 1
        assert result["test_pass_rate"] == 1.0
        assert result["stars"] == 3

    @patch('services.attempt_service.run_temp_file')
    @patch('services.attempt_service.run_eslint')
    def test_grade_javascript_attempt_partial_pass(self, mock_eslint, mock_run):
        mock_run.return_value = MagicMock(stdout="Test 1: PASSED\nTest 2: FAILED\nRESULTS: 1/2")
        mock_eslint.return_value = (7.0, "{}")
        
        test_cases = [{"args": [1], "expected": 1}, {"args": [2], "expected": 2}]
        result = grade_javascript_attempt("code", "func", json.dumps(test_cases))
        
        assert result["tests_passed"] == 1
        assert result["tests_total"] == 2
        assert result["stars"] == 0

    @patch('services.attempt_service.run_temp_file')
    def test_run_eslint_success(self, mock_run):
        eslint_output = json.dumps([{
            "messages": [
                {"severity": 2},
                {"severity": 1}
            ]
        }])
        mock_run.return_value = MagicMock(stdout=eslint_output)
        
        score, feedback = run_eslint("function test() {}")
        
        assert score == 8.0
        assert feedback == eslint_output

    @patch('services.attempt_service.run_temp_file')
    def test_run_eslint_many_errors(self, mock_run):
        """Test running eslint with many errors."""
        eslint_output = json.dumps([{
            "messages": [{"severity": 2}] * 10
        }])
        mock_run.return_value = MagicMock(stdout=eslint_output)
        
        score, feedback = run_eslint("bad code")
        
        assert score == 0.0

    @patch('services.attempt_service.run_temp_file')
    def test_run_eslint_invalid_json(self, mock_run):
        """Test running eslint with invalid JSON."""
        mock_run.return_value = MagicMock(stdout="Invalid JSON")
        
        score, feedback = run_eslint("code")
        
        assert score == 0.0

    @patch('services.attempt_service.run_temp_file')
    def test_run_eslint_none_result(self, mock_run):
        mock_run.return_value = None
        
        score, feedback = run_eslint("code")
        
        assert score == 0.0
        assert feedback == ""