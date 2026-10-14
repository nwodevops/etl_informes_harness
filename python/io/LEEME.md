# python/io/ — I/O post-staging (RData)

Flujo en `main.py`:
  `leer_h2.py` → `logica/` → `escribir_oracle.py` + `escribir_mysql.py` (+ Excel opcional)

- `leer_h2.py` — `LECTURAS` (`INF_RDATA` ← `STG_INF_CONSOL`)
- `escribir_oracle.py` — TRUNCATE+INSERT `DW_INF_CONSOL_RDATA` en **oracle_dw**
- `escribir_mysql.py` — TRUNCATE+INSERT `DW_INF_CONSOL_RDATA` en **mysql_dw** (`DB_MYSQL_DW_*`)
- `escribir_excel.py` — inspección local `output/resultado.xlsx`

FORM/CSEP no usan este paquete (Hop dual-write).

No crear `STG_*` aquí. Eso es `python/stg/create_stg.py` / `python/stage/stage_rdata.py`.

No importar este paquete como `import io`: choca con la stdlib.
