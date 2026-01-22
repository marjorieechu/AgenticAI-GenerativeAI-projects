# CI/CD Pipeline Skills

## Project Reference
- Repository: [titanic-devops-assessment](https://github.com/marjorieechu/titanic-devops-assessment)
- Reusable Workflows: [shared-gh-workflows](https://github.com/marjorieechu/shared-gh-workflows)

## Skills Demonstrated

### GitHub Actions

| Skill | Why It Matters |
|-------|---------------|
| Reusable workflows | DRY principle - centralized security policies |
| Parallel job execution | Faster feedback - scans run simultaneously |
| Job dependencies with `needs` | Ensures correct execution order |
| GitHub Environments | Separate configs for dev/staging/prod |
| Manual approval gates | Production safety - human review required |

### Shift-Left Security (Sequential Gates)

| Stage | Tool | Fails If | Why Sequential |
|-------|------|----------|----------------|
| 1 | Gitleaks | Secrets found | Stop immediately - no point continuing with leaked creds |
| 2 | Checkov | IaC misconfigs | Don't build insecure infrastructure |
| 3 | SonarCloud | Quality gate failed | Don't build code with bugs/vulnerabilities |
| 4 | Tests | Coverage < 70% | Enforce code coverage standards |
| 5 | Build | - | Only after all checks pass |
| 6 | Trivy | CRITICAL/HIGH CVEs | Scan the actual built image |

**Why Sequential (not parallel)?**
- Each gate must pass before proceeding
- Fail fast - don't waste compute on doomed builds
- Clear accountability - know exactly which check failed

### Docker in CI/CD

| Skill | Why It Matters |
|-------|---------------|
| Multi-stage builds in CI | Consistent builds across environments |
| Docker layer caching (`type=gha`) | 50-80% faster builds |
| GHCR (GitHub Container Registry) | Free, integrated with GitHub Actions |
| Semantic versioning tags | Track deployments, easy rollbacks |

### Deployment Strategies

| Strategy | Implementation | Why |
|----------|---------------|-----|
| Multi-environment | dev → staging → prod | Test changes progressively |
| Auto-deploy dev/staging | On push to branch | Fast iteration |
| Manual approval for prod | GitHub Environments | Human verification |
| Rollback capability | SHA-tagged images | Quick recovery |

### Automated Rollback

```yaml
# Store current revision before deploy
CURRENT_REVISION=$(kubectl rollout history deployment/app | tail -2 | head -1)

# Deploy and health check
kubectl apply -k k8s/overlays/prod
kubectl rollout status deployment/app --timeout=300s

# If health check fails, rollback
kubectl rollout undo deployment/app --to-revision=$CURRENT_REVISION
```

**Why Automated Rollback?**
- Reduces MTTR (Mean Time To Recovery)
- No manual intervention needed at 3am
- Health checks catch issues probes might miss

### SonarCloud Quality Gate

| Condition | Threshold | Why |
|-----------|-----------|-----|
| Coverage | >= 70% | Ensure adequate test coverage |
| Duplicated Lines | <= 3% | Reduce technical debt |
| Maintainability Rating | A | Keep code maintainable |
| Reliability Rating | A | No bugs in production |
| Security Rating | A | No vulnerabilities |

## Key Files
- `.github/workflows/ci-cd.yml` - Main pipeline
- `shared-gh-workflows/.github/workflows/` - Reusable security scans

## Secrets Management

### Repository vs Environment Secrets

| Type | Scope | Use Case |
|------|-------|----------|
| Repository Secrets | All workflows | `SONAR_TOKEN`, `SLACK_WEBHOOK_URL` |
| Environment Secrets | Per environment | `KUBECONFIG` (different per cluster) |

### GitHub Environments Pattern

```yaml
deploy-dev:
  environment:
    name: development    # ← Scopes secrets to this environment
  steps:
    - run: echo "${{ secrets.KUBECONFIG }}" | base64 -d > ~/.kube/config
      # ↑ Uses KUBECONFIG from 'development' environment
```

**Why Environment Secrets?**
- Same secret name (`KUBECONFIG`), different value per environment
- Production can require manual approval before secrets are exposed
- Clear separation between dev/staging/prod credentials

### Setting Up Environment Secrets

```bash
# Base64 encode kubeconfig (required for multi-line secrets)
base64 -w 0 ~/.kube/dev-config > dev.b64

# Set per-environment secret
gh secret set KUBECONFIG --env development --body "$(cat dev.b64)"
gh secret set KUBECONFIG --env staging --body "$(cat staging.b64)"
gh secret set KUBECONFIG --env production --body "$(cat prod.b64)"
```

### Security Best Practices

| Practice | Why |
|----------|-----|
| Never hardcode secrets | Use `${{ secrets.NAME }}` |
| Base64 encode multi-line | GitHub secrets don't preserve newlines well |
| Rotate every 90 days | Limit blast radius of leaked credentials |
| Least privilege | Service accounts with minimal permissions |

## Commands Learned
```bash
# Trigger workflow manually
gh workflow run ci-cd.yml

# View workflow runs
gh run list

# View specific run logs
gh run view <run-id> --log
```
