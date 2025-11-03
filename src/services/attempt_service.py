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
        return grade_python_attempt(
            code=code,
            function_name=exercise.function_name,
            test_cases_json=exercise.test_cases
        )
    elif language == "javascript":
        return grade_javascript_attempt(
            code=code,
            function_name=exercise.function_name,
            test_cases_json=exercise.test_cases
        )
    else:
        raise ValueError(f"Unsupported language: {exercise.language}")


def grade_python_attempt(code: str, function_name: str, test_cases_json: str) -> dict:
    test_cases = json.loads(test_cases_json)
    python_executable = sys.executable
    
    test_code = code + "\n\n"
    test_code += "passed = 0\ntotal = 0\n\n"
    
    for i, test in enumerate(test_cases):
        args_str = ", ".join(repr(arg) for arg in test["args"])
        expected = repr(test["expected"])
        
        test_code += f"""
try:
    result = {function_name}({args_str})
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
    
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w')
    tmp_name = tmp.name
    
    try:
        tmp.write(test_code)
        tmp.flush()
        tmp.close()
        
        try:
            result = subprocess.run(
                [python_executable, tmp_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
                text=True
            )
            output = result.stdout
            
            if "RESULTS:" in output:
                results_line = [line for line in output.split('\n') if 'RESULTS:' in line][0]
                passed_str = results_line.split('RESULTS:')[1].strip()
                passed, total = map(int, passed_str.split('/'))
            else:
                passed, total = 0, len(test_cases)
                
        except subprocess.TimeoutExpired:
            passed, total = 0, len(test_cases)
        except Exception as e:
            print(f"Error running tests: {e}")
            passed, total = 0, len(test_cases)
    finally:
        try:
            os.unlink(tmp_name)
        except PermissionError:
            pass
    
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
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w')
    tmp_name = tmp.name
    
    try:
        tmp.write(code)
        tmp.flush()
        tmp.close()

        result = subprocess.run(
            [
                "pylint",
                "--score=y",
                "--disable=C0114,C0116,C0304,C0103",
                "--max-line-length=120",
                tmp_name
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    finally:
        try:
            os.unlink(tmp_name)
        except PermissionError:
            pass

    match = re.search(r"rated at ([\d\.]+)/10", result.stdout)
    score = float(match.group(1)) if match else 0.0
    feedback = result.stdout
    
    return score, feedback

def grade_javascript_attempt(code: str, function_name: str, test_cases_json: str) -> dict:
    test_cases = json.loads(test_cases_json)
    
    test_code = code + "\n\n"
    test_code += "let passed = 0;\nlet total = 0;\n\n"
    
    for i, test in enumerate(test_cases):
        args_str = ", ".join(json.dumps(arg) for arg in test["args"])
        expected = json.dumps(test["expected"])
        
        test_code += f"""
try {{
    const result = {function_name}({args_str});
    const expected = {expected};
    total += 1;
    if (JSON.stringify(result) === JSON.stringify(expected)) {{
        passed += 1;
        console.log(`Test {i+1}: PASSED`);
    }} else {{
        console.log(`Test {i+1}: FAILED - Expected ${{expected}}, got ${{result}}`);
    }}
}} catch (e) {{
    total += 1;
    console.log(`Test {i+1}: ERROR - ${{e.message}}`);
}}
"""
    
    test_code += '\nconsole.log(`RESULTS: ${passed}/${total}`);\n'
    
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".js", mode='w')
    tmp_name = tmp.name
    
    try:
        tmp.write(test_code)
        tmp.flush()
        tmp.close()
        
        try:
            result = subprocess.run(
                ["node", tmp_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
                text=True
            )
            output = result.stdout
            
            if "RESULTS:" in output:
                results_line = [line for line in output.split('\n') if 'RESULTS:' in line][0]
                passed_str = results_line.split('RESULTS:')[1].strip()
                passed, total = map(int, passed_str.split('/'))
            else:
                passed, total = 0, len(test_cases)
                
        except subprocess.TimeoutExpired:
            passed, total = 0, len(test_cases)
        except Exception as e:
            print(f"Error running tests: {e}")
            passed, total = 0, len(test_cases)
    finally:
        try:
            os.unlink(tmp_name)
        except PermissionError:
            pass
    
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
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".js", mode='w')
    tmp_name = tmp.name
    
    try:
        tmp.write(code)
        tmp.flush()
        tmp.close()

        result = subprocess.run(
            [
                "npx", "eslint",
                "--format", "json",
                "--no-eslintrc",
                "--rule", "semi: off",
                "--rule", "quotes: off",
                tmp_name
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    finally:
        try:
            os.unlink(tmp_name)
        except PermissionError:
            pass

    try:
        reports = json.loads(result.stdout)
        messages = reports[0].get("messages", [])
        errors = sum(1 for m in messages if m["severity"] == 2)
        warnings = sum(1 for m in messages if m["severity"] == 1)
    except Exception:
        errors = warnings = 10
        messages = []

    score = max(0.0, 10 - errors * 1.5 - warnings * 0.5)
    feedback = result.stdout
    
    return round(score, 2), feedback


def calculate_stars(test_pass_rate: float, style_score: float) -> int:
    stars = 0
    if test_pass_rate >= 1.0:
        stars = 1
        if style_score >= 6.0:
            stars = 2
        if style_score >= 8.0:
            stars = 3
    return stars