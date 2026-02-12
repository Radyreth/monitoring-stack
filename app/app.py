"""
Application Flask instrumentee avec des metriques Prometheus.

Expose 3 metriques custom :
- http_requests_total     : compteur de requetes par endpoint et status
- http_request_duration   : histogramme de latence par endpoint
- http_errors_total       : compteur d'erreurs applicatives

Les metriques sont exposees sur /metrics au format Prometheus.
"""

import time
import random
from flask import Flask, jsonify, request, Response
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)

app = Flask(__name__)


# =============================================================================
# Definition des metriques Prometheus
# =============================================================================

# Compteur : nombre total de requetes HTTP
# Labels : method (GET/POST), endpoint (/api/data), status (200/500)
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

# Histogramme : distribution de la duree des requetes
# Les buckets definissent les seuils de latence a mesurer
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

# Compteur : nombre total d'erreurs applicatives
ERROR_COUNT = Counter(
    "http_errors_total",
    "Total number of HTTP errors",
    ["method", "endpoint", "error_type"]
)


# =============================================================================
# Middleware : mesure automatique de chaque requete
# =============================================================================

@app.before_request
def start_timer():
    """Demarre un timer avant chaque requete."""
    request._start_time = time.time()


@app.after_request
def track_metrics(response):
    """Enregistre les metriques apres chaque requete."""
    # Ne pas tracker les metriques Prometheus elles-memes
    if request.path == "/metrics":
        return response

    duration = time.time() - request._start_time
    endpoint = request.path

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()

    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=endpoint
    ).observe(duration)

    return response


# =============================================================================
# Routes de l'application
# =============================================================================

@app.route("/")
def home():
    """Page d'accueil."""
    return jsonify({
        "service": "monitoring-demo",
        "status": "running",
        "endpoints": ["/", "/api/data", "/api/slow", "/api/error", "/health", "/metrics"]
    })


@app.route("/health")
def health():
    """Health check pour Prometheus et les orchestrateurs."""
    return jsonify({"status": "healthy"}), 200


@app.route("/api/data")
def get_data():
    """Endpoint rapide qui retourne des donnees."""
    # Simule un temps de traitement variable (5-50ms)
    time.sleep(random.uniform(0.005, 0.05))
    return jsonify({
        "items": [
            {"id": 1, "name": "Server A", "cpu": random.randint(10, 90)},
            {"id": 2, "name": "Server B", "cpu": random.randint(10, 90)},
            {"id": 3, "name": "Server C", "cpu": random.randint(10, 90)},
        ]
    })


@app.route("/api/slow")
def slow_endpoint():
    """Endpoint lent pour tester les alertes de latence."""
    # Simule un traitement long (200ms - 2s)
    delay = random.uniform(0.2, 2.0)
    time.sleep(delay)
    return jsonify({"message": "slow response", "delay_seconds": round(delay, 3)})


@app.route("/api/error")
def error_endpoint():
    """Endpoint qui genere des erreurs aleatoires pour tester le monitoring."""
    if random.random() < 0.5:
        ERROR_COUNT.labels(
            method="GET",
            endpoint="/api/error",
            error_type="random_failure"
        ).inc()
        return jsonify({"error": "Random failure occurred"}), 500

    return jsonify({"message": "success"})


@app.route("/metrics")
def metrics():
    """Expose les metriques au format Prometheus."""
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
