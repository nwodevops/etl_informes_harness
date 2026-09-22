#!/usr/bin/env bash
# Harness — smoke: RData (Python) + FORM/CSEP (hop-run) → 3 tablas Oracle (hard-fail).
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

LOG="$(mktemp)"
trap 'rm -f "$LOG"' EXIT

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
[ -f h2/lib/h2-2.4.240.jar ] || fail "jar H2 no encontrado"
find_hop_run >/dev/null || fail "hop-run.sh no encontrado (export HOP_HOME o instala en ~/apps/hop)"
if [ ! -x .venv/bin/python ]; then
  fail "venv ausente o roto. A mano: python3 -m venv .venv && .venv/bin/python -m pip install -r python/requirements.txt"
fi
"$PY" -c "import yaml, pandas, jaydebeapi" 2>/dev/null \
  || fail "el .venv no tiene dependencias. .venv/bin/python -m pip install -r python/requirements.txt"
if [ ! -f project-config.json ]; then
  step "Generando project-config.json (switch-env local)"
  ./switch-env.sh local
fi

step "Reset H2 + DDL"
./h2/scripts/reset_and_create.sh

step "Python create STG"
"$PY" python/stg/create_stg.py

step "Stage RData → STG_INF_CONSOL"
command -v Rscript >/dev/null 2>&1 || fail "Rscript no está en PATH"
"$PY" python/stage/stage_rdata.py

step "Python main → DW_INF_CONSOL_RDATA (TRUNCATE)"
set +e
"$PY" python/main.py 2>&1 | tee "$LOG"
MAIN_RC=${PIPESTATUS[0]}
set -e
[ "$MAIN_RC" -eq 0 ] || fail "python/main.py terminó con código $MAIN_RC"

run_hop_pipeline "pipelines/pl_form_informes.hpl"
run_hop_pipeline "pipelines/pl_csep_informes.hpl"

step "Comprobando salidas RData"
grep -q "Salida RESULTADO" "$LOG" || fail "no hay Salida RESULTADO en el log"
grep -q "DW:.*DW_INF_CONSOL_RDATA" "$LOG" || fail "no hay carga Oracle DW_INF_CONSOL_RDATA en el log"
grep -q "Excel:" "$LOG" || warn "no se escribió Excel (opcional)"
if grep -q '\${[A-Za-z0-9_]\+}' "$LOG"; then
  fail "log contiene variables Hop sin resolver"
fi

echo
echo -e "${GREEN}HARNESS OK${NC} — 3 tablas: DW_INF_CONSOL_RDATA (Python), DW_INF_CONSOL_FORM + DW_INF_CSEP_INFORMES_VIEW (Hop)"
