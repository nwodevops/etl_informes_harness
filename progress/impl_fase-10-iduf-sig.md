# impl — fase-10-iduf-sig

Rama `feature/mysql-dw-mirror`. FORM no lleva la columna. CSEP no se altera (el espejo sigue el view de SISUD).

- `IDUF_SIG` `VARCHAR2(20)` / `VARCHAR(20)` solo en `DW_INF_CONSOL_RDATA` (Oracle + MySQL DW). `ensure_dw_tables` hace ALTER si la tabla ya existía.
- Copia directa desde el RData. El coalesce de `ID_UF` no cambia: `IDUF` → `ID_UF` → `IDUF_SIG`.
- En BD los códigos no coinciden (`SUR…` en `ID_UF`, `UF…` en `IDUF_SIG`). En OD no hay `ID_UF` en el archivo: `ID_UF` sigue saliendo de `IDUF_SIG` y la columna nueva repite ese código.
- Los valores en la tabla aparecen al volver a ejecutar `wf_create_stg`. `init.sh` no cubre RData.
- Evidencia: mapa CHID `ID_UF=SUR33881` / `IDUF_SIG=UF0013687`; CRES `ID_UF=SUR29872` y `UF0009796`+`UF0013841`. `ensure_dw_tables` agregó la columna en Oracle local y MySQL DW. FORM no la tiene.
