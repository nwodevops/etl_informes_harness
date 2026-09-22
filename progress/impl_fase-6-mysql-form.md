# impl_fase-6-mysql-form

## Qué

Cablear SQL HEC (`vw_inf_consol_simil.sql`) como segunda fuente: MySQL → `STG_INF_CONSOL_FORM` → `APP.DW_INF_CONSOL_FORM`, en paralelo a RData → `DW_INF_CONSOL_RDATA`.

## Cambios

- `inputs.yaml` type `mysql` + `python/introspect/mysql.py` + handler en `create_stg.py`
- `python/stage_mysql.py` + `pymysql` + `DB_MYSQL_*`
- `leer_h2` clave `INF_FORM`; logica `RESULTADO_FORM` passthrough; `escribir_oracle(table=...)`; `main` escribe ambas
- `init.sh` corre stage_mysql y grepea `DW_INF_CONSOL_FORM`

## Verificación

`./init.sh` → `HARNESS OK`
