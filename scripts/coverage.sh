#!/usr/bin/env bash
# Monorepo coverage: backend (pytest + pytest-cov) and frontend (Vitest + @vitest/coverage-v8).
# Run from repo root:  bash scripts/coverage.sh
# Windows: use Git Bash or WSL (not plain cmd.exe).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Backend (pytest) ==="
cd "$ROOT/backend"
# pytest-cov is not in requirements.txt; install for this invocation only.
python -m pip install -q pytest-cov
python -m pytest tests/ \
  --cov=flaskr \
  --cov-report=term-missing:skip-covered \
  --cov-report=html:"$ROOT/coverage/backend-html"

echo ""
echo "=== Frontend (Vitest) ==="
cd "$ROOT/frontend"
npm install --silent
npm run test:coverage

echo ""
echo "HTML reports (open index.html in a browser):"
echo "  Backend:  $ROOT/coverage/backend-html/index.html"
echo "  Frontend: $ROOT/coverage/frontend-html/index.html"
echo "Text summary printed above; totals are also in each HTML tree."
