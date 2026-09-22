# MySQL (gappsdb) — sistema informes HEC

Fuente paralela a RData. Carga canónica vía **Hop** (`pl_form_informes.hpl`), no Python.

| Archivo | Contenido |
|---|---|
| [`vw_inf_consol_simil.sql`](vw_inf_consol_simil.sql) | SELECT 83 cols (grano = hecho; `FUENTE` BD\|OD) — embebido en el pipeline |
| [`mapa_mysql_vs_rdata.md`](mapa_mysql_vs_rdata.md) | ER, OD/SEDE, mapeo y huecos |

## Pipeline

`metadata/rdbms/mysql.json` + `pipelines/pl_form_informes.hpl` → TRUNCATE `APP.DW_INF_CONSOL_FORM`.

Prerrequisito: CREATE tabla una vez ([`sql/dw/02_dw_inf_consol_form.sql`](../../sql/dw/02_dw_inf_consol_form.sql)).

Variables: `DB_MYSQL_*` en `environments/*.json` (vía `project-config.json`). Hard-fail si MySQL cae.

Credenciales: `docs/credenciales/` (no versionado).
