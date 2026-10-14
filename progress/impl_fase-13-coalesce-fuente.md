# impl — fase-13-coalesce-fuente

Rama `feature/mysql-dw-mirror`. No hay columna nueva. FORM y CSEP no cambian. `init.sh` no cubre RData.

- `ID_ADMINISTRADO` sede: `IDADMINISTRADO_REV`, `IDADMIN`, `IDAMIN`, `ID_ADMIN`, `IDADMINISTRADO`. OD: solo `IDADMIN`.
- `ID_UF` sede: `ID_UF_UNIDAD_REV`, `IDUF_SIG`. OD: `IDUF_REV`, `IDUF_SIG`. El `SUR…` de la columna fuente `ID_UF` no se publica. `IDUF_SIG` sigue copiándose en su columna.
- `RECOMENDACION_MEDIDAS_ADMIN` (sede y OD): `RECOM_MA`, `RECOMENDACIÓN_MEDIDAS`, `RECOM_MEDIDAS`, `RECOM_MEDIDA`. El nombre largo `RECOMENDACION DE MEDIDAS ADMINISTRATIVAS` ya no entra. `RECOM_MA` sigue también en `RECOM_ACCION`.
- Los valores ya cargados cambian al volver a ejecutar `wf_create_stg`.

Evidencia (`map_to_canonical`, sin escribir el DW):

- CHID agosto 2026, 6 filas: `ID_UF=UF0013687`, `IDUF_SIG=UF0013687`. `RECOMENDACION_MEDIDAS_ADMIN` vacío.
- OD agosto 2026: 3631 filas con `IDUF_SIG` lleno y `ID_UF` igual a ese código.
- Sede diciembre 2019: `IDADMINISTRADO_REV` gana en 10048/10048; `ID_UF_UNIDAD_REV` gana en 10030/10030.
- OD diciembre 2019: `IDUF_REV` gana en 6626/6626.
- `00034-2019-OEFA/DSAP-CIND`: `ID_ADMINISTRADO` queda `ADM16072` (el REV). La columna `IDADMINISTRADO` sigue en `ADM06821` / `ADM07102`.
