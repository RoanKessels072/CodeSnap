from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)
CORS(app)

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

@app.route('/')
def hello():
    return jsonify({"message": "Coding sandbox backend is running!"})

@app.route('/api/execute', methods=['POST'])
def execute_code():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    return jsonify({
        "output": f"Received {language} code: {code[:50]}...",
        "error": None
    })

@app.route('/api/ai-assistant', methods=['POST'])
def ai_assistant():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')

    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-pro",
            contents=[f"Analyze and provide feedback for this {language} code: {code}"]
        )
        ai_response = response.text
    except Exception as e:
        ai_response = f"Error calling Google AI: {str(e)}"

    return jsonify({
        "response": ai_response
    })

@app.route('/api/ai-rival', methods=['POST'])
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
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)