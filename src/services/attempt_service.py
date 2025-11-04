import subprocess
from sqlalchemy.orm import Session
from models.exercise import Exercise
from models.attempt import Attempt
from datetime import datetime, timezone
import tempfile
import os
import re
import json
import sys


def create_attempt(db: Session, user_id: int, exercise_id: int, code: str) -> Attempt:
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise ValueError(f"Exercise with id {exercise_id} not found")

    attempt = Attempt(
        user_id=user_id,
        exercise_id=exercise_id,
        code_submitted=code,
        attempted_at=datetime.now(timezone.utc)
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    grade_result = grade_submission(code, exercise)
    attempt.score = grade_result["style_score"]
    attempt.stars = grade_result["stars"]
    
    db.commit()
    db.refresh(attempt)
    return attempt


def grade_submission(code: str, exercise) -> dict:
    language = exercise.language.lower()
    if language == "python":
        grader = grade_python_attempt
    elif language == "javascript":
        grader = grade_javascript_attempt
    else:
        raise ValueError(f"Unsupported language: {exercise.language}")
    return grader(code, exercise.function_name, exercise.test_cases)


# ---------------------- Generic helpers ----------------------

def run_temp_file(command: list[str], content: str, suffix: str, timeout: int = 5):
    """Writes content to a temp file, runs a subprocess command, and cleans up."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode='w')
    tmp_name = tmp.name
    try:
        tmp.write(content)
        tmp.flush()
        tmp.close()
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            text=True
        )
        return result
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        print(f"Error during subprocess: {e}")
        return None
    finally:
        try:
            os.unlink(tmp_name)
        except PermissionError:
            pass


def extract_test_results(output: str, test_cases_count: int) -> tuple[int, int]:
    """Parses test result summary like 'RESULTS: 3/5'."""
    if not output or "RESULTS:" not in output:
        return 0, test_cases_count
    try:
        line = next(line for line in output.splitlines() if "RESULTS:" in line)
        passed_str = line.split("RESULTS:")[1].strip()
        passed, total = map(int, passed_str.split("/"))
        return passed, total
    except Exception:
        return 0, test_cases_count


def calculate_stars(test_pass_rate: float, style_score: float) -> int:
    if test_pass_rate < 1.0:
        return 0
    if style_score >= 8.0:
        return 3
    if style_score >= 6.0:
        return 2
    return 1


# ---------------------- Python grading ----------------------

def grade_python_attempt(code: str, function_name: str, test_cases_json: str) -> dict:
    test_cases = json.loads(test_cases_json)
    test_code = code + "\n\npassed = 0\ntotal = 0\n\n"

    for i, test in enumerate(test_cases):
        args = ", ".join(repr(a) for a in test["args"])
        expected = repr(test["expected"])
        test_code += f"""
try:
    result = {function_name}({args})
    expected = {expected}
    total += 1
    if result == expected:
        passed += 1
        print(f"Test {i+1}: PASSED")
    else:
        print(f"Test {i+1}: FAILED - Expected {{expected}}, got {{result}}")
except Exception as e:
    total += 1
    print(f"Test {i+1}: ERROR - {{str(e)}}")
"""
    test_code += '\nprint(f"RESULTS: {passed}/{total}")\n'

    result = run_temp_file([sys.executable, "temp.py"], test_code, ".py")
    output = result.stdout if result else ""
    passed, total = extract_test_results(output, len(test_cases))

    test_pass_rate = passed / total if total > 0 else 0.0
    pylint_score, pylint_feedback = run_pylint(code)
    stars = calculate_stars(test_pass_rate, pylint_score)

    return {
        "test_pass_rate": test_pass_rate,
        "style_score": pylint_score,
        "stars": stars,
        "feedback": pylint_feedback,
        "tests_passed": passed,
        "tests_total": total
    }


def run_pylint(code: str) -> tuple[float, str]:
    result = run_temp_file(
        [
            "pylint", "--score=y",
            "--disable=C0114,C0116,C0304,C0103",
            "--max-line-length=120", "temp.py"
        ],
        code, ".py", timeout=10
    )
    output = result.stdout if result else ""
    match = re.search(r"rated at ([\d\.]+)/10", output)
    score = float(match.group(1)) if match else 0.0
    return score, output


# ---------------------- JavaScript grading ----------------------

def grade_javascript_attempt(code: str, function_name: str, test_cases_json: str) -> dict:
    test_cases = json.loads(test_cases_json)
    test_code = code + "\n\nlet passed = 0;\nlet total = 0;\n\n"

    for i, test in enumerate(test_cases):
        args = ", ".join(json.dumps(a) for a in test["args"])
        expected = json.dumps(test["expected"])
        test_code += f"""
try {{
    const result = {function_name}({args});
    const expected = {expected};
    total++;
    if (JSON.stringify(result) === JSON.stringify(expected)) {{
        passed++;
        console.log(`Test {i+1}: PASSED`);
    }} else {{
        console.log(`Test {i+1}: FAILED - Expected ${{expected}}, got ${{result}}`);
    }}
}} catch (e) {{
    total++;
    console.log(`Test {i+1}: ERROR - ${{e.message}}`);
}}
"""
    test_code += '\nconsole.log(`RESULTS: ${passed}/${total}`);\n'

    result = run_temp_file(["node", "temp.js"], test_code, ".js")
    output = result.stdout if result else ""
    passed, total = extract_test_results(output, len(test_cases))

    test_pass_rate = passed / total if total > 0 else 0.0
    eslint_score, eslint_feedback = run_eslint(code)
    stars = calculate_stars(test_pass_rate, eslint_score)

    return {
        "test_pass_rate": test_pass_rate,
        "style_score": eslint_score,
        "stars": stars,
        "feedback": eslint_feedback,
        "tests_passed": passed,
        "tests_total": total
    }


def run_eslint(code: str) -> tuple[float, str]:
    result = run_temp_file(
        [
            "npx", "eslint", "--format", "json",
            "--no-eslintrc",
            "--rule", "semi: off",
            "--rule", "quotes: off",
            "temp.js"
        ],
        code, ".js", timeout=10
    )
    output = result.stdout if result else ""
    try:
        reports = json.loads(output)
        messages = reports[0].get("messages", [])
        errors = sum(1 for m in messages if m["severity"] == 2)
        warnings = sum(1 for m in messages if m["severity"] == 1)
    except Exception:
        errors = warnings = 10

    score = max(0.0, 10 - errors * 1.5 - warnings * 0.5)
    return round(score, 2), output