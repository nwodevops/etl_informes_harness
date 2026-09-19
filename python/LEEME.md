# python/ — STG, extract y I/O (sin reglas de negocio)

Hop / harness llaman entry points aquí. **`logica/`** es post-staging.

| Capa | Entry / módulo | Hace | No hace |
|---|---|---|---|
| **STG / DDL** | `create_stg.py` + `introspect/` | `CREATE TABLE STG_*` | Filas, negocio |
| **Extract RData** | `stage_rdata.py` | R → `rdata.map` → H2 | Oracle, QA |
| **Contrato RData** | `rdata/schema.py` | Columnas, tipos, DDL/COMMENT | I/O |
| **Adapter mapa** | `rdata/map.py` | EQUIV / `map_to_canonical` | Conexiones |
| **Post-staging** | `main.py` + `io/` | Lee H2 → llama `logica/` → Oracle/Excel | Introspect |

```
inputs.yaml → create_stg.py → introspect/ → H2 vacío
stage_rdata.py (o Hop) → STG_* con filas
main.py → io/leer_h2 → logica/*.py → io/escribir_oracle
```

`config.py` y `h2_conn.py` son compartidos.

Compat: `rdata_schema.py` reexporta `rdata.*` (preferir imports nuevos).

Contrato: [`CONTRATO.md`](CONTRATO.md).
