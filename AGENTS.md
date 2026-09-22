# AGENTS.md — mapa para agentes (cascarón Hop + H2 + Python)

ETL **Apache Hop + H2 in-memory + Python**. Arquitectura: [`docs/arquitectura.md`](docs/arquitectura.md).

**Verificación:** [`./init.sh`](init.sh) [`./init.bat`](init.bat) debe terminar en **`HARNESS OK`**. Criterios: [`CHECKPOINTS.md`](CHECKPOINTS.md).

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
# Primera vez / DW vacío: Hop → wf_create_stg.hwf  (o: .venv/bin/python python/stg/ensure_dw_tables.py)
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
- Hop: `HOP_HOME` o `~/apps/hop` (`hop-run` obligatorio en init)
- H2: `h2\scripts\reset_and_create.bat`
- `Rscript`: se busca en `C:\Program Files\R\R-*` si no está en PATH

## Verificación

`init.sh` / `init.bat` → **HARNESS OK** con **3 tablas** en oracle_dw (precreadas en [`sql/dw/`](sql/dw/)):

1. `DW_INF_CONSOL_RDATA` — Python TRUNCATE+INSERT
2. `DW_INF_CONSOL_FORM` — Hop `pl_form_informes` (hard-fail si MySQL cae)
3. `DW_INF_CSEP_INFORMES_VIEW` — Hop `pl_csep_informes` (hard-fail si SISUD cae)

Requiere Java, jar H2, `.venv` (`pyyaml pandas jaydebeapi`), **Rscript**, **hop-run**, Oracle DW, MySQL y SISUD vivos.

## Preferir Apache Hop

**Siempre intentar Hop primero** para extract/load 1:1 (TableInput → TableOutput truncate). Python solo cuando hace falta homologación, QA, joins o reglas en `logica/`.

| Workflow | Rol |
|---|---|
| [`workflows/wf_create_stg.hwf`](workflows/wf_create_stg.hwf) / [`wf_create_stg_windows.hwf`](workflows/wf_create_stg_windows.hwf) | **Diseño / DDL:** crea `STG_*` en H2 **y** asegura `DW_INF_*` en oracle_dw (CREATE si faltan, sin DROP). Primera vez o cuando falten tablas. |
| [`workflows/wf_main.hwf`](workflows/wf_main.hwf) / [`wf_main_windows.hwf`](workflows/wf_main_windows.hwf) | **Corrida habitual:** DW ya creadas; TRUNCATE + carga. |

Oracle DW: también documentado en [`sql/dw/`](sql/dw/); lo habitual es dejarlo a `wf_create_stg` → `python/stg/ensure_dw_tables.py`. H2 es in-memory: cada `wf_main` recreate STG porque el mem se pierde al reset.

## Reglas críticas

1. **Un solo `.py`** en `logica/` (hoy: `informes_rdata.py`) — solo reglas post-STG RData.
2. **Sin secretos** en git. `project-config.json` es generado; gitignored: `client_secret.json`, `docs/credenciales/`, `input/input_mysql/tablas.txt`, `h2/sql/02_stg.sql`.
3. **Sin `${VAR}` literal** en logs Hop = variable mal definida.
4. `logica/` no abre conexiones. I/O en `python/io/`. Homologación RData en `python/rdata/` + `python/stage/stage_rdata.py`.
5. `python/io/leer_h2.py` y sus pares se cargan por ruta en `main.py`; **no** hacer `import io` (choca con stdlib).
6. Destino Oracle: **TRUNCATE** en corrida (no DROP). CREATE si faltan → `wf_create_stg` / `python/stg/ensure_dw_tables.py` (ref. [`sql/dw/`](sql/dw/)).
7. Cargas 1:1 (FORM, CSEP, etc.) → **pipelines Hop**, no scripts Python de extract/load.

## Flujo informes (RData + FORM + CSEP)

```
inputs.yaml → python/stg/create_stg.py → python/stage/stage_rdata.py
  → python/main.py → DW_INF_CONSOL_RDATA
hop-run pipelines/pl_form_informes.hpl → DW_INF_CONSOL_FORM
hop-run pipelines/pl_csep_informes.hpl → DW_INF_CSEP_INFORMES_VIEW
```

Mapa RData: [`docs/rdata_column_map.md`](docs/rdata_column_map.md). SQL HEC: [`input/input_mysql/`](input/input_mysql/). Layout: [`python/LEEME.md`](python/LEEME.md).

| OS | Primera vez (DDL) | Corrida habitual |
|---|---|---|
| Linux | [`wf_create_stg.hwf`](workflows/wf_create_stg.hwf) | [`wf_main.hwf`](workflows/wf_main.hwf) |
| Windows | [`wf_create_stg_windows.hwf`](workflows/wf_create_stg_windows.hwf) | [`wf_main_windows.hwf`](workflows/wf_main_windows.hwf) |

Misma lógica en ambos OS; solo cambian shells `.sh` vs `.bat`.

CSEP standalone: [`wf_csep_informes*.hwf`](workflows/wf_csep_informes.hwf) (solo pipeline).

## Nuevo proyecto

Fuentes STG → `inputs.yaml`. Lecturas → `python/io/leer_h2.py`. Transformación → `logica/<tu>.py`. Destino DW RData → `escribir_oracle.py` (TRUNCATE). Cargas 1:1 → pipelines Hop.
