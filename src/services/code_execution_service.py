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

    # Create temp file with delete=False to handle Windows file locking
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8')
    tmp_name = tmp.name
    
    try:
        # Write and close file before subprocess uses it (Windows requirement)
        tmp.write(code)
        tmp.close()
        
        # Now run the subprocess
        result = subprocess.run(
            runner + [tmp_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        
        return {
            "output": result.stdout.decode('utf-8').strip() or "(no output)",
            "error": sanitize_error(result.stderr.decode('utf-8').strip()) or None
        }
    except subprocess.TimeoutExpired:
        return {
            "output": "(no output)",
            "error": "Execution timed out"
        }
    except Exception as e:
        return {
            "output": "(no output)",
            "error": f"Execution error: {str(e)}"
        }
    finally:
        # Clean up: remove temp file
        try:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
        except PermissionError:
            # On Windows, file might still be locked
            # Try again after a short delay
            import time
            time.sleep(0.1)
            try:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
            except:
                pass