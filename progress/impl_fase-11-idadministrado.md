# impl — fase-11-idadministrado

Rama `feature/mysql-dw-mirror`. FORM no lleva la columna. CSEP no se altera.

- `IDADMINISTRADO` `VARCHAR2(20)` / `VARCHAR(20)` solo en `DW_INF_CONSOL_RDATA` (Oracle + MySQL DW). `ensure_dw_tables` hace ALTER si la tabla ya existía.
- Copia directa desde el RData. El coalesce de `ID_ADMINISTRADO` no cambia: `IDADMIN` → `IDAMIN` → `ID_ADMIN` → `IDADMINISTRADO`.
- En `00034-2019-OEFA/DSAP-CIND`, `IDAMIN` es `ADM06821` en las 4 filas y `IDADMINISTRADO` alterna `ADM06821` / `ADM07102`. `IDADMINISTRADO_REV` no se copia.
- Los valores en la tabla aparecen al volver a ejecutar `wf_create_stg`. `init.sh` no cubre RData.
- Evidencia: mapa CIND `ID_ADMINISTRADO=ADM06821` en 4 filas; `IDADMINISTRADO` = `ADM06821` (2) y `ADM07102` (2). `ensure_dw_tables` agregó la columna en Oracle local y MySQL DW. FORM no la tiene.
