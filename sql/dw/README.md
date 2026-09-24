# sql/dw/ — DDL Oracle destino (referencia)

La forma canónica de **crear** las tablas si no existen es:

```bash
# vía Hop
# Play workflows/wf_create_stg.hwf
# o:
.venv/bin/python python/stg/ensure_dw_tables.py
```

`ensure_dw_tables.py` hace CREATE solo si faltan (nunca DROP). CSEP toma columnas de `CSEP_INFORMES_VIEW` en `oracle_sisud`.

Estos `.sql` son referencia / fallback manual:

| Script | Tabla |
|---|---|
| [`01_dw_inf_consol_rdata.sql`](01_dw_inf_consol_rdata.sql) | `APP.DW_INF_CONSOL_RDATA` |
| [`02_dw_inf_consol_form.sql`](02_dw_inf_consol_form.sql) | `APP.DW_INF_CONSOL_FORM` (+ `FECHA_CARGA`) |
| [`03_dw_inf_csep_informes_view.sql`](03_dw_inf_csep_informes_view.sql) | `DW_INF_CSEP_INFORMES_VIEW` (preferir ensure desde vista) |

**Corrida** (`wf_main`): solo TRUNCATE + INSERT.
