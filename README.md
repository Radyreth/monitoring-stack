# Cloud Monitoring Stack

![Validate Stack](https://github.com/Radyreth/monitoring-stack/actions/workflows/validate.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white)

> Stack de monitoring complete avec Prometheus, Grafana et Node Exporter.
> Dashboard pre-configure, metriques custom Flask, tout demarre en une commande.

---

## How to run

```bash
# 1. Cloner le repo
git clone https://github.com/Radyreth/monitoring-stack.git
cd monitoring-stack

# 2. Lancer la stack
docker compose up -d

# 3. Ouvrir Grafana
# → http://localhost:3000 (pas de login requis)
```

C'est tout. Le dashboard est deja configure.

---

## Architecture

```
+-------------------+
|    Grafana :3000  |  ← Dashboard pre-configure (provisioning auto)
+--------+----------+
         |
         | PromQL queries
         v
+-------------------+
|  Prometheus :9090 |  ← Collecte les metriques toutes les 15s
+--------+----------+
         |
         | scrape /metrics
         |
    +----+----+--------------------+
    |         |                    |
    v         v                    v
+--------+ +--------+      +-------------+
| Flask  | | Node   |      | Prometheus  |
|  App   | | Export  |      |  (self)     |
| :5000  | | :9100  |      |             |
+--------+ +--------+      +-------------+
 Custom     CPU, RAM,        Internal
 metrics    Disk, Net        metrics
```

## What is monitored

### Application metrics (Flask)
| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total requests by method, endpoint, status |
| `http_request_duration_seconds` | Histogram | Request latency distribution |
| `http_errors_total` | Counter | Application errors by type |

### System metrics (Node Exporter)
| Metric | Description |
|--------|-------------|
| CPU Usage | Percentage of CPU time not idle |
| Memory Usage | RAM utilization percentage |
| Disk Usage | Filesystem space used |

## Dashboard

The Grafana dashboard includes 8 panels organized in 3 rows:

**Row 1 — Traffic**
- Request rate (req/s) by endpoint
- Error rate percentage (with color thresholds)
- Number of targets UP

**Row 2 — Performance**
- P95 latency by endpoint
- Application errors over time

**Row 3 — Infrastructure**
- CPU usage timeline
- Memory usage gauge
- Disk usage gauge

### Screenshots

> Add screenshots after running the stack:
> 1. Open http://localhost:3000
> 2. Generate traffic: `for i in $(seq 1 100); do curl -s localhost:5000/api/data > /dev/null; done`
> 3. Take screenshots and place them in `screenshots/`

![Dashboard Overview](screenshots/dashboard-overview.png)
![System Metrics](screenshots/system-metrics.png)

## Generate test traffic

```bash
# Fast requests
for i in $(seq 1 200); do curl -s localhost:5000/api/data > /dev/null; done

# Slow requests (latency spikes)
for i in $(seq 1 20); do curl -s localhost:5000/api/slow > /dev/null; done

# Error requests (50% failure rate)
for i in $(seq 1 50); do curl -s localhost:5000/api/error > /dev/null; done
```

After generating traffic, the dashboard updates within 15 seconds.

## Endpoints

| URL | Description |
|-----|-------------|
| http://localhost:3000 | Grafana dashboard |
| http://localhost:9090 | Prometheus UI |
| http://localhost:5000 | Flask API |
| http://localhost:5000/metrics | Prometheus metrics (raw) |
| http://localhost:9100/metrics | Node Exporter metrics |

## How it works

### Prometheus scraping
Prometheus pulls metrics from each target every 15 seconds. Targets are defined in `prometheus.yml`. Each target exposes a `/metrics` endpoint in Prometheus text format.

### Custom metrics
The Flask app uses `prometheus_client` to expose 3 custom metrics. A middleware (`before_request` / `after_request`) automatically tracks every HTTP request.

### Grafana provisioning
Grafana supports file-based provisioning: datasources and dashboards are loaded from YAML/JSON files at startup. No manual configuration needed.

### PromQL queries
The dashboard uses PromQL (Prometheus Query Language) to query metrics:
- `rate()` for calculating per-second rates from counters
- `histogram_quantile()` for latency percentiles
- `node_*` metrics for system monitoring

## Tech stack

| Tool | Role | Port |
|------|------|------|
| Prometheus | Metrics collection & storage | 9090 |
| Grafana | Visualization & dashboards | 3000 |
| Node Exporter | System metrics (CPU/RAM/disk) | 9100 |
| Flask | Demo app with custom metrics | 5000 |
| Docker Compose | Orchestration | - |

## License

MIT
