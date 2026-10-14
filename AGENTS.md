# AGENTS.md — mapa para agentes (`etl_informes_harness`)

ETL **Apache Hop + H2 in-memory + Python** para informes de supervisión (FORM, CSEP y consolidado RData), con dual-write a **Oracle DW (`oracle_dw`)** y **MySQL DW (`mysql_dw`)**.

**Verificación diaria:** `./init.sh` (Linux) o `init.bat remote` (Windows) debe terminar en **`HARNESS OK`**. Criterios: [`CHECKPOINTS.md`](CHECKPOINTS.md).

## Modos de ejecución y flujos

| Flujo | Entrypoint | Qué ejecuta | Tablas destino (`oracle_dw` + `mysql_dw`) |
|---|---|---|---|
| **Diario** (sin H2) | `./init.sh`, `init.bat`, `run_wf_main.bat`, `workflows/wf_main*.hwf` | Hop `pl_form_informes.hpl` + `pl_csep_informes.hpl` + `python/check_form_pk.py` | `DW_INF_CONSOL_FORM` (81 cols, con `FECHA_CARGA`), `DW_INF_CSEP_INFORMES_VIEW` |
| **Bajo demanda** (RData + DDL) | `workflows/wf_create_stg.hwf` / `wf_create_stg_windows.hwf` | Reset H2 → `create_stg.py` → `ensure_dw_tables.py` → `stage_rdata.py` → `python/main.py` (`logica/informes_rdata.py` + `rdata/oficina.py`) | `DW_INF_CONSOL_RDATA` (81 cols: incluye `IDUF_SIG`; sin `FECHA_CARGA` ni `IDADMINISTRADO`) |

- **DDL idempotente (sin DROP TABLE):** `.venv/bin/python python/stg/ensure_dw_tables.py` crea o aplica `ALTER TABLE ADD` sobre las 3 tablas en `oracle_dw` y `mysql_dw`. Si `DW_INF_CONSOL_FORM` o `DW_INF_CONSOL_RDATA` aún tienen `OD`, `CATEG`, `COMPET`, `TIPO_OD` o `IDADMINISTRADO`, las quita con `DROP COLUMN`. SQL de referencia en `sql/dw/` y `sql/dw/mysql/`.
- **Fuente MySQL vs Destino MySQL:** La conexión Hop `mysql` (`DB_MYSQL_*`) es la **fuente** HEC (`gappsdb`). La conexión `mysql_dw` (`DB_MYSQL_DW_*`) es el **destino espejo DW**.
- **SQL de FORM embebido:** `pipelines/pl_form_informes.hpl` embebe el SELECT de `input/input_mysql/vw_inf_consol_simil.sql` (con `NOW() AS FECHA_CARGA`). Si cambia el query de FORM, actualizar el `.sql` y el `<sql>` dentro de `pl_form_informes.hpl`. El `.sql` no lo ejecuta Hop: es referencia para probar a mano en MySQL `gappsdb`.

## Harness

| Archivo | Propósito |
|---|---|
| [`feature_list.json`](feature_list.json) | Alcance; **una** `in_progress` a la vez |
| [`progress/current.md`](progress/current.md) | Plan de sesión activa |
| [`progress/history.md`](progress/history.md) | Bitácora append-only |
| [`docs/harness/workflow.md`](docs/harness/workflow.md) | Roles líder / implementador / revisor |
| [`docs/harness/platform.md`](docs/harness/platform.md) | Hop, H2, variables |

## Skills

- [`.agents/skills/hop-python-etl/SKILL.md`](.agents/skills/hop-python-etl/SKILL.md) — capas Hop / H2 / Python
- [`.agents/skills/linux-windows-parity/SKILL.md`](.agents/skills/linux-windows-parity/SKILL.md) — el cambio de Linux se espeja en `init.bat`, `wf_main_windows.hwf`, `wf_create_stg_windows.hwf` y `run_wf_main.bat`
- [`.agents/skills/etl-run-logs/SKILL.md`](.agents/skills/etl-run-logs/SKILL.md) — cada corrida deja bitácora en `logs/`
- [`.agents/skills/release-etl/SKILL.md`](.agents/skills/release-etl/SKILL.md) — corta la rama `release` solo con el ETL

## Inicio rápido

### Linux (desarrollo, entorno `local`)

```bash
./switch-env.sh local
./init.sh
~/apps/hop/hop-gui.sh   # → workflows/wf_main.hwf o wf_create_stg.hwf
```

### Windows (este equipo, entorno `remote`)

```bat
powershell -ExecutionPolicy Bypass -File switch-env.ps1 remote
init.bat remote
REM Programador de tareas → run_wf_main.bat
REM Hop GUI → workflows\wf_main_windows.hwf / wf_create_stg_windows.hwf
```

## Entornos

Variables de conexión en `environments/local.json` y `environments/remote.json`. Credenciales reales solo en `docs/credenciales/*.txt` (gitignored), aplicadas por `switch-env.sh` / `switch-env.ps1` para generar `project-config.json` (gitignored).

## Reglas críticas

1. **Prioridad:** Apache Hop mueve las filas 1:1 (`pl_form_informes`, `pl_csep_informes`). Python en `python/rdata/` + `logica/informes_rdata.py` homologa y procesa los `.RData` vía H2 (`STG_INF_CONSOL`).
2. **Un solo `.py`** en `logica/` (`informes_rdata.py`). `python/main.py` falla si hay 0 o >1.
3. **Diferencia de esquema RDATA vs FORM:** `IDUF_SIG` está en `RDATA_ONLY_COLS` (`python/rdata/schema.py`) y solo existe en `DW_INF_CONSOL_RDATA`. `FECHA_CARGA` solo existe en `DW_INF_CONSOL_FORM`. `PK_OFICINA` existe en ambas (en FORM viene de `T_SEP_OFICINA.PK_OFICINA`; en RData la calcula `python/rdata/oficina.py` usando `oficina_alias.yaml`). El nombre fuente `IDADMINISTRADO` alimenta el coalesce de `ID_ADMINISTRADO` y no se publica como columna.
4. **Sin secretos** en git (`project-config.json` y `docs/credenciales/` están en `.gitignore`).
5. **Sin `${VAR}` literal** en logs Hop = variable mal definida.
6. `logica/` no abre conexiones. I/O vive en `python/io/`.
7. **No solapar corridas H2**: `mem:csep`:9092 es compartido con repos hermanos y `reset_and_create` ejecuta `DROP ALL OBJECTS`.
8. **Corrida en `logs/`**: `logs/init_YYYYMMDD.log` y `logs/wf_main_YYYYMMDD.log`. Skill `etl-run-logs`.
