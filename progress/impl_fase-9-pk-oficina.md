# impl — fase-9-pk-oficina

Rama `feature/mysql-dw-mirror`. CSEP sin cambio.

- Columna `PK_OFICINA` `VARCHAR2(20)` / `VARCHAR(20)` en `DW_INF_CONSOL_FORM` y `DW_INF_CONSOL_RDATA` (Oracle + MySQL DW). `ensure_dw_tables` hace ALTER si la tabla ya existía.
- FORM: `ofi.PK_OFICINA` en el SELECT de `vw_inf_consol_simil.sql` (join ya existente con `T_SEP_OFICINA`).
- RData: `python/main.py` → `python/rdata/oficina.py`. Catálogo vivo `T_SEP_OFICINA`; alias en `python/rdata/oficina_alias.yaml`.
- Evidencia local: `./init.sh` HARNESS OK. MySQL DW FORM 19 filas: `COR065` (16) y `COR040` (3). Resolver: nombre Electricidad y `CELE` → `COR062`; Cusco y `ODES-CUS` → `COR040`.
