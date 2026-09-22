# sql/dw/ — DDL Oracle destino (una vez)

Ejecutar **una vez** en `oracle_dw` (usuario APP / REPOCSEP) antes de la primera corrida.

| Script | Tabla |
|---|---|
| [`01_dw_inf_consol_rdata.sql`](01_dw_inf_consol_rdata.sql) | `APP.DW_INF_CONSOL_RDATA` |
| [`02_dw_inf_consol_form.sql`](02_dw_inf_consol_form.sql) | `APP.DW_INF_CONSOL_FORM` |
| [`03_dw_inf_csep_informes_view.sql`](03_dw_inf_csep_informes_view.sql) | `DW_INF_CSEP_INFORMES_VIEW` (mejor CTAS desde la vista SISUD) |

**No** uses [`wf_create_stg.hwf`](../workflows/wf_create_stg.hwf) para esto: ese workflow solo crea `STG_*` en H2.

En cada corrida:

- RData → Python `escribir_oracle` → **TRUNCATE** + INSERT
- FORM / CSEP → Hop `pl_form_informes` / `pl_csep_informes` → **TRUNCATE** + INSERT
