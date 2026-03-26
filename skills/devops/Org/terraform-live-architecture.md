---
name: terraform-live-architecture
description: Expert guide for the Plateng-terraform-live multi-cloud infrastructure, covering AKS with AWS integrations, bastion provisioning, ArgoCD user management, and cross-cloud orchestration.
model: inherit
tools: ["Read", "LS", "Grep", "Glob", "Execute"]
---

You are an expert on the Plateng-terraform-live infrastructure repository. Help users understand and work with this multi-cloud Terraform setup.

## Architecture Overview

```
                                    AWS Route53
                                 (dev.webforxtech.com)
                                         │
                                         │ DNS
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Azure (East US)                                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Virtual Network (10.1.0.0/16)                     │   │
│  │                                                                      │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │                     AKS Subnet (10.1.0.0/20)                    │ │   │
│  │  │                                                                 │ │   │
│  │  │  ┌─────────────────────────────────────────────────────────┐   │ │   │
│  │  │  │              AKS Cluster (development-webforx-aks)      │   │ │   │
│  │  │  │                                                         │   │ │   │
│  │  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │   │ │   │
│  │  │  │  │   Traefik   │  │ cert-manager│  │  External DNS   │ │   │ │   │
│  │  │  │  │  (Ingress)  │  │ (AWS Route53│  │  (AWS Route53)  │ │   │ │   │
│  │  │  │  └─────────────┘  │  DNS-01)    │  └─────────────────┘ │   │ │   │
│  │  │  │                   └─────────────┘                       │   │ │   │
│  │  │  │  ┌─────────────┐  ┌─────────────────────────────────┐  │   │ │   │
│  │  │  │  │   ArgoCD    │  │  External Secrets Operator      │  │   │ │   │
│  │  │  │  │  (GitOps)   │  │  (HashiCorp Vault integration)  │  │   │ │   │
│  │  │  │  └─────────────┘  └─────────────────────────────────┘  │   │ │   │
│  │  │  └─────────────────────────────────────────────────────────┘   │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  │                                                                      │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │                     VM Subnet                                   │ │   │
│  │  │  ┌─────────────────────────────────────────────────────────┐   │ │   │
│  │  │  │  Bastion Host (Azure VM)                                │   │ │   │
│  │  │  │  - Configured via Ansible (docker, kubectl, users)      │   │ │   │
│  │  │  └─────────────────────────────────────────────────────────┘   │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Repository Structure

```
Plateng-terraform-live/
├── aws/
│   ├── development/          # Placeholder
│   └── staging/
│       ├── eks/              # EKS cluster + addons
│       ├── vpc/              # Networking
│       ├── rds/              # Databases (postgres, mariadb)
│       ├── ec2/bastion/      # AWS Bastion host
│       ├── parameter-store/  # SSM secrets (Vault creds stored here)
│       └── s3-backend/       # TF state bucket (SHARED by AWS+Azure)
├── azure/
│   └── development/
│       ├── az-aks/           # AKS + ALL addons (cert-manager, traefik, external-dns, argocd, ESO)
│       ├── az-argocd/        # ArgoCD standalone (optional)
│       ├── argocd-users/     # ArgoCD user management
│       ├── az-cert-manager/  # cert-manager standalone (optional)
│       ├── az-traefik/       # Traefik standalone (optional)
│       ├── az-external-dns/  # External DNS standalone (optional)
│       ├── external-secret-operator/  # ESO standalone (optional)
│       ├── az-virtual-network/
│       ├── az-public-ip/
│       └── virtual-machine/
│           ├── bastion-host/ # Azure Bastion VM
│           └── session-12/   # Training VM
└── packer/                   # AMI/image builds
```

## How One Terraform Code Orchestrates Across Multiple Clouds

### The Key: Shared Module Repository + AWS Services on Azure

```
Plateng-terraform-modules/          (Reusable modules)
    ├── aws/                        (AWS-specific: EKS, VPC, RDS, EC2)
    ├── azure/                      (Azure modules using AWS for DNS/TLS)
    │   ├── az-aks/
    │   ├── az-cert-manager/        → Uses AWS Route53 for DNS-01 challenge
    │   ├── az-external-dns/        → Updates AWS Route53 records
    │   ├── az-traefik/
    │   └── az-argocd/
    └── aks-eks/                    (Cloud-agnostic K8s modules)
        ├── argocd-users/           # Works on both AKS and EKS
        └── external-secret-operator/
```

### Cross-Cloud Integration Pattern

**Azure AKS cluster uses AWS services:**

```hcl
# In az-aks/main.tf - cert-manager uses AWS Route53
module "cert_manager" {
  source = "...//azure/az-cert-manager?ref=develop"
  
  az_cert_manager = {
    aws_region     = var.aws_region        # AWS region for Route53
    hosted_zone_id = var.cert_manager.hosted_zone_id  # Route53 zone
    domain_name    = var.cert_manager.domain_name
    # Let's Encrypt DNS-01 validation via Route53
  }
}

# External DNS updates Route53 from Azure AKS
module "external_dns" {
  source = "...//azure/az-external-dns?ref=develop"
  
  az_external_dns = {
    aws_region     = var.aws_region
    hosted_zone_id = var.external_dns.hosted_zone_id
    # Creates A records in Route53 for services
  }
}
```

### Why Use AWS Route53 for Azure AKS?

| Reason | Explanation |
|--------|-------------|
| Centralized DNS | All domains managed in one place (Route53) |
| Proven automation | External-dns and cert-manager have mature Route53 support |
| Cost efficiency | No need for Azure DNS zones |
| Team expertise | Team already familiar with Route53 |

### Unified S3 State Backend (Both Clouds)

```hcl
# Azure component stores state in AWS S3!
terraform {
  backend "s3" {
    bucket         = "webforx-staging-tf-state"
    key            = "azure/development/aks/dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "webforx-staging-tf-state-lock"
  }
}
```

### Cross-Cloud Dependencies via Remote State

```hcl
# ESO fetches Vault creds from AWS Parameter Store
data "aws_ssm_parameter" "vault_username" {
  name = var.vault_username_parameter_path
}

data "aws_ssm_parameter" "vault_password" {
  name            = var.vault_password_parameter_path
  with_decryption = true
}
```

## Deployment Order (Dependencies)

### Azure Development - Two Options

**Option 1: All-in-One AKS (Recommended)**
```
1. az-virtual-network  → VNet, subnets
2. az-public-ip        → Static IPs for bastion
3. az-aks              → AKS + cert-manager + traefik + external-dns + argocd + ESO (ALL IN ONE)
4. argocd-users        → User management
5. virtual-machine/bastion-host → Bastion VM (then Ansible configures it)
```

**Option 2: Standalone Components**
```
1. az-virtual-network  → VNet, subnets
2. az-public-ip        → Static IPs
3. az-aks              → AKS cluster only (addons disabled)
4. az-cert-manager     → TLS (standalone)
5. az-traefik          → Ingress (standalone)
6. az-external-dns     → DNS (standalone)
7. az-argocd           → ArgoCD (standalone)
8. external-secret-operator → Vault integration
9. argocd-users        → User management
```

### AWS Staging
```
1. s3-backend          → State bucket (bootstrap, SHARED by Azure too)
2. vpc                 → Networking
3. eks                 → EKS + all addons in one apply
4. rds/postgres        → Database
5. rds/mariadb         → Database
6. ec2/bastion         → AWS Bastion host
7. parameter-store     → Secrets (including Vault creds for Azure ESO)
```

## Bastion Host Provisioning

### Azure Bastion (azure/development/virtual-machine/bastion-host/)

Terraform provisions the VM:

```hcl
module "vm" {
  source = "...//azure/az-virtual-machine?ref=develop"
  
  vm = {
    name           = var.vm.name
    vm_size        = "Standard_B1s"
    admin_username = "azureuser"
    subnet_id      = data.terraform_remote_state.vnet.outputs.vm_subnet_id
    # Attaches NSG, public IP from remote state
  }
}
```

**Post-Provisioning with Ansible** (separate repo/workflow):
- Install Docker
- Install kubectl and configure kubeconfig for AKS
- Create user accounts
- Security hardening

### AWS Bastion (aws/staging/ec2/bastion/)

```hcl
module "bastion" {
  source = "...//aws/ec2?ref=develop"
  
  ec2 = {
    instance_type = "t3.micro"
    key_name      = var.bastion.key_name
    user_data     = var.bastion.user_data  # Cloud-init script
    # Security group, public IP attached
  }
}
```

Uses `user_data` for initial setup, or Ansible for post-config.

## ArgoCD User Creation with Terraform

### Architecture

The `argocd-users` module patches Kubernetes ConfigMaps/Secrets directly:

```
terraform.tfvars → Module → K8s API → ConfigMaps/Secrets → ArgoCD Server
```

### Resources Modified

| Resource | Purpose |
|----------|---------|
| `ConfigMap: argocd-cm` | User account definitions |
| `Secret: argocd-secret` | Bcrypt-hashed passwords |
| `ConfigMap: argocd-rbac-cm` | RBAC policy rules |

### User Configuration Example

```hcl
# terraform.tfvars
argocd_users = {
  namespace = "argocd"

  admin_users = {
    instructors = ["godwill_ocheme", "tia_leo", "eric_kemvou"]
    s10         = ["s10carol", "s10lexis", "s10ritchy"]
  }

  readonly_users = {
    others = ["read_only_user", "s10readonly"]
  }

  restart_argocd = true  # Auto-restart after changes

  rbac_policy_rules = [
    # Admin role
    "p, role:admin, applications, *, */*, allow",
    "p, role:admin, clusters, *, *, allow",
    # Readonly role
    "p, role:readonly, applications, get, */*, allow",
    "p, role:readonly, applications, sync, */*, deny",
  ]
}
```

### How It Works Internally

1. **Password Generation**: Each user gets password = username (initial)
2. **Bcrypt Hashing**: Terraform bcrypt provider hashes passwords
3. **ConfigMap Patch**: Adds `accounts.<username>: apiKey, login` to argocd-cm
4. **Secret Patch**: Adds `accounts.<username>.password: <bcrypt_hash>` to argocd-secret
5. **RBAC Patch**: Updates policy.csv in argocd-rbac-cm
6. **Server Restart**: Rolls out argocd-server deployment

### Adding Users Workflow

```bash
cd azure/development/argocd-users

# Edit terraform.tfvars - add user to appropriate group
vim terraform.tfvars

terraform plan   # Review changes
terraform apply  # Apply (auto-restarts ArgoCD)
```

### Verify Users

```bash
# Check user in ConfigMap
kubectl get cm argocd-cm -n argocd -o yaml | grep accounts

# Check RBAC
kubectl get cm argocd-rbac-cm -n argocd -o jsonpath='{.data.policy\.csv}'

# Test login
argocd login argocd.dev.webforxtech.com --username <user> --password <user>
```

## EKS Cluster Addons (AWS)

The EKS main.tf deploys cluster + all addons in one apply:

```hcl
module "eks_control_plane"           # EKS cluster
module "eks_node_group"              # Worker nodes
module "aws_auth_config"             # IAM → K8s RBAC mapping
module "eks_storage_class"           # EBS storage class
module "eks_cluster_autoscaler"      # Node autoscaling
module "eks_ebs_csi_driver"          # EBS CSI driver
module "eks_external_dns"            # Route53 automation
module "eks_load_balancer_controller" # ALB/NLB controller
module "eks_metrics_server"          # HPA metrics
module "eks_namespaces"              # Namespace creation
```

## External Secrets Operator (ESO)

Integrates HashiCorp Vault with Kubernetes:

```hcl
module "external_secrets" {
  source = "...//aks-eks/external-secret-operator?ref=develop"

  external_secret_operator = {
    vault_secret_store = {
      enabled  = true
      address  = "https://vault.example.com"
      username = data.aws_ssm_parameter.vault_username[0].value
      password = data.aws_ssm_parameter.vault_password[0].value
    }
  }
}
```

Vault credentials are fetched from AWS Parameter Store at apply time.

## Common Commands

```bash
# Initialize any component
cd azure/development/az-aks
terraform init

# Plan with var file
terraform plan

# Apply
terraform apply

# Destroy (careful!)
terraform destroy
```

## Troubleshooting

### State Lock Issues
```bash
terraform force-unlock <LOCK_ID>
```

### Module Update
```bash
terraform init -upgrade
```

### Check Remote State
```bash
aws s3 ls s3://webforx-staging-tf-state/ --recursive
```
