import time
from functools import wraps
from prometheus_client import Counter, Histogram, Gauge, start_http_server, REGISTRY
import threading
import json
from datetime import datetime


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

            # Use the global registry
            self.registry = REGISTRY

            # Create metrics
            self.request_counter = Counter('bedrock_requests_total', 'Total number of requests to Bedrock',
                                           ['function_name', 'model_name'], registry=self.registry)
            self.response_time = Histogram('bedrock_response_time_milliseconds', 'Response time in milliseconds',
                                           ['function_name', 'model_name'], registry=self.registry)
            self.input_cost_tracker = Counter('bedrock_input_cost_dollars', 'Total input cost in dollars',
                                              ['function_name', 'model_name'], registry=self.registry)
            self.output_cost_tracker = Counter('bedrock_output_cost_dollars', 'Total output cost in dollars',
                                               ['function_name', 'model_name'], registry=self.registry)
            self.total_cost = Gauge('bedrock_total_cost_dollars', 'Total cumulative cost in dollars',
                                    registry=self.registry)

            self.initialized = True

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

            self.request_counter.labels(function_name, model_name).inc()

            result = func(*args, **kwargs)

            response_time_ms = (time.perf_counter() - start_time) * 1000
            self.response_time.labels(function_name, model_name).observe(response_time_ms)

            input_cost, output_cost, total_cost = 0.0, 0.0, 0.0
            if isinstance(result, tuple) and len(result) >= 4:
                input_cost, output_cost, total_cost = result[1], result[2], result[3]

            self.input_cost_tracker.labels(function_name, model_name).inc(input_cost)
            self.output_cost_tracker.labels(function_name, model_name).inc(output_cost)
            self.total_cost.inc(total_cost)

            self._log_metrics_to_file(function_name, model_name, response_time_ms, input_cost, output_cost, total_cost)

            return result

        return wrapper

    def _log_metrics_to_file(self, function_name, model_name, response_time_ms, input_cost, output_cost, total_cost):
        metric_entry = {
            'timestamp': datetime.now().isoformat(),
            'function_name': function_name,
            'model_name': model_name,
            'total_requests': self.request_counter.labels(function_name, model_name)._value.get(),
            'response_time_ms': response_time_ms,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost,
            'cumulative_total_cost': self.total_cost._value.get()
        }

        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metric_entry) + '\n')


observability = Observability()


def track_observability(func):
    return observability.track_request(func)