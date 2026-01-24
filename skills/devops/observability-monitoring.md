# Observability & Monitoring Skills

## Project Reference
- Repository: [titanic-devops-assessment](https://github.com/marjorieechu/titanic-devops-assessment)

## Skills Demonstrated

### Monitoring Stack

| Component | Purpose |
|-----------|---------|
| Prometheus | Metrics collection (pull-based) |
| Grafana | Dashboards & visualization |
| AlertManager | Alert routing & notifications |

### ServiceMonitor (Prometheus Operator)

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: my-app
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

**Why ServiceMonitor?**
- Auto-discovers pods via labels
- No need to edit Prometheus config
- Works with Prometheus Operator

### Key Metrics (RED Method)

| Type | Metric | What it tells you |
|------|--------|-------------------|
| **R**ate | `http_requests_total` | Traffic volume |
| **E**rrors | `status=~"5.."` | Failure rate |
| **D**uration | `http_request_duration_seconds` | Latency |

### Grafana Dashboard Panels

| Panel | PromQL |
|-------|--------|
| Request Rate | `sum(rate(http_requests_total[5m])) by (status)` |
| p95 Latency | `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))` |
| Error Rate | `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))` |
| CPU Usage | `sum(rate(container_cpu_usage_seconds_total{container="app"}[5m])) by (pod)` |
| Memory | `sum(container_memory_usage_bytes{container="app"}) by (pod)` |

### Alert Rules

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
spec:
  groups:
    - name: app.availability
      rules:
        - alert: AppDown
          expr: up{job="my-app"} == 0
          for: 1m
          labels:
            severity: critical
```

**Alert Design:**
| Field | Purpose |
|-------|---------|
| `expr` | PromQL condition |
| `for` | Wait duration before firing |
| `severity` | critical/warning/info |
| `annotations` | Human-readable description |

### Severity Guidelines

| Severity | Response | Example |
|----------|----------|---------|
| Critical | Page on-call | App down, >5% errors |
| Warning | Next business day | High CPU, latency |
| Info | Review weekly | Minor anomalies |

## Key Learnings

1. **Pull vs Push** - Prometheus pulls metrics; apps expose `/metrics`
2. **Labels are powerful** - Filter/aggregate with `{label="value"}`
3. **histogram_quantile** - Calculate percentiles from histogram buckets
4. **rate() over increase()** - rate() is per-second, increase() is total
5. **Dashboard as ConfigMap** - Auto-provision Grafana dashboards via K8s
