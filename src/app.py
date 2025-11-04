from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
from database.db import init_db
from routes import code_execution, ai_assistant, exercises, attempts, users
from prometheus_client import Summary, Counter, Gauge, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import psutil
from metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    ERROR_COUNT,
    CPU_USAGE
)


load_dotenv()

app = Flask(__name__)
CORS(app)

init_db()

app.register_blueprint(code_execution.bp, url_prefix='/api/code')
app.register_blueprint(ai_assistant.bp, url_prefix='/api/ai')
app.register_blueprint(exercises.bp, url_prefix='/api/exercises')
app.register_blueprint(attempts.bp, url_prefix='/api/attempts')
app.register_blueprint(users.bp, url_prefix='/api/users')

@app.before_request
def before_request():
    request.start_time = psutil.Process().cpu_times().user


@app.after_request
def after_request(response):
    blueprint = request.blueprint or "root"
    method = request.method

    REQUEST_COUNT.labels(blueprint=blueprint, method=method).inc()

    with REQUEST_LATENCY.labels(blueprint=blueprint, method=method).time():
        pass

    if response.status_code >= 400:
        ERROR_COUNT.labels(
            blueprint=blueprint,
            method=method,
            status_code=response.status_code
        ).inc()

    CPU_USAGE.set(psutil.cpu_percent(interval=None))

    return response

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
