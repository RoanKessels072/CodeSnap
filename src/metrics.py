from prometheus_client import Counter, Histogram, Gauge, Info

REQUEST_COUNT = Counter(
    "flask_request_count_total",
    "Total number of requests received",
    ["blueprint", "method", "endpoint"]
)

REQUEST_LATENCY = Histogram(
    "flask_request_duration_seconds",
    "Request latency in seconds",
    ["blueprint", "method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

ERROR_COUNT = Counter(
    "flask_request_errors_total",
    "Total number of error responses",
    ["blueprint", "method", "endpoint", "status_code"]
)

CPU_USAGE = Gauge(
    "flask_cpu_usage_percent",
    "CPU usage percentage of the process"
)

MEMORY_USAGE = Gauge(
    "flask_memory_usage_bytes",
    "Memory usage in bytes"
)

ACTIVE_REQUESTS = Gauge(
    "flask_active_requests",
    "Number of requests currently being processed",
    ["blueprint", "method"]
)

APP_INFO = Info(
    "flask_app_info",
    "Application information"
)

APP_INFO.info({
    'version': '0.1.0',
    'app_name': 'codesnap'
})