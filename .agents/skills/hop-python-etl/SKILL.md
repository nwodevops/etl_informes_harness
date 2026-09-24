---
name: hop-python-etl
description: >-
  Arquetipo Apache Hop primero + H2 STG_* + Python post-staging.
  Preferir Hop 1:1; wf_create_stg (diseño DDL STG) vs wf_main (corrida).
  inputs.yaml, create_stg.py, logica/ aislada, project-config.json.
  Usar al clonar el cascarón, añadir fuentes STG, cablear workflows o depurar Hop/H2/Python.
---

# Hop + H2 + Python ETL

## Arquitectura (no mezclar capas)

```
Fuentes (Excel / Sheets / Oracle / lo que declare inputs.yaml)
  → inputs.yaml          (declara STG_*)
  → Python create_stg    (DDL H2; no extrae filas)
  → Hop extract          (TableInput → TableOutput H2, truncate)
  → H2 mem:csep          (landing efímero, reset cada corrida)
  → Python logica/       (un .py; reglas)
  → Destino demo         (Excel output/resultado.xlsx)
```

| Capa | Hace | No hace |
|---|---|---|
| `inputs.yaml` | Manifiesto de fuentes | Extraer filas |
| `python/stg/create_stg.py` | Introspect + `CREATE TABLE STG_*` | Negocio |
| Hop | Extract → H2 | UNION multi-fuente ni KPIs |
| `logica/` | Negocio en memoria | Conexiones ni drivers |
| `python/io/` | Leer H2, escribir destino | Reglas de negocio |

**Contrato:** `python/CONTRATO.md`. **Staging:** [reference.md](reference.md).

## Preferir Apache Hop

**Regla de oro:** intentar siempre Hop (pipeline TableInput → TableOutput) antes de escribir extract/load en Python. Python queda para post-staging (`logica/`) u homologación que Hop no cubre bien (p.ej. RData + mapa de columnas).

## Workflows

| Workflow | Rol |
|---|---|
| **Diseño / RData** [`wf_create_stg.hwf`](../../../workflows/wf_create_stg.hwf) | DDL + carga backup RData → `DW_INF_CONSOL_RDATA` (bajo demanda; no diario). |
| **Corrida diaria** [`wf_main.hwf`](../../../workflows/wf_main.hwf) | Solo `pl_form` + `pl_csep`. |

## Cuándo Hop solo vs Python

- **Hop (preferido):** 1 fuente → destinos 1:1 o copy dual (ej. FORM HEC→Oracle+MySQL DW, CSEP vista→Oracle+MySQL DW).
- **Python:** homologación RData, calidad, joins, KPIs en `logica/`; RDATA también escribe `mysql_dw`.

Un solo `.py` en `logica/` (auto-descubierto por `python/main.py`). Entrada = claves de `LECTURAS` en `python/io/leer_h2.py`. Salida = DataFrame `RESULTADO`.

## Workflows (detalle arquetipo)

**Diseño / RData** (`wf_create_stg.hwf`): Reset H2 → create STG → ensure DW → stage RData → Python RDATA.

**Diario** (`wf_main.hwf`): `pl_form` → `pl_csep` → Success.

Smoke sin Hop GUI (requiere hop-run + tablas sql/dw/):

```bash
./h2/scripts/reset_and_create.sh
.venv/bin/python python/stg/create_stg.py
.venv/bin/python python/stage/stage_rdata.py
.venv/bin/python python/main.py
# hop-run pl_form + pl_csep (o ./init.sh)
```

Layout: `python/{core,stg,stage,rdata,introspect,io}/` + `pipelines/pl_form_informes.hpl` + `pl_csep_informes.hpl` — ver `python/LEEME.md` y `sql/dw/`.

## Extender una fuente (checklist)

1. Entrada en `inputs.yaml` ([inputs.example.yaml](inputs.example.yaml)).
2. Play `wf_create_stg` → crear `pipelines/pl_stage_*.hpl`.
3. Cablear en `wf_main.hwf` **después** de Python create STG.
4. Clave en `python/io/leer_h2.py` → `LECTURAS`.
5. Lógica en `logica/` (no conexiones). Borrar `demo.py` al pasar a lógica real.
6. Actualizar `python/CONTRATO.md` y `AGENTS.md`.

## Variables y conexiones

Fuente única: `project-config.json` → `config.variables`. Entorno: `./switch-env.sh local|remote`.

- `DB_H2_*` — staging TCP `localhost:9092/mem:csep`
- `DB_ORA_DW_*` / `DB_ORA_SISUD_*` — Oracle destino / fuente CSEP
- `DB_MYSQL_*` — fuente HEC gappsdb
- `DB_MYSQL_DW_*` — destino mirror DW (misma BD tipicamente; **conexión distinta**)

`${VAR}` literal en log = variable no definida o proyecto Hop equivocado.

**Secretos:** no commitear passwords reales en `project-config.json` / `environments/`.

## Gotchas

| Síntoma | Causa |
|---|---|
| Workflow colgado en Reset H2 | `start_h2.sh` sin `nohup` + redirección al log |
| H2 vacío tras reinicio | in-memory se pierde al parar el server |
| `import io` falla | colisión con stdlib; cargar módulos por ruta en `main.py` |
| `#N/A` tumba pipeline | Sheets/Excel → VARCHAR en STG |
| Hop sobrescribe variables | `hop-conf.sh --project-create` sin `--project-keep-config-file` |
