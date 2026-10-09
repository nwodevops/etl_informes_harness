# Equivalencias SEDE y OD (backup RData)

Los backups `BDInf_*.RData` (sede) y `ODInf_*.RData` (oficinas desconcentradas) se apilan en una sola tabla: `DW_INF_CONSOL_RDATA`.

Plantilla vigente (agosto 2026):

| Origen | Archivo | Objeto R | Columnas |
|---|---|---|---|
| SEDE | `BDInf_Agosto_2026.RData` | `INF_CONSOL_BOLETIN` | 83 |
| OD | `ODInf_Agosto_2026.RData` | `INF_OD_CONSOL_BOLETIN` | 51 |

`FUENTE` distingue la fila: `BD` (sede) u `OD`. Si un campo no existe en ese archivo, la celda queda vacía. Los espacios del nombre fuente pasan a guion bajo (`ANALISTA LEGAL` → `ANALISTA_LEGAL`).

Detalle técnico: [`rdata_column_map.md`](rdata_column_map.md).  
Campos que no entran: [`campos_fuera_sede_od.md`](campos_fuera_sede_od.md).

## Mismo nombre en sede y en OD

La columna de la tabla única se llama igual.

`INFORME`, `FECHA_INFORME`, `EXPEDIENTE`, `CUC_INAPS`, `HECHO_VERIF`, `TIPIFICA_HECHO`, `CLASIF_HECHO`, `RESULT_HECHO`, `MOTIVO_ARCHIV_CONOC`, `RECOM_INFORME`, `DOC_CIERRE`, `NRO_DOC_CIERRE`, `FECHA_DOC_CIERRE`, `FECHA_DERIV`, `FEINICIO`, `FEFIN`, `TIPOSUP_INAPS`, `SUPERV_ORIENTATIVA`, `MES_META`, `TIPO_INF`, `TXCOORDINACION`, `OBLIG_CUMPL`, `OBL_INCUMPLIDA`, `SUBSANA`, `SUBS_LEVE`, `SUBS_TRAS`, `SUBSANADO`, `CUMPLIM_ADD`, `FILTRO_INF_UNIQ`, `TIPOACCION_INAPS`, `FECHA_REAL`, `YEAR_APROB`, `FEINI_ELAB_INF`, `TX_DOCUMENTO_PREVIO`, `TX_NUMERO_DOCUMENTO_PREVIO`, `FE_DOCUMENTO_PREVIO`, `FE_REGISTRO_DOCUMENTO_PREVIO`, `TX_OTRO_DOCUMENTO_PREVIO`, `FE_DERIV_DOC_DERIVACION`.

## Nombres distintos, un solo campo

Gana el primer valor que ya viene lleno, en el orden de la fila.

| Tabla única | SEDE | OD |
|---|---|---|
| `ID_ADMINISTRADO` | `IDADMIN`, `IDAMIN`, `ID_ADMIN`, `IDADMINISTRADO` | `IDADMIN` |
| `ADMIN` | `ADMIN`, `ADMINISTRADO_INAPS` | `ADMIN`, `ADMINISTRADO_INAPS` |
| `ID_UF` | `ID_UF`, y si viene vacío `IDUF_SIG` | `IDUF_SIG` |
| `UF` | `UF`, `UF_INAPS` | `UF`, `UF_INAPS` |
| `RECOM_ACCION` | `RECOM_INAPS` | `RECOM_MA` |
| `SECTOR_O_SUBSECTOR` | `SECTOR` | `SUBSECTOR` |
| `TXCOORDINACION` | `TXCOORDINACION`, `COORDINACION` | `TXCOORDINACION` |
| `TIPOACCION_INAPS` | `TIPOACCION_INAPS` | `TIPOACCION_INAPS`, `TXACCION` |
| `TIPOSUP_INAPS` | `TIPOSUP_INAPS` | `TIPOSUP_INAPS`, `TXTIPSUP` |
| `EXPEDIENTE` | `EXPEDIENTE` | `EXPEDIENTE`, `TXNUMEXP` |
| `TIPO_OD` | — | `TIPO` |
| `RECOMENDACION_MEDIDAS_ADMIN` | `RECOMENDACION DE MEDIDAS ADMINISTRATIVAS` | — |

Dos códigos se guardan además tal como vienen, porque en sede no son el mismo valor que la columna unificada:

| Tabla única | SEDE | OD |
|---|---|---|
| `IDUF_SIG` | `IDUF_SIG` (`UF…`). `ID_UF` guarda el `SUR…` | `IDUF_SIG`. En OD, `ID_UF` repite este mismo código |
| `IDADMINISTRADO` | `IDADMINISTRADO`. Puede diferir de `IDAMIN` / `ID_ADMIN` | `IDADMINISTRADO` si el archivo lo trae |

`PK_OFICINA` no está en el RData. Se arma después, cruzando el texto de `TXCOORDINACION` con `T_SEP_OFICINA`.

## Solo sede

En filas OD quedan vacías.

`DIREC`, `COORDINADOR`, `DIRECTOR`, `DOC_INICIO_ELA`, `FECHA_INICIO_ELA`, `PROVEIDO`, `FECHA_PROV`, `TIPO_INFRACCION`, `DAÑO_RIESGO_ASOCIADO`, `HUMANOS`, `AIRE`, `FLORA`, `FAUNA`, `AGUA`, `SUELO`, `TIPO_SUBSANACION`, `PRESUNTOS_INCUMPL`, `TOTAL_HECHOS`, `ACTA_TRANSF`, `FECHA_ACTA_TRASNF`, `RPS`, `FECHA_RPS`, `RES_ACTA_MEDIDA`, `FECHA_MEDIDA`, `ESTADO`, `ANALISTA_LEGAL`, `RESPONSABLE_COMISION`.

## Solo OD

En filas sede quedan vacías.

`OD`, `CATEG`, `COMPET`, `TIPO_OD`.

## No entran a la tabla única

| Columna fuente | Motivo |
|---|---|
| `N°`, `USUARIO`, `FECHA_REGISTRO` | Dato de exportación, no del informe |
| `INF_EVAL`, `FECHA_INF_EVAL` | Casi vacías en el corte vigente |
| `*_REV` (`ADMIN_REV`, `IDUF_REV`, …) | Copia de revisión |
| Bloque SIIA 2019–2020 (`TXESTADO`, `CUENTA`, `ESPECIALISTA`, …) | No está en la plantilla 2025/2026 |
