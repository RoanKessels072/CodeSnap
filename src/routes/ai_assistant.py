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
    exercise_name = data.get('exercise_name', '')
    exercise_description = data.get('exercise_description', '')
    reference_solution = data.get('reference_solution', '')

    try:
        prompt = f"""
        You are a coding assistant. The user is working on a coding exercise.

        Instructions:
        - Review the provided code and the exercise reference solution.
        - Suggest **ONLY ONE NEXT STEP or hint** that helps the user progress toward the reference solution.
        - Also provide **feedback on likely errors, edge-cases, or bad practices** (max 3 bullets).
        - Output everything as **inline code comments** appropriate for {language}.
        - Do NOT rewrite or delete user code. Do NOT provide full solutions.
        - Be concise: next step on the first line, then a blank line, then the bullet list.

        Context:
        Exercise name: {exercise_name}
        Exercise description: {exercise_description}
        Reference solution: {reference_solution}
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
    exercise_name = data.get('exercise_name', '')
    exercise_description = data.get('exercise_description', '')
    language = data.get('language', 'python')
    difficulty = data.get('difficulty', 'easy')  # easy, medium, hard
    
    try:
        prompt = f"""
        You are an AI competitor in a coding exercise. Create a solution in {language}.

        Instructions:
        - Your goal is to provide a plausible solution to the exercise.
        - Depending on the difficulty level, introduce mistakes, inefficiencies, or edge-case oversights:
        - easy → more likely to have obvious mistakes
        - medium → subtle mistakes or missing edge cases
        - hard → mostly correct, small inefficiencies or minor mistakes
        - Output the full code as {language} code.
        - Do NOT reference or copy the user's code. Make it self-contained.

        Context:
        Exercise name: {exercise_name}
        Exercise description: {exercise_description}
        Difficulty: {difficulty}
        """
        response = client.models.generate_content(
            model="models/gemini-2.5-pro",
            contents=[prompt]
        )
        ai_response = response.text
        ai_response = re.sub(r'^```[a-zA-Z]*\n', '', ai_response)
        ai_response = re.sub(r'\n```$', '', ai_response)

    except Exception as e:
        ai_response = f"Error calling Google AI: {str(e)}"

    return jsonify({
        "response": ai_response
    })