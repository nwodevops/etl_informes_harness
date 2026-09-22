# AGENTS.md — mapa para agentes (cascarón Hop + H2 + Python)

ETL **Apache Hop + H2 in-memory + Python**. Arquitectura: [`docs/arquitectura.md`](docs/arquitectura.md).

**Verificación:** [`./init.sh`](init.sh) [`./init.bat`](init.bat) debe terminar en **`HARNESS OK`**. Criterios: [`CHECKPOINTS.md`](CHECKPOINTS.md) (algunos checkpoints Fase 1-3 aún hablan del `demo.py`/arquetipo; el flujo real es informes RData + FORM).

## Harness

| Archivo | Propósito |
|---|---|
| [`feature_list.json`](feature_list.json) | Alcance; **una** `in_progress` a la vez |
| [`progress/current.md`](progress/current.md) | Plan de sesión activa |
| [`progress/history.md`](progress/history.md) | Bitácora append-only |
| [`docs/harness/workflow.md`](docs/harness/workflow.md) | Roles líder / implementador / revisor |
| [`docs/harness/platform.md`](docs/harness/platform.md) | Hop, H2, variables |

## Skill

- [`.agents/skills/hop-python-etl/SKILL.md`](.agents/skills/hop-python-etl/SKILL.md)

## Inicio rápido

**Linux**

```bash
./switch-env.sh local
./init.sh
~/apps/hop/hop-gui.sh   # → wf_main.hwf
```

**Windows**

```powershell
.\switch-env.ps1 local   # o remote
.\init.bat               # default remote; o: init.bat local
# Hop GUI → workflows\wf_main_windows.hwf
```

- Python: `.venv\Scripts\python.exe`
- H2: `h2\scripts\reset_and_create.bat` (servicio/tarea `H2_SERVICE_MEM_CSEP` según scripts bat)
- `Rscript`: se busca en `C:\Program Files\R\R-*` si no está en PATH
- `switch-env.ps1` no pisa valores reales de `project-config.json` si la plantilla trae placeholders `<...>`

## Verificación

`init.sh` / `init.bat` → **HARNESS OK** con **3 tablas** en oracle_dw:

1. `DW_INF_CONSOL_RDATA`
2. `DW_INF_CONSOL_FORM` (siempre; vacía si MySQL cae)
3. `DW_INF_CSEP_INFORMES_VIEW` (stub vacío si SISUD cae)

Requiere Java, jar H2, `.venv` (`pyyaml pandas jaydebeapi pymysql`), **Rscript**, y Oracle DW vivo. MySQL/SISUD van en modo soft.

## Reglas críticas

1. **Un solo `.py`** en `logica/` (hoy: `informes_rdata.py`) — solo reglas post-STG.
2. **Sin secretos** en git. `project-config.json` es generado; gitignored: `client_secret.json`, `docs/credenciales/`, `input/input_mysql/tablas.txt`, `h2/sql/02_stg.sql`. Los `environments/*.json` traen valores placeholder `<...>` **más hints reales en las `description`** (apuntan a `docs/credenciales/`) — no commitear valores nuevos.
3. **Sin `${VAR}` literal** en logs Hop = variable mal definida.
4. `logica/` no abre conexiones. I/O en `python/io/`. Homologación RData en `python/rdata/` + `stage_rdata.py`.
5. `python/io/leer_h2.py` y sus pares se cargan por ruta en `main.py`; **no** hacer `import io` (choca con stdlib).

## Flujo informes (RData + FORM + CSEP)

`wf_main` / `./init.sh` dejan **3 tablas** en oracle_dw:

1. `DW_INF_CONSOL_RDATA` (RData)
2. `DW_INF_CONSOL_FORM` (MySQL HEC; **siempre** se crea, aunque MySQL caiga o vaya vacío)
3. `DW_INF_CSEP_INFORMES_VIEW` (vista SISUD `CSEP_INFORMES_VIEW` vía DDL + `pl_csep_informes`; stub vacío si SISUD cae)

`inputs.yaml` → `create_stg.py` → `stage_rdata.py` / `stage_mysql.py --soft` → `main.py` → `ddl_csep_informes.py` + pipeline Hop.  
Mapa RData: [`docs/rdata_column_map.md`](docs/rdata_column_map.md). SQL HEC: [`input/input_mysql/`](input/input_mysql/).

| OS | Harness | Workflow Hop |
|---|---|---|
| Linux | [`init.sh`](init.sh) | [`workflows/wf_main.hwf`](workflows/wf_main.hwf) |
| Windows | [`init.bat`](init.bat) | [`workflows/wf_main_windows.hwf`](workflows/wf_main_windows.hwf) |

CSEP solo: [`wf_csep_informes.hwf`](workflows/wf_csep_informes.hwf) / [`wf_csep_informes_windows.hwf`](workflows/wf_csep_informes_windows.hwf).

## Nuevo proyecto

Este repo es un cascarón. Fuentes → `inputs.yaml`. Lecturas → `python/io/leer_h2.py`. Transformación → `logica/<tu>.py`. Destino DW → `escribir_oracle.py`.
