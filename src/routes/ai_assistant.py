from flask import Blueprint, request, jsonify
import re
import os
from google import genai

bp = Blueprint('ai_assistant', __name__)

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

@bp.route('/ai-assistant', methods=['POST'])
def ai_assistant():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    exercise = data.get('exercise', '')

    try:
        prompt = f"""
        You are a focused coding assistant. The user provided the following {language} code and (optionally) exercise description.
        Your job: produce ONLY two parts, and nothing else:
        1) A single, concrete NEXT STEP the user should take to progress toward solving the exercise (one short sentence, or one short code edit suggestion). Do NOT provide a full solution, do NOT provide multiple steps.
        2) A short bullet list (at most 3 bullets) of likely errors, edge-cases, or bad practices that could cause problems if not addressed.

        Rules:
        - ALWAYS respond in English.
        - Output must be concise. First line = the single NEXT STEP. Follow with a blank line, then the bullets prefixed with a dash.
        - Do NOT generate unrelated code, do NOT rewrite the user's code, and do NOT include full implementations.
        - If you need context from the exercise, use the provided 'exercise' field; do NOT invent requirements.

        Context:
        Exercise: {exercise}
        User code:
        {code}
        """

        response = client.models.generate_content(
            model="models/gemini-2.5-pro",
            contents=[prompt]
        )
        ai_response = response.text.strip()
        ai_response = re.sub(r'^```[a-zA-Z]*\n', '', ai_response)
        ai_response = re.sub(r'\n```$', '', ai_response)
        
    except Exception as e:
        ai_response = f"Error calling Google AI: {str(e)}"

    return jsonify({
        "response": ai_response
    })

@bp.route('/ai-rival', methods=['POST'])
def ai_rival():
    data = request.get_json()
    exercise = data.get('exercise', '')
    language = data.get('language', 'python')
    difficulty = data.get('difficulty', 'easy')
    
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-pro",
            contents=[f"Create an implementation of the following coding exercise in {language}: {exercise}"]
        )
        ai_response = response.text
    except Exception as e:
        ai_response = f"Error calling Google AI: {str(e)}"

    return jsonify({
        "response": ai_response
    })