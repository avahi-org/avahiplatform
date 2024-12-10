import time
from functools import wraps
from prometheus_client import Counter, Histogram, Gauge, start_http_server, REGISTRY
import threading
import json
from datetime import datetime
import os

class Observability:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Observability, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.metrics_file = 'metrics.jsonl'
            self.prometheus_started = False
            self.prometheus_port = 8000
            self.registry = REGISTRY

            # Load existing metrics or initialize
            self._metrics_lock = threading.Lock()
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r') as f:
                    try:
                        self.metrics_data = json.load(f)
                    except json.JSONDecodeError:
                        self.metrics_data = {"functions": {}}
            else:
                self.metrics_data = {"functions": {}}

            # Ensure Prometheus metrics are not duplicated
            self.request_counter = self._get_or_create_counter(
                'bedrock_requests_total',
                'Total number of requests to Bedrock',
                ['function_name', 'model_name']
            )
            self.response_time = self._get_or_create_histogram(
                'bedrock_response_time_milliseconds',
                'Response time in milliseconds',
                ['function_name', 'model_name']
            )
            self.input_cost_tracker = self._get_or_create_counter(
                'bedrock_input_cost_dollars',
                'Total input cost in dollars',
                ['function_name', 'model_name']
            )
            self.output_cost_tracker = self._get_or_create_counter(
                'bedrock_output_cost_dollars',
                'Total output cost in dollars',
                ['function_name', 'model_name']
            )
            self.total_cost = self._get_or_create_gauge(
                'bedrock_total_cost_dollars',
                'Total cumulative cost in dollars'
            )

            self.initialized = True

    def _get_or_create_counter(self, name, documentation, labelnames):
        try:
            return Counter(name, documentation, labelnames, registry=self.registry)
        except ValueError:
            # Metric already exists
            return self.registry._names_to_collectors[name]

    def _get_or_create_histogram(self, name, documentation, labelnames):
        try:
            return Histogram(name, documentation, labelnames, registry=self.registry)
        except ValueError:
            # Metric already exists
            return self.registry._names_to_collectors[name]

    def _get_or_create_gauge(self, name, documentation):
        try:
            return Gauge(name, documentation, registry=self.registry)
        except ValueError:
            # Metric already exists
            return self.registry._names_to_collectors[name]

    def initialize(self, metrics_file='metrics.jsonl', start_prometheus=False, prometheus_port=8000):
        self.metrics_file = metrics_file
        self.prometheus_port = prometheus_port
        if start_prometheus and not self.prometheus_started:
            self.start_prometheus_server()

    def start_prometheus_server(self):
        if not self.prometheus_started:
            start_http_server(self.prometheus_port)
            print(f"Prometheus metrics server started on port {self.prometheus_port}")
            self.prometheus_started = True

    def track_request(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            function_name = f"{func.__module__}.{func.__qualname__}"
            model_name = kwargs.get('model_name', 'default_model')

            # Increment Prometheus metrics
            self.request_counter.labels(function_name, model_name).inc()

            result = func(*args, **kwargs)

            response_time_ms = (time.perf_counter() - start_time) * 1000
            self.response_time.labels(function_name, model_name).observe(response_time_ms)

            # Extract costs if present
            input_cost, output_cost, total_cost = 0.0, 0.0, 0.0
            if isinstance(result, tuple) and len(result) >= 4:
                input_cost, output_cost, total_cost = result[1], result[2], result[3]

            self.input_cost_tracker.labels(function_name, model_name).inc(input_cost)
            self.output_cost_tracker.labels(function_name, model_name).inc(output_cost)
            self.total_cost.inc(total_cost)

            # Update metrics.jsonl
            self._update_metrics_file(
                function_name,
                model_name,
                response_time_ms,
                input_cost,
                output_cost,
                total_cost
            )

            return result
        return wrapper

    def _update_metrics_file(self, function_name, model_name, response_time_ms, input_cost, output_cost, total_cost):
        with self._metrics_lock:
            if "functions" not in self.metrics_data:
                self.metrics_data["functions"] = {}

            if function_name not in self.metrics_data["functions"]:
                self.metrics_data["functions"][function_name] = {
                    "model_name": model_name,
                    "total_requests": 0,
                    "total_response_time_ms": 0.0,
                    "avg_response_time_ms": 0.0,
                    "input_cost_dollars": 0.0,
                    "output_cost_dollars": 0.0,
                    "cumulative_total_cost_dollars": 0.0
                }

            func_metrics = self.metrics_data["functions"][function_name]

            # Update metrics
            func_metrics["total_requests"] += 1
            func_metrics["total_response_time_ms"] += response_time_ms
            func_metrics["avg_response_time_ms"] = func_metrics["total_response_time_ms"] / func_metrics["total_requests"]
            func_metrics["input_cost_dollars"] += input_cost
            func_metrics["output_cost_dollars"] += output_cost
            func_metrics["cumulative_total_cost_dollars"] += total_cost

            # Write back to the JSON file
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics_data, f, indent=4)


observability = Observability()


def track_observability(func):
    return observability.track_request(func)