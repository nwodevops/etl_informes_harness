# AGENTS.md — mapa para agentes (cascarón Hop + H2 + Python)

ETL **Apache Hop + H2 in-memory + Python**. Arquitectura: [`docs/arquitectura.md`](docs/arquitectura.md).

**Verificación:** [`./init.sh`](init.sh) debe terminar en **`HARNESS OK`**. Criterios: [`CHECKPOINTS.md`](CHECKPOINTS.md).

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

## Reglas críticas

1. **Un solo `.py`** en `logica/` (hoy: `informes_rdata.py`) — solo reglas post-STG.
2. **Sin secretos** en git (`project-config.json` es generado).
3. **Sin `${VAR}` literal** en logs Hop = variable mal definida.
4. `logica/` no abre conexiones. I/O en `python/io/`. Homologación RData en `python/rdata/` + `stage_rdata.py`.

## Flujo informes (RData + FORM)

`inputs.yaml` → `create_stg.py` → `stage_rdata.py` / `stage_mysql.py` → `main.py` / `logica/` → `APP.DW_INF_CONSOL_RDATA` + `APP.DW_INF_CONSOL_FORM`.  
Mapa: [`docs/rdata_column_map.md`](docs/rdata_column_map.md). SQL HEC: [`input/input_mysql/`](input/input_mysql/).

## Flujo CSEP informes (Hop, paralelo)

`CSEP_INFORMES_VIEW` (oracle_sisud) → [`python/ddl_csep_informes.py`](python/ddl_csep_informes.py) + [`pipelines/pl_csep_informes.hpl`](pipelines/pl_csep_informes.hpl) → `CSEP_INFORMES` (oracle_dw).  
Workflow: [`workflows/wf_csep_informes.hwf`](workflows/wf_csep_informes.hwf). **No** entra en `./init.sh` / `wf_main`.

```bash
./switch-env.sh local   # o remote (completar DB_ORA_SISUD_* + DB_ORA_DW_* desde docs/credenciales/)
# Hop GUI → wf_csep_informes   |   hop-run -f workflows/wf_csep_informes.hwf ...
```

## Nuevo proyecto

Este repo es un cascarón. Fuentes → `inputs.yaml`. Lecturas → `python/io/leer_h2.py`. Transformación → `logica/<tu>.py`. Destino DW → `escribir_oracle.py`.
