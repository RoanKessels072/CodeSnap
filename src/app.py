from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
from database.db import init_db
from routes import code_execution, ai_assistant, exercises, attempts, users
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import psutil
import time
from metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    ERROR_COUNT,
    CPU_USAGE,
    MEMORY_USAGE,
    ACTIVE_REQUESTS
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
    request._start_time = time.time()
    
    blueprint = request.blueprint or "root"
    method = request.method
    
    ACTIVE_REQUESTS.labels(blueprint=blueprint, method=method).inc()


@app.after_request
def after_request(response):
    blueprint = request.blueprint or "root"
    method = request.method
    endpoint = request.endpoint or "unknown"
    
    ACTIVE_REQUESTS.labels(blueprint=blueprint, method=method).dec()
    
    REQUEST_COUNT.labels(
        blueprint=blueprint,
        method=method,
        endpoint=endpoint
    ).inc()
    
    if hasattr(request, '_start_time'):
        duration = time.time() - request._start_time
        REQUEST_LATENCY.labels(
            blueprint=blueprint,
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    if response.status_code >= 400:
        ERROR_COUNT.labels(
            blueprint=blueprint,
            method=method,
            endpoint=endpoint,
            status_code=response.status_code
        ).inc()
    
    process = psutil.Process()
    CPU_USAGE.set(process.cpu_percent(interval=None))
    MEMORY_USAGE.set(process.memory_info().rss)
    
    return response


@app.errorhandler(Exception)
def handle_exception(e):
    """Record exceptions in metrics"""
    blueprint = request.blueprint or "root"
    method = request.method
    endpoint = request.endpoint or "unknown"
    
    ERROR_COUNT.labels(
        blueprint=blueprint,
        method=method,
        endpoint=endpoint,
        status_code=500
    ).inc()
    
    raise e

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
