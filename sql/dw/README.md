# sql/dw/ — DDL destino (referencia)

La forma canónica de **crear** las tablas si no existen es:

```bash
# vía Hop
# Play workflows/wf_create_stg.hwf
# o:
.venv/bin/python python/stg/ensure_dw_tables.py
```

`ensure_dw_tables.py` hace CREATE solo si faltan (nunca DROP) en **oracle_dw** y **mysql_dw**.
CSEP toma columnas de `CSEP_INFORMES_VIEW` en `oracle_sisud`.

## Oracle (`oracle_dw`)

| Script | Tabla |
|---|---|
| [`01_dw_inf_consol_rdata.sql`](01_dw_inf_consol_rdata.sql) | `APP.DW_INF_CONSOL_RDATA` |
| [`02_dw_inf_consol_form.sql`](02_dw_inf_consol_form.sql) | `APP.DW_INF_CONSOL_FORM` (+ `FECHA_CARGA`) |
| [`03_dw_inf_csep_informes_view.sql`](03_dw_inf_csep_informes_view.sql) | `DW_INF_CSEP_INFORMES_VIEW` (preferir ensure desde vista) |

## MySQL mirror (`mysql_dw` / `DB_MYSQL_DW_*`)

Misma BD gappsdb, **conexión distinta** de la fuente HEC (`mysql` / `DB_MYSQL_*`).

| Script | Tabla |
|---|---|
| [`mysql/01_dw_inf_consol_rdata.sql`](mysql/01_dw_inf_consol_rdata.sql) | `DW_INF_CONSOL_RDATA` |
| [`mysql/02_dw_inf_consol_form.sql`](mysql/02_dw_inf_consol_form.sql) | `DW_INF_CONSOL_FORM` (+ `FECHA_CARGA`) |
| [`mysql/03_dw_inf_csep_informes_view.sql`](mysql/03_dw_inf_csep_informes_view.sql) | `DW_INF_CSEP_INFORMES_VIEW` (preferir ensure) |

**Corrida** (`wf_main`): Hop dual-write TRUNCATE+INSERT (Oracle + MySQL). RDATA: `main.py` → `escribir_oracle` + `escribir_mysql`.
