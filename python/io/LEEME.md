# python/io/ — I/O post-staging

Flujo en `main.py`:
  `leer_h2.py` → `logica/` → `escribir_oracle.py` (+ Excel opcional)

- `leer_h2.py` — `LECTURAS` (`INF_RDATA` ← `STG_INF_CONSOL`)
- `escribir_oracle.py` — wipe+DDL+COMMENT+INSERT `APP.DW_INF_CONSOL_RDATA` (DW)
- `escribir_excel.py` — inspección local `output/resultado.xlsx`

No crear `STG_*` aquí. Eso es `python/create_stg.py` / `stage_rdata.py`.

No importar este paquete como `import io`: choca con la stdlib.
