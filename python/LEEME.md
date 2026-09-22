# python/ — STG, extract RData y I/O (sin reglas de negocio)

Hop / harness llaman entry points aquí. **`logica/`** es post-staging RData.
FORM y CSEP son pipelines Hop (no Python).

## Carpetas

| Carpeta | Contenido |
|---|---|
| `core/` | `config.py`, `h2_conn.py`, bootstrap de `sys.path` |
| `stg/` | `create_stg.py` — DDL `STG_INF_CONSOL` desde `inputs.yaml` |
| `stage/` | `stage_rdata.py` — RData → H2 |
| `rdata/` | Contrato columnas + mapa EQUIV |
| `introspect/` | Deduce columnas (oracle, mysql, rdata, …) |
| `io/` | Leer H2 / TRUNCATE+INSERT Oracle·Excel |
| `main.py` | Entry post-staging → `logica/` → `DW_INF_CONSOL_RDATA` |

## Capas

| Capa | Entry / módulo | Hace | No hace |
|---|---|---|---|
| **STG / DDL** | `stg/create_stg.py` + `introspect/` | `CREATE TABLE STG_*` | Filas, negocio |
| **Extract RData** | `stage/stage_rdata.py` | R → `rdata.map` → H2 | Oracle, QA |
| **Contrato RData** | `rdata/schema.py` | Columnas, tipos, DDL/COMMENT | I/O runtime |
| **Adapter mapa** | `rdata/map.py` | EQUIV / `map_to_canonical` | Conexiones |
| **Post-staging** | `main.py` + `io/` | Lee H2 → `logica/` → Oracle/Excel | FORM/CSEP |
| **FORM / CSEP** | `pipelines/pl_*` | Truncate load Hop | Python |

```
inputs.yaml → stg/create_stg.py → introspect/ → H2 vacío
stage/stage_rdata.py → STG_INF_CONSOL con filas
main.py → io/leer_h2 → logica/*.py → io/escribir_oracle (RDATA)
hop-run pl_form_informes + pl_csep_informes → FORM + CSEP
```

DDL Oracle: [`sql/dw/`](../sql/dw/). Contrato: [`CONTRATO.md`](CONTRATO.md).
