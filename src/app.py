from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from src.database.db import init_db
from src.routes import code_execution, ai_assistant, exercises, attempts, users
from prometheus_client import Summary, Counter, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware


load_dotenv()

REQUEST_COUNT = Counter("request_count", "Total request count")
REQUEST_LATENCY = Summary("request_latency_seconds", "Request latency")

app = Flask(__name__)
CORS(app)

init_db()

app.register_blueprint(code_execution.bp, url_prefix='/api/code')
app.register_blueprint(ai_assistant.bp, url_prefix='/api/ai')
app.register_blueprint(exercises.bp, url_prefix='/api/exercises')
app.register_blueprint(attempts.bp, url_prefix='/api/attempts')
app.register_blueprint(users.bp, url_prefix='/api/users')

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
