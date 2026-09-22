# impl_fase-6-mysql-form (actualizado 2026-09-22)

## Qué

MySQL HEC → `APP.DW_INF_CONSOL_FORM` vía **Hop** (`pl_form_informes.hpl`), truncate, hard-fail.

## Piezas

- `metadata/rdbms/mysql.json` (`DB_MYSQL_*`)
- `pipelines/pl_form_informes.hpl` (SQL embebido desde `input/input_mysql/vw_inf_consol_simil.sql`)
- DDL una vez: `sql/dw/02_dw_inf_consol_form.sql`
- Cableado en `wf_main` / `init.sh` (hop-run)

## Nota

Ya no hay `stage_mysql.py` ni STG_INF_CONSOL_FORM en H2.
