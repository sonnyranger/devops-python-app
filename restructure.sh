#!/usr/bin/env bash
set -euo pipefail

echo "==> Restructuring project..."

# Run only from project root
if [[ ! -d "app" || ! -d "k8s" ]]; then
  echo "Error: run this script from the project root (devops-python-app)"
  exit 1
fi

# Create target dirs
mkdir -p k8s/app
mkdir -p k8s/db
mkdir -p k8s/monitoring
mkdir -p .github/workflows

move_if_exists() {
  local src="$1"
  local dst="$2"
  if [[ -f "$src" ]]; then
    mv "$src" "$dst"
    echo "Moved: $src -> $dst"
  fi
}

# Move app manifests
move_if_exists "k8s/deployment.yaml" "k8s/app/deployment.yaml"
move_if_exists "k8s/service.yaml" "k8s/app/service.yaml"
move_if_exists "k8s/ingress.yaml" "k8s/app/ingress.yaml"

# Move db manifest
move_if_exists "k8s/postgres.yaml" "k8s/db/postgres.yaml"

# Move monitoring manifests
move_if_exists "k8s/grafana-deployment.yaml" "k8s/monitoring/grafana-deployment.yaml"
move_if_exists "k8s/grafana-pvc.yaml" "k8s/monitoring/grafana-pvc.yaml"
move_if_exists "k8s/grafana-svc.yaml" "k8s/monitoring/grafana-svc.yaml"

move_if_exists "k8s/prometheus-configmap.yaml" "k8s/monitoring/prometheus-configmap.yaml"
move_if_exists "k8s/prometheus-deployment.yaml" "k8s/monitoring/prometheus-deployment.yaml"
move_if_exists "k8s/prometheus-pvc.yaml" "k8s/monitoring/prometheus-pvc.yaml"
move_if_exists "k8s/prometheus-svc.yaml" "k8s/monitoring/prometheus-svc.yaml"

move_if_exists "k8s/node-exporter-deployment.yaml" "k8s/monitoring/node-exporter-deployment.yaml"
move_if_exists "k8s/node-exporter-svc.yaml" "k8s/monitoring/node-exporter-svc.yaml"

# Move workflow only if it exists in root and not already in .github/workflows
if [[ -f "ci-cd.yml" && ! -f ".github/workflows/ci-cd.yml" ]]; then
  mv "ci-cd.yml" ".github/workflows/ci-cd.yml"
  echo "Moved: ci-cd.yml -> .github/workflows/ci-cd.yml"
fi

# Create .gitignore if missing
if [[ ! -f ".gitignore" ]]; then
  cat > .gitignore <<'EOF'
__pycache__/
*.pyc
.env
.venv/
venv/
EOF
  echo "Created: .gitignore"
fi

echo
echo "==> New structure:"
find . -maxdepth 3 \( -path './.git' -o -path './.terraform' \) -prune -o -print | sort

echo
echo "==> Done."
echo "Next:"
echo "  git status"
echo "  kubectl apply -f k8s/"
