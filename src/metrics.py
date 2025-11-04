from prometheus_client import Counter, Summary, Gauge

REQUEST_COUNT = Counter(
    "flask_request_count_total",
    "Total number of requests received",
    ["blueprint", "method"]
)

REQUEST_LATENCY = Summary(
    "flask_request_latency_seconds",
    "Request latency in seconds",
    ["blueprint", "method"]
)

ERROR_COUNT = Counter(
    "flask_request_errors_total",
    "Total number of error responses",
    ["blueprint", "method", "status_code"]
)

CPU_USAGE = Gauge(
    "flask_cpu_usage_percent",
    "CPU usage percentage of the process"
)
