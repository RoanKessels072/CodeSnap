import re
from google import genai
import os

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def get_ai_assistant_feedback(code, language, exercise_name, description, reference_solution):
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
        Exercise description: {description}
        Reference solution: {reference_solution}
        User code:
        {code}
        """

    response = client.models.generate_content(
        model="models/gemini-2.5-pro",
        contents=[prompt]
    )
    text = response.text.strip()
    text = re.sub(r'^```[a-zA-Z]*\n', '', text)
    text = re.sub(r'\n```$', '', text)
    return text

def generate_ai_rival(language, exercise_name, description, difficulty):
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
        Exercise description: {description}
        Difficulty: {difficulty}
        """
    response = client.models.generate_content(
        model="models/gemini-2.5-pro",
        contents=[prompt]
    )
    text = response.text.strip()
    text = re.sub(r'^```[a-zA-Z]*\n', '', text)
    text = re.sub(r'\n```$', '', text)
    return text
