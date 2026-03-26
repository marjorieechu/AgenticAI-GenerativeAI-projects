# Helm Wrapper (Umbrella) Chart - DevOps Skill Guide

## Table of Contents
1. [What is a Helm Wrapper Chart?](#what-is-a-helm-wrapper-chart)
2. [Why Use Wrapper Charts?](#why-use-wrapper-charts)
3. [Key Concepts](#key-concepts)
4. [Wrapper Chart Architecture](#wrapper-chart-architecture)
5. [When to Use Wrapper Charts](#when-to-use-wrapper-charts)
6. [Building a Wrapper Chart Step-by-Step](#building-a-wrapper-chart-step-by-step)
7. [Best Practices](#best-practices)
8. [Common Patterns](#common-patterns)
9. [Skills Learned from This Ticket](#skills-learned-from-this-ticket)
10. [Troubleshooting](#troubleshooting)

---

## What is a Helm Wrapper Chart?

A **Helm Wrapper Chart** (also called an **Umbrella Chart**) is a parent Helm chart that bundles multiple sub-charts (child charts) together into a single deployable unit. Instead of deploying each component of your application separately, you deploy one chart that orchestrates all components.

### Simple Analogy
Think of it like a shipping container:
- **Without wrapper chart**: You ship individual boxes (frontend, backend, database) separately
- **With wrapper chart**: You pack all boxes into one container and ship together

### Basic Structure
```
my-wrapper-chart/
├── Chart.yaml          # Defines the wrapper and its dependencies
├── values.yaml         # Configuration for all sub-charts
├── charts/             # Contains all sub-charts
│   ├── frontend/
│   ├── backend/
│   └── database/
└── templates/          # Shared resources (optional)
```

---

## Why Use Wrapper Charts?

### 1. Single Deployment Command
```bash
# Without wrapper (multiple commands)
helm install frontend ./frontend-chart
helm install backend ./backend-chart
helm install redis ./redis-chart

# With wrapper (one command)
helm install myapp ./wrapper-chart
```

### 2. Consistent Versioning
All components are versioned together. When you release v2.0.0 of your application, all sub-charts deploy together.

### 3. Simplified Configuration
One `values.yaml` file controls all components:
```yaml
frontend:
  replicaCount: 3
backend:
  replicaCount: 5
  database:
    host: mydb.example.com
```

### 4. Environment Management
Easily switch between environments:
```bash
helm install myapp . -f values.yaml -f values-prod.yaml
```

### 5. GitOps Friendly
ArgoCD/FluxCD can manage one Application resource instead of many.

### 6. Dependency Management
Helm automatically handles the order of deployment based on dependencies.

---

## Key Concepts

### Chart.yaml Dependencies
The wrapper chart declares its sub-charts as dependencies:

```yaml
# Chart.yaml
apiVersion: v2
name: my-wrapper
version: 1.0.0
dependencies:
  - name: backend
    version: 1.0.0
    repository: "file://charts/backend"    # Local sub-chart
    condition: backend.enabled             # Can be disabled
  - name: redis
    version: 17.0.0
    repository: "https://charts.bitnami.com/bitnami"  # External chart
    condition: redis.enabled
```

### Condition Flag
The `condition` field allows you to enable/disable sub-charts:
```yaml
# values.yaml
backend:
  enabled: true    # Deploy backend
redis:
  enabled: false   # Skip redis deployment
```

### Value Inheritance
Values flow from parent to child charts:
```yaml
# Parent values.yaml
global:
  environment: production    # Available to ALL sub-charts

backend:                     # Passed to backend sub-chart
  replicaCount: 3
  image:
    tag: v2.0.0
```

### Global Values
Use `global` for values shared across all sub-charts:
```yaml
global:
  imagePullSecrets:
    - name: registry-secret
  environment: prod
  domain: example.com
```

---

## Wrapper Chart Architecture

### Typical Structure for a Web Application

```
connect-wrapper/
├── Chart.yaml                    # Main chart definition
├── values.yaml                   # Base/default values
├── values-dev.yaml               # Development overrides
├── values-stage.yaml             # Staging overrides
├── values-prod.yaml              # Production overrides
├── .helmignore                   # Files to ignore when packaging
├── templates/
│   ├── _helpers.tpl              # Shared template helpers
│   ├── NOTES.txt                 # Post-install notes
│   └── namespace.yaml            # Optional shared resources
└── charts/
    ├── connect-backend/
    │   ├── Chart.yaml
    │   ├── values.yaml
    │   └── templates/
    │       ├── _helpers.tpl
    │       ├── deployment.yaml
    │       ├── service.yaml
    │       ├── ingress.yaml
    │       ├── configmap.yaml
    │       ├── secret.yaml
    │       ├── hpa.yaml
    │       └── serviceaccount.yaml
    └── connect-frontend/
        ├── Chart.yaml
        ├── values.yaml
        └── templates/
            ├── _helpers.tpl
            ├── deployment.yaml
            ├── service.yaml
            ├── ingress.yaml
            ├── configmap.yaml
            └── secret.yaml
```

### How Values Flow

```
                    ┌─────────────────────┐
                    │   values.yaml       │
                    │   (base config)     │
                    └─────────┬───────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  values-{env}.yaml  │
                    │  (env overrides)    │
                    └─────────┬───────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    ┌───────────┐      ┌───────────┐      ┌───────────┐
    │  global   │      │  backend  │      │  frontend │
    │  values   │      │  values   │      │  values   │
    └─────┬─────┘      └─────┬─────┘      └─────┬─────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │  Rendered K8s       │
                    │  Manifests          │
                    └─────────────────────┘
```

---

## When to Use Wrapper Charts

### Good Use Cases

| Scenario | Why Wrapper Chart Helps |
|----------|------------------------|
| Microservices application | Deploy all services together with consistent config |
| Multi-tier app (frontend + backend + cache) | Single deployment, shared ingress rules |
| Multiple environments (dev/stage/prod) | Environment-specific values files |
| GitOps workflows | One ArgoCD Application instead of many |
| Team onboarding | New developers run one command to deploy |
| Release management | Version all components together |

### When NOT to Use

| Scenario | Better Alternative |
|----------|-------------------|
| Single service application | Regular Helm chart |
| Services with very different lifecycles | Separate charts |
| Third-party charts only | Use Helmfile instead |
| Extremely large deployments (50+ services) | Consider Helmfile or Kustomize |

---

## Building a Wrapper Chart Step-by-Step

### Step 1: Create Directory Structure
```bash
mkdir -p my-wrapper/charts
mkdir -p my-wrapper/templates
```

### Step 2: Create Main Chart.yaml
```yaml
# my-wrapper/Chart.yaml
apiVersion: v2
name: my-wrapper
description: Umbrella chart for My Application
type: application
version: 1.0.0
appVersion: "1.0.0"

dependencies:
  - name: backend
    version: 1.0.0
    repository: "file://charts/backend"
    condition: backend.enabled
  - name: frontend
    version: 1.0.0
    repository: "file://charts/frontend"
    condition: frontend.enabled
```

### Step 3: Create Sub-Chart (Example: Backend)
```yaml
# my-wrapper/charts/backend/Chart.yaml
apiVersion: v2
name: backend
description: Backend API service
type: application
version: 1.0.0
appVersion: "1.0.0"
```

### Step 4: Create Sub-Chart Templates
```yaml
# my-wrapper/charts/backend/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "backend.fullname" . }}
  labels:
    {{- include "backend.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "backend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "backend.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: {{ .Values.service.port }}
```

### Step 5: Create Base Values
```yaml
# my-wrapper/values.yaml
global:
  environment: dev
  imagePullSecrets:
    - name: registry-secret

backend:
  enabled: true
  replicaCount: 2
  image:
    repository: myrepo/backend
    tag: latest
  service:
    port: 8080

frontend:
  enabled: true
  replicaCount: 2
  image:
    repository: myrepo/frontend
    tag: latest
```

### Step 6: Create Environment Overrides
```yaml
# my-wrapper/values-prod.yaml
global:
  environment: prod

backend:
  replicaCount: 5
  image:
    tag: v2.0.0
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi

frontend:
  replicaCount: 3
  image:
    tag: v2.0.0
```

### Step 7: Update Dependencies
```bash
cd my-wrapper
helm dependency update
```

### Step 8: Validate
```bash
helm lint .
helm lint . -f values-prod.yaml
helm template myapp . -f values-prod.yaml
```

### Step 9: Deploy
```bash
# Development
helm install myapp . -f values.yaml -n dev --create-namespace

# Production
helm install myapp . -f values.yaml -f values-prod.yaml -n prod --create-namespace
```

---

## Best Practices

### 1. Use Meaningful Names
```yaml
# Good
connect-backend:
  enabled: true

# Bad
chart1:
  enabled: true
```

### 2. Always Use Conditions
```yaml
dependencies:
  - name: redis
    condition: redis.enabled  # Always add this!
```

### 3. Leverage Global Values
```yaml
global:
  # Shared across ALL sub-charts
  domain: example.com
  environment: prod
  imagePullSecrets:
    - name: ecr-secret
```

### 4. Template Helpers for Consistency
```yaml
# _helpers.tpl
{{- define "myapp.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
```

### 5. Use Checksum Annotations for Config Reloads
```yaml
# deployment.yaml
metadata:
  annotations:
    checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
```

### 6. Separate Secrets from ConfigMaps
- ConfigMaps: Non-sensitive configuration
- Secrets: Passwords, API keys, certificates

### 7. External Secrets for Production
```yaml
externalSecrets:
  enabled: true
  secretStoreName: vault-backend
  refreshInterval: 1h
```

### 8. Health Checks
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 10
```

---

## Common Patterns

### Pattern 1: Conditional External Dependencies
```yaml
# Chart.yaml
dependencies:
  - name: redis
    version: 17.x.x
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
    
# values.yaml
redis:
  enabled: true  # Set to false if using external Redis
  
# values-prod.yaml  
redis:
  enabled: false  # Use AWS ElastiCache instead
```

### Pattern 2: Environment-Specific Ingress
```yaml
# values-dev.yaml
backend:
  ingress:
    hosts:
      - host: api.dev.example.com
        
# values-prod.yaml
backend:
  ingress:
    hosts:
      - host: api.example.com
    annotations:
      nginx.ingress.kubernetes.io/rate-limit: "100"
```

### Pattern 3: Scaling Per Environment
```yaml
# values-dev.yaml
backend:
  replicaCount: 1
  autoscaling:
    enabled: false

# values-prod.yaml
backend:
  replicaCount: 3
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilization: 70
```

### Pattern 4: ArgoCD Integration
```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-prod
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/org/charts.git
    path: my-wrapper
    helm:
      valueFiles:
        - values.yaml
        - values-prod.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

---

## Skills Learned from This Ticket

### Technical Skills

1. **Helm Chart Development**
   - Creating Chart.yaml with proper metadata
   - Defining dependencies with conditions
   - Writing Go templates for Kubernetes manifests
   - Using template helpers (_helpers.tpl)

2. **Kubernetes Resource Management**
   - Deployments with proper labels and selectors
   - Services (ClusterIP, NodePort, LoadBalancer)
   - Ingress with TLS configuration
   - ConfigMaps and Secrets separation
   - HorizontalPodAutoscaler (HPA)
   - PodDisruptionBudget (PDB)
   - ServiceAccounts

3. **Environment Configuration**
   - Base values with sensible defaults
   - Environment-specific overrides
   - Global values for cross-chart sharing

4. **Security Best Practices**
   - External Secrets Operator integration
   - Vault secret management
   - Image pull secrets for private registries

5. **GitOps Workflows**
   - ArgoCD Application manifests
   - Automated sync policies
   - Multi-environment deployment strategies

### DevOps Concepts

1. **Infrastructure as Code (IaC)**
   - Declarative configuration
   - Version-controlled deployments
   - Reproducible environments

2. **12-Factor App Principles**
   - Config stored in environment
   - Dev/prod parity
   - Disposable containers

3. **Release Management**
   - Semantic versioning
   - Rolling updates
   - Rollback capabilities

---

## Troubleshooting

### Common Issues

#### 1. Dependencies Not Found
```bash
Error: found in Chart.yaml, but missing in charts/ directory
```
**Solution**: Run `helm dependency update`

#### 2. Values Not Applied to Sub-Chart
```yaml
# Wrong - values at root level
replicaCount: 3

# Correct - values under sub-chart name
backend:
  replicaCount: 3
```

#### 3. Template Rendering Errors
```bash
# Debug with template command
helm template myapp . --debug

# Check specific template
helm template myapp . -s charts/backend/templates/deployment.yaml
```

#### 4. Ingress Not Working
- Check ingress class exists: `kubectl get ingressclass`
- Verify TLS secret: `kubectl get secret -n <namespace>`
- Check ingress controller logs

#### 5. Pods Stuck in Pending
```bash
kubectl describe pod <pod-name>
# Check for:
# - Resource constraints
# - Node selectors
# - Image pull issues
```

### Useful Commands

```bash
# Lint chart
helm lint .
helm lint . -f values-prod.yaml

# Dry run
helm install myapp . --dry-run --debug

# Template only
helm template myapp . > rendered.yaml

# Diff changes (requires helm-diff plugin)
helm diff upgrade myapp . -f values-prod.yaml

# Debug release
helm get manifest myapp
helm get values myapp
helm history myapp

# Rollback
helm rollback myapp 1
```

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Create chart | `helm create mychart` |
| Update deps | `helm dependency update` |
| Lint | `helm lint .` |
| Template | `helm template myapp .` |
| Dry run | `helm install myapp . --dry-run` |
| Install | `helm install myapp . -n namespace` |
| Upgrade | `helm upgrade myapp . -n namespace` |
| Rollback | `helm rollback myapp 1` |
| Uninstall | `helm uninstall myapp -n namespace` |
| List releases | `helm list -A` |
| Get values | `helm get values myapp` |
| Get manifest | `helm get manifest myapp` |

---

## Further Reading

- [Helm Documentation](https://helm.sh/docs/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [ArgoCD with Helm](https://argo-cd.readthedocs.io/en/stable/user-guide/helm/)
- [External Secrets Operator](https://external-secrets.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

---

*This skill document was generated from the Connect Helm Wrapper Chart ticket implementation.*

ok lets go back to the helm project for now.i noticed the wrapper chart.yml and wrapper values.yml are combinations of the individual
    microservice charts but the wrapper template doesnt hold the combination, explain why is this

⛬  Great observation! Let me explain why the wrapper chart's templates/ folder doesn't contain the combined templates from the
   sub-charts.

   How Helm Umbrella Charts Work

   The wrapper chart's `templates/` folder is intentionally minimal because Helm handles sub-chart templates automatically through the
   dependency system.

   The Architecture

     helm-wrapper/
     ├── Chart.yaml          # Declares dependencies on sub-charts
     ├── values.yaml         # Passes values DOWN to sub-charts
     ├── templates/          # Only for SHARED/GLOBAL resources
     │   ├── _helpers.tpl    # Shared helper functions
     │   ├── NOTES.txt       # Post-install message
     │   └── namespace.yaml  # Optional shared resources
     └── charts/
         ├── connect-backend/
         │   └── templates/   # Backend templates rendered automatically
         └── connect-frontend/
             └── templates/   # Frontend templates rendered automatically

   Why It Works This Way

   1. Helm Dependency Resolution: When you run helm install, Helm automatically:
     •  Reads Chart.yaml dependencies
     •  Renders ALL templates from sub-charts in charts/ folder
     •  Combines everything into one release

   2. Value Inheritance: The wrapper's values.yaml passes values to sub-charts by key name:

   yaml
        # wrapper values.yaml
        connect-backend:      # <-- This entire block goes to connect-backend sub-chart
          replicaCount: 3
        connect-frontend:     # <-- This entire block goes to connect-frontend sub-chart
          replicaCount: 2

   3. No Duplication Needed: Sub-chart templates remain in their own folders - Helm merges them at install time.

   What Gets Rendered

   When you run helm template connect-wrapper .:

     # From charts/connect-backend/templates/deployment.yaml
     ---
     apiVersion: apps/v1
     kind: Deployment
     metadata:
       name: connect-connect-backend
     ...

     # From charts/connect-frontend/templates/deployment.yaml
     ---
     apiVersion: apps/v1
     kind: Deployment
     metadata:
       name: connect-connect-frontend
     ...

     # From templates/NOTES.txt (wrapper's own template)
     ---
     NOTES: Connect Application deployed!

   When to Add Templates to Wrapper

   Only add templates to the wrapper's templates/ folder for:
   •  Shared resources used by multiple sub-charts (e.g., shared ConfigMap, NetworkPolicy)
   •  Global resources like Namespace, ResourceQuota
   •  Cross-cutting concerns like PodSecurityPolicy
