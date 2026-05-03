# Train models on Kubernetes

This project supports running training jobs on a Kubernetes cluster for resource management and isolation per model.

## Setup Steps

### 1. Prepare your cluster

Ensure you have a Kubernetes cluster available. For local development, you can use [k3s](https://k3s.io/).

### 2. Create a ServiceAccount and permissions

Run these commands in your cluster:

```bash
# Create namespace (optional, can use 'default' instead)
kubectl create namespace nwdaf-ml

# Create ServiceAccount, Role, and bindings
kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: nwdaf-ml-trainer
  namespace: nwdaf-ml
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: nwdaf-ml-job-manager
  namespace: nwdaf-ml
rules:
  - apiGroups: ["batch"]
    resources: ["jobs"]
    verbs: ["create", "get", "list", "delete"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: nwdaf-ml-job-manager-binding
  namespace: nwdaf-ml
subjects:
  - kind: ServiceAccount
    name: nwdaf-ml-trainer
    namespace: nwdaf-ml
roleRef:
  kind: Role
  name: nwdaf-ml-job-manager
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: nwdaf-ml-metrics-reader
rules:
  - apiGroups: ["metrics.k8s.io"]
    resources: ["pods"]
    verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: nwdaf-ml-metrics-reader-binding
subjects:
  - kind: ServiceAccount
    name: nwdaf-ml-trainer
    namespace: nwdaf-ml
roleRef:
  kind: ClusterRole
  name: nwdaf-ml-metrics-reader
  apiGroup: rbac.authorization.k8s.io
EOF
```

### 3. Get cluster credentials

Run these commands to retrieve the necessary values:

```bash
# Get the bearer token
TRAIN_KUBE_TOKEN=$(kubectl create token nwdaf-ml-trainer --namespace nwdaf-ml --duration=8760h)

# Get cluster API server URL from kubeconfig
TRAIN_KUBE_HOST=$(kubectl config view -o jsonpath='{.clusters[0].cluster.server}')

# Get CA certificate (base64-encoded)
TRAIN_KUBE_CA_CERT=$(kubectl config view --raw --flatten -o jsonpath='{.clusters[0].cluster.certificate-authority-data}')

# Print them out for copying
echo "TRAIN_KUBE_HOST=$TRAIN_KUBE_HOST"
echo "TRAIN_KUBE_TOKEN=$TRAIN_KUBE_TOKEN"
echo "TRAIN_KUBE_CA_CERT=$TRAIN_KUBE_CA_CERT"
```

### 4. Configure environment

Update your `.env` file with the values from step 3:

```bash
TRAIN_USE_KUBE=true
TRAIN_KUBE_HOST=https://10.255.28.159:6443
TRAIN_KUBE_TOKEN=eyJhbGciOiJSUzI1NiIsImtpZCI6IklIWk5jb3ZpeF81NG44UkJDRHozcnNYMWhJaC16VjFlUnJrMF9ka091cE0ifQ...
TRAIN_KUBE_CA_CERT=LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUJlRENDQVIyZ0F3SUJBZ0lCQURBS0JnZ3Foa2pPUFFRREFqQWpNU0V3SHdZRFZRUUREQmhyTTNNdGMyVnkK...
TRAIN_KUBE_NAMESPACE=nwdaf-ml
TRAIN_KUBE_IMAGE=<your-container-registry>/pei-nwdaf-ml-trainer:latest
```

> Note: `TRAIN_KUBE_NAMESPACE` can be any namespace (e.g., `default`), but must match the namespace where the ServiceAccount was created in step 2.

### 5. Rebuild and restart

```bash
docker compose up -d --build mlservice
```

## Verify setup

Check if training jobs run on Kubernetes:

```bash
# List active training jobs
kubectl get jobs -l app=ml-train -n nwdaf-ml

# View job logs
kubectl logs -f job/ml-train-<model_id>-<job_id> -n nwdaf-ml
```
