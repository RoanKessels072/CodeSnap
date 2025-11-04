import subprocess, tempfile, os, re

def sanitize_error(raw_error: str) -> str:
    sanitized = re.sub(r'([A-Z]:)?[/\\][\w./\\-]+', '<path>', raw_error)
    sanitized = re.sub(r'tmp[a-zA-Z0-9_]+\.py', '<tempfile>', sanitized)
    sanitized = sanitized.replace(os.getcwd(), '<cwd>')
    return "\n".join([line for line in sanitized.splitlines() if line.strip()]).strip()

def execute_code(code: str, language: str):
    if language not in ['python', 'javascript']:
        return {"output": "", "error": f"Unsupported language: {language}"}

    suffix = ".py" if language == "python" else ".js"
    runner = ["python"] if language == "python" else ["node"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(code.encode('utf-8'))
        tmp.flush()
        try:
            result = subprocess.run(
                runner + [tmp.name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
        finally:
            os.unlink(tmp.name)

    return {
        "output": result.stdout.decode('utf-8').strip() or "(no output)",
        "error": sanitize_error(result.stderr.decode('utf-8').strip()) or None
    }
