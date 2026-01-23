# Kubernetes Deployment Skills

## Project Reference
- Repository: [titanic-devops-assessment](https://github.com/marjorieechu/titanic-devops-assessment)

## Skills Demonstrated

### Kustomize vs Helm

| Tool | Use Case | Pros |
|------|----------|------|
| **Kustomize** | Environment patches | No templating, GitOps-friendly, built into kubectl |
| **Helm** | Package & share | Templating, dependencies, chart repos |

### Kustomize Pattern

```
k8s/
├── base/              # Common manifests
│   └── kustomization.yaml
└── overlays/
    ├── dev/           # namePrefix: dev-
    ├── staging/       # namePrefix: staging-
    └── prod/          # namePrefix: prod-
```

**Key Features:**
- `namePrefix` - Adds prefix to all resources
- `patches` - Override specific fields
- `secretGenerator` - Generate secrets per environment
- `configMapGenerator` - Generate configmaps

### Production-Ready Deployment

| Feature | Why |
|---------|-----|
| Resource requests/limits | Prevent resource starvation |
| Liveness probe | Restart unhealthy pods |
| Readiness probe | Don't route traffic until ready |
| HPA | Auto-scale on CPU/memory |
| PDB | Maintain availability during disruptions |
| Network Policy | Restrict pod communication |
| Anti-affinity | Spread pods across nodes |

### Security Context

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

**Why Each Setting:**
- `runAsNonRoot` - Container escape won't have root
- `readOnlyRootFilesystem` - Prevent file tampering
- `capabilities.drop: ALL` - Minimal Linux capabilities

### Rolling Update Strategy

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # Add 1 new pod first
    maxUnavailable: 0  # Never kill existing pods
```

**Result:** Zero-downtime deployments

### Horizontal Pod Autoscaler

```yaml
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          averageUtilization: 70
```

**Behavior tuning:**
- `scaleDown.stabilizationWindowSeconds: 300` - Wait 5 min before scaling down
- `scaleUp.stabilizationWindowSeconds: 0` - Scale up immediately

### Network Policy

```yaml
spec:
  podSelector:
    matchLabels:
      app: titanic-api
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
  egress:
    - to:
        - ipBlock:
            cidr: 10.0.0.0/8  # RDS in VPC
      ports:
        - port: 5432
```

**What it does:**
- Only allow ingress from ingress controller
- Only allow egress to database (port 5432)

## Commands Learned

```bash
# Kustomize
kubectl kustomize k8s/overlays/dev        # Preview
kubectl apply -k k8s/overlays/dev         # Apply
kubectl delete -k k8s/overlays/dev        # Delete

# Helm
helm install titanic-api ./helm/titanic-api
helm upgrade titanic-api ./helm/titanic-api
helm rollback titanic-api 1               # Rollback to revision 1
helm uninstall titanic-api
```
