from flask import Blueprint, request, jsonify
import subprocess
import tempfile
import re
import os

bp = Blueprint('code_execution', __name__)

def sanitize_error(raw_error: str) -> str:
    sanitized = re.sub(r'([A-Z]:)?[/\\][\w./\\-]+', '<path>', raw_error)
    sanitized = re.sub(r'tmp[a-zA-Z0-9_]+\.py', '<tempfile>', sanitized)
    sanitized = sanitized.replace(os.getcwd(), '<cwd>')
    sanitized = "\n".join([line for line in sanitized.splitlines() if line.strip()])
    return sanitized.strip()

@bp.route('/execute', methods=['POST'])
def execute_code():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')

    try:
        if language == 'python':
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
                tmp.write(code.encode('utf-8'))
                tmp.flush()
                result = subprocess.run(
                    ['python', tmp.name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5
                )
            os.unlink(tmp.name)

        elif language == 'javascript':
            with tempfile.NamedTemporaryFile(delete=False, suffix=".js") as tmp:
                tmp.write(code.encode('utf-8'))
                tmp.flush()
                result = subprocess.run(
                    ['node', tmp.name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5
                )
            os.unlink(tmp.name)

        else:
            return jsonify({"output": "", "error": f"Unsupported language: {language}"})

        output = result.stdout.decode('utf-8')
        error = sanitize_error(result.stderr.decode('utf-8'))
        
        return jsonify({
            "output": output.strip() if output.strip() else "(no output)",
            "error": sanitize_error(error) if error.strip() else None
        })

    except subprocess.TimeoutExpired:
        return jsonify({"output": "", "error": "Execution timed out (max 5s)."})
    except Exception as e:
        return jsonify({"output": "", "error": str(e)})