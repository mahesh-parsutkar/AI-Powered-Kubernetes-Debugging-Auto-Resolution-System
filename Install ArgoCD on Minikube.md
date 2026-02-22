# Installing Minikube and ArgoCD on Ubuntu 24.04 LTS

## Step #1: Install Minikube on Ubuntu 24.04 LTS

### Update System Packages
```bash
sudo apt update -y
```

### Install Minikube Dependencies
```bash
sudo apt install curl wget apt-transport-https -y
```

### Install Docker
```bash
sudo apt install docker.io
```

### Configure Docker to Run Without `sudo`
```bash
sudo usermod -aG docker $USER
sudo chmod 666 /var/run/docker.sock
```

### Check for Virtualization Support
```bash
egrep -q 'vmx|svm' /proc/cpuinfo && echo yes || echo no
```

### Install KVM and Other Tools
```bash
sudo apt install qemu-kvm libvirt-clients libvirt-daemon-system bridge-utils virtinst libvirt-daemon
```

### Download the Latest Minikube Binary
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
```

### Install Minikube
```bash
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### Verify Minikube Installation
```bash
minikube version
```
**Output:**
```
minikube version: v1.33.1
commit: 5883c09216182566a63dff4c326a6fc9ed2982ff
```

## Step #2: Install `kubectl` on Minikube

`kubectl` is a command-line utility used to interact with a Kubernetes cluster.

### Download `kubectl`
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
```

### Set Executable Permissions
```bash
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

### Verify `kubectl` Installation
```bash
kubectl version --client --output=yaml
```
**Output:**
```
clientVersion:
  buildDate: "2024-06-11T20:29:44Z"
  compiler: gc
  gitCommit: 39683505b630ff2121012f3c5b16215a1449d5ed
  gitTreeState: clean
  gitVersion: v1.30.2
  goVersion: go1.22.4
  major: "1"
  minor: "30"
  platform: linux/amd64
kustomizeVersion: v5.0.4-0.20230601165947-6ce0bf390ce3
```

## Step #3: Start Minikube on Ubuntu 24.04 LTS

### Start Minikube with Docker Driver
```bash
minikube start --vm-driver docker
```
**Output:**
```
* minikube v1.33.1 on Ubuntu 24.04 (xen/amd64)
* Using the docker driver based on user configuration
... (truncated for brevity) ...
```

### Check Minikube Status
```bash
minikube status
```
**Output:**
```
minikube
  type: Control Plane
  host: Running
  kubelet: Running
  apiserver: Running
  kubeconfig: Configured
```

### Verify Kubernetes Cluster
```bash
kubectl cluster-info
kubectl get nodes
```

### Create Deployment and Service
```bash
kubectl create deployment my-app --image=nginx
kubectl expose deployment my-app --name=my-app-svc --type=NodePort --port=80
kubectl get svc my-app-svc
minikube service my-app-svc --url
```

## Step #4: Install ArgoCD on Minikube

### Create Namespace for ArgoCD
```bash
kubectl create ns argocd
```

### Install ArgoCD
```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.5.8/manifests/install.yaml
```

### Verify Installation
```bash
kubectl get all -n argocd
```

## Step #5: Access ArgoCD UI on Browser

### Expose ArgoCD Server
```bash
kubectl port-forward svc/argocd-server -n argocd --address 0.0.0.0 8080:443
```
Access the UI at `http://localhost:8080` or `http://<IP>:8080`.

### Retrieve Admin Password
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

## Step #6: Deploy an App on ArgoCD

### Create a New Application
1. Log in to the ArgoCD UI.
2. Click `+ New App`.
3. Configure the app:
   - **Name:** `guestbook`
   - **Repository URL:** Your GitHub repo URL
   - **Path:** `guestbook`
   - **Cluster URL:** `https://kubernetes.default.svc`
   - **Namespace:** `default`
4. Click `Create`.

### Synchronize and Deploy
1. Select the app.
2. Click `Synchronize` to deploy.

Your app is now deployed using ArgoCD!
