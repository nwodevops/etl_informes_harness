#!/usr/bin/env bash
# Harness diario: FORM + CSEP (hop-run). RData/backup = wf_create_stg (bajo demanda).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

fail() { echo -e "${RED}FAIL:${NC} $*" >&2; exit 1; }
warn() { echo -e "${YELLOW}AVISO:${NC} $*"; }
step() { echo -e "${GREEN}==>${NC} $*"; }

PY=python3
[ -x .venv/bin/python ] && PY=.venv/bin/python

HOP_PROJECT="${HOP_PROJECT:-etl_informes_harness}"
HOP_RUNCONFIG="${HOP_RUNCONFIG:-local}"

find_hop_run() {
  if [ -n "${HOP_HOME:-}" ] && [ -x "${HOP_HOME}/hop-run.sh" ]; then
    echo "${HOP_HOME}/hop-run.sh"
    return 0
  fi
  if [ -x "${HOME}/apps/hop/hop-run.sh" ]; then
    echo "${HOME}/apps/hop/hop-run.sh"
    return 0
  fi
  if command -v hop-run.sh >/dev/null 2>&1; then
    command -v hop-run.sh
    return 0
  fi
  return 1
}

run_hop_pipeline() {
  local file="$1"
  local hop
  hop="$(find_hop_run)" || fail "hop-run.sh no encontrado (HOP_HOME o ~/apps/hop)"
  step "hop-run ${file}"
  "${hop}" -j "${HOP_PROJECT}" -r "${HOP_RUNCONFIG}" -f "${ROOT}/${file}" -l Basic
}

step "Validando feature_list.json"
"$PY" - <<'PY'
import json, sys
from pathlib import Path
data = json.loads(Path("feature_list.json").read_text(encoding="utf-8"))
active = [f for f in data.get("features", []) if f.get("status") == "in_progress"]
if len(active) > 1:
    sys.exit(f"más de una in_progress: {', '.join(f['id'] for f in active)}")
print(f"features: {len(data.get('features', []))}, in_progress: {len(active)}")
PY

step "Prerrequisitos"
command -v java >/dev/null 2>&1 || fail "java no está en PATH"
find_hop_run >/dev/null || fail "hop-run.sh no encontrado (export HOP_HOME o instala en ~/apps/hop)"
if [ ! -f project-config.json ]; then
  step "Generando project-config.json (switch-env local)"
  ./switch-env.sh local
fi

run_hop_pipeline "pipelines/pl_form_informes.hpl"
run_hop_pipeline "pipelines/pl_csep_informes.hpl"

echo
echo -e "${GREEN}HARNESS OK${NC} — diario FORM + CSEP (Hop). RData: play wf_create_stg bajo demanda."
