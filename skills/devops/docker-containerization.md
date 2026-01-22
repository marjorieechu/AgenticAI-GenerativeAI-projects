# Docker Containerization Skills

## Project Reference
- Repository: [titanic-devops-assessment](https://github.com/marjorieechu/titanic-devops-assessment)

## Skills Demonstrated

### Docker

| Skill | Why It Matters |
|-------|---------------|
| Writing Dockerfiles for Python/Flask | Ensures consistent environments across dev/staging/prod |
| Multi-stage builds | Reduces image size by 80%+, removes build tools from production |
| Development vs production configs | Dev has hot-reload & debug tools; prod is minimal & secure |

### Multi-Stage Build Benefits

```dockerfile
# Stage 1: Builder - has gcc, build tools
FROM python:3.11-slim AS builder
# Stage 2: Production - only runtime deps
FROM python:3.11-slim AS production
COPY --from=builder /root/.local /home/appuser/.local
```

**Why?**
- **Smaller images**: ~150MB vs ~800MB (faster pulls, less storage)
- **Security**: No compilers = smaller attack surface
- **Compliance**: Fewer packages = fewer CVEs to patch

### Security Best Practices

| Practice | Implementation | Reason |
|----------|---------------|--------|
| Non-root user | `USER appuser` (UID 1000) | Container escape won't have root privileges |
| Slim base image | `python:3.11-slim` | ~50 packages vs ~400 in full image |
| No pip cache | `--no-cache-dir` | Saves ~50MB, no stale cache issues |
| Apt cleanup | `rm -rf /var/lib/apt/lists/*` | Removes package index (~30MB) |

### Docker Compose

| Skill | Why It Matters |
|-------|---------------|
| Multi-container orchestration | Single command starts entire stack |
| Environment variables with defaults | `${VAR:-default}` allows override without code changes |
| Health checks | Kubernetes/orchestrators know when app is truly ready |
| Service dependencies | `condition: service_healthy` prevents race conditions |
| Volume management | Data persists across container restarts |

### Health Checks - Why They're Critical

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/"]
  interval: 30s
  timeout: 10s
  retries: 3
```

**Benefits:**
- Load balancers only route to healthy instances
- Orchestrators auto-restart failed containers
- Rolling deployments wait for new pods to be healthy

### Troubleshooting

| Issue | Solution | Learning |
|-------|----------|----------|
| Flask/Werkzeug version conflicts | Pin versions in requirements.txt | Always lock dependencies |
| Python import path errors | Set `WORKDIR` and `PYTHONPATH` correctly | Container paths differ from local |
| Container startup failures | `docker logs -f <container>` | Always check logs first |

## Key Files
- `docker/Dockerfile` - Production Dockerfile
- `docker/Dockerfile.dev` - Development Dockerfile with hot-reload
- `docker-compose.yml` - Base compose configuration
- `docker-compose.dev.yml` - Development compose with volume mounts
- `docker-compose.prod.yml` - Production compose configuration

## Commands Learned
```bash
# Build and run containers
docker-compose -f docker-compose.dev.yml up --build

# Run in detached mode
docker-compose -f docker-compose.dev.yml up -d

# View container logs
docker logs -f <container-name>

# Stop containers
docker-compose -f docker-compose.dev.yml down
```
