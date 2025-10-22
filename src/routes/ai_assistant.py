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

    try:
        prompt = f"""
            You are a coding assistant that reviews only the provided code and suggests improvements
            by inserting helpful comments directly above the relevant lines.

            Rules:
            - Always respond in English.
            - Do not generate new or unrelated code.
            - Do not translate or rephrase existing comments or code.
            - Only work with the provided code and add comments in place.

            Here is the user's {language} code:
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