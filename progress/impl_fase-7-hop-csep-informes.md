# impl_fase-7-hop-csep-informes (actualizado 2026-09-22)

## Qué

Vista `CSEP_INFORMES_VIEW` (oracle_sisud) → `DW_INF_CSEP_INFORMES_VIEW` (oracle_dw) vía Hop truncate, hard-fail.

## Piezas

- `pipelines/pl_csep_informes.hpl`
- `workflows/wf_csep_informes*.hwf` (solo pipeline)
- Cableado en `wf_main` / `init.sh` (hop-run)
- DDL una vez: `sql/dw/03_dw_inf_csep_informes_view.sql` (preferir CTAS desde la vista)

## Nota

Eliminado `python/csep/ddl_csep_informes.py` (DROP+CREATE + soft).
