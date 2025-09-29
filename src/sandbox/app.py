from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)