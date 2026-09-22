# MySQL (gappsdb) — sistema informes HEC

Fuente paralela a RData. Extract en Python (`stage_mysql.py`), no Hop TableInput.

| Archivo | Contenido |
|---|---|
| [`vw_inf_consol_simil.sql`](vw_inf_consol_simil.sql) | SELECT 83 cols (grano = hecho; `FUENTE` BD\|OD) |
| [`mapa_mysql_vs_rdata.md`](mapa_mysql_vs_rdata.md) | ER, OD/SEDE, mapeo y huecos |

## Pipeline

`inputs.yaml` (`type: mysql`) → `create_stg.py` → `STG_INF_CONSOL_FORM` → `logica` (`RESULTADO_FORM` passthrough) → `APP.DW_INF_CONSOL_FORM`.

Variables: `DB_MYSQL_*` en `environments/*.json` (vía `project-config.json`).

Credenciales: `docs/credenciales/` (no versionado). No guardar passwords aquí.
