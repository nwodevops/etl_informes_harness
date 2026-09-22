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

## Flujo informes (RData + FORM + CSEP)

`wf_main` / `./init.sh` dejan **3 tablas** en oracle_dw:

1. `DW_INF_CONSOL_RDATA` (RData)
2. `DW_INF_CONSOL_FORM` (MySQL HEC; **siempre** se crea, aunque MySQL caiga o vaya vacío)
3. `DW_INF_CSEP_INFORMES_VIEW` (vista SISUD `CSEP_INFORMES_VIEW` vía DDL + `pl_csep_informes`; stub vacío si SISUD cae)

`inputs.yaml` → `create_stg.py` → `stage_rdata.py` / `stage_mysql.py --soft` → `main.py` → `ddl_csep_informes.py` + pipeline Hop.  
Mapa RData: [`docs/rdata_column_map.md`](docs/rdata_column_map.md). SQL HEC: [`input/input_mysql/`](input/input_mysql/).

## Nuevo proyecto

Este repo es un cascarón. Fuentes → `inputs.yaml`. Lecturas → `python/io/leer_h2.py`. Transformación → `logica/<tu>.py`. Destino DW → `escribir_oracle.py`.
