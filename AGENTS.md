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

```bash
./switch-env.sh local
./init.sh
~/apps/hop/hop-gui.sh   # → wf_main.hwf
```

**Windows** (el repo trae ambos): `.\switch-env.ps1 local|remote` (genera `project-config.json` si falta) y H2 vía `h2/scripts/*.bat` (server como **tarea programada** `H2_SERVICE_MEM_CSEP`, NO se para desde el workflow). Correr `init.bat [local|remote]` (default `remote`). `init.bat` agrega `Rscript` al PATH desde `C:\Program Files\R\R-*`. Hop Windows en `D:\Eder\hop` (`hop-gui.bat`, `hop-run.bat`); el workflow Windows es [`workflows/wf_main_windows.hwf`](workflows/wf_main_windows.hwf). `switch-env.ps1` no pisa valores reales ya presentes en `project-config.json` si la plantilla trae placeholders `<...>`.

`init.sh` solo corre desde Git Bash/WSL; ahí `.venv/bin/python` no existe (el venv es `.venv\Scripts\python.exe`), así que el script cae a `python3` del PATH y requiere las deps globales.

## Verificación: no es offline

`init.sh`/`init.bat` validan `java` + `h2/lib/h2-2.4.240.jar` + `.venv/` con `pyyaml pandas jaydebeapi pymysql` + **Rscript**, y corren `create_stg.py` → `stage_rdata.py` → `stage_mysql.py` → `main.py`.

- Necesita BD vivas: `stage_mysql.py` lee **MySQL HEC** (gappsdb) y `main.py` escribe **Oracle DW**. En el entorno `remote` real: MySQL **10.1.1.217:3306** (la IP pública 209.45.104.78 NO responde desde esta red) y Oracle **10.6.0.15:1532/dvoefacore**, usuario **REPOCSEP** (las tablas quedan en esquema `REPOCSEP`, no `APP`). Con creds placeholder `<...>` → falla con `require_live_conn`.
- Falla si el log tiene `${VAR}` literal (variable Hop sin resolver = bug).

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

**Windows:** el workflow usa SHELL en bash (solo Linux); la variante Windows es [`workflows/wf_csep_informes_windows.hwf`](workflows/wf_csep_informes_windows.hwf) (SHELL en cmd → `python\ddl_csep_informes.py` con `.venv\Scripts\python.exe`). `ddl_csep_informes.py` es Python puro + oracledb (thin; su `init_oracle_client()` falla silencioso si no hay Instant Client) — verificado en esta PC: `SISUD.CSEP_INFORMES_VIEW` (57 cols) → `CREATE CSEP_INFORMES` en `REPOCSEP`.

## Nuevo proyecto

Este repo es un cascarón. Fuentes → `inputs.yaml`. Lecturas → `python/io/leer_h2.py`. Transformación → `logica/<tu>.py`. Destino DW → `escribir_oracle.py`.
