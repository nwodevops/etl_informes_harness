# impl — fase-8-mysql-dw-mirror

Rama `feature/mysql-dw-mirror`.

- Conexión Hop/Python `mysql_dw` (`DB_MYSQL_DW_*`); fuente HEC sigue en `mysql`
- `ensure_dw_tables` CREATE en Oracle + MySQL (TEXT/LONGTEXT + ROW_FORMAT=DYNAMIC)
- `pl_form` / `pl_csep`: copy → `oracle_dw` + `mysql_dw` (TRUNCATE)
- `main.py` → `escribir_oracle` + `escribir_mysql` (RDATA bajo demanda)
- Ref: `sql/dw/mysql/`
