from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from database.db import init_db
from routes import code_execution, ai_assistant
from routes.exercises import bp as exercises_bp  # use this

load_dotenv()

app = Flask(__name__)
CORS(app)

init_db()

app.register_blueprint(code_execution.bp, url_prefix='/api/code')
app.register_blueprint(ai_assistant.bp, url_prefix='/api/ai')
app.register_blueprint(exercises_bp, url_prefix='/api/exercises')

@app.route('/')
def hello():
    return jsonify({"message": "Coding sandbox backend is running!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
