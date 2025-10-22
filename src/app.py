from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from database.db import init_db

# Import blueprints
from routes import code_execution, ai_assistant

load_dotenv()

app = Flask(__name__)
CORS(app)

init_db()

app.register_blueprint(code_execution.bp, url_prefix='/api')
app.register_blueprint(ai_assistant.bp, url_prefix='/api')

@app.route('/')
def hello():
    return jsonify({"message": "Coding sandbox backend is running!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)