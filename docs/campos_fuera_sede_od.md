# Campos que no entran a la tabla única

Comparación de todos los `BDInf_*.RData` (sede) y `ODInf_*.RData` (OD) en `input/input_rdata` contra las columnas de `DW_INF_CONSOL_RDATA`.

Un campo entra si se copia con el mismo nombre o si está en la tabla de equivalencias. El resto queda fuera. La unión sede/OD está en [`equivalencias_sede_od.md`](equivalencias_sede_od.md).

En agosto 2026, sede trae 83 columnas y OD 51. De esas, OD entra completa. Sede deja fuera las 5 de exportación y, además, el `SUR…` de `ID_UF` y el nombre largo de medidas administrativas.

## Sede — siguen en 2025/2026 y no entran

| Campo | Años en el backup | Motivo |
|---|---|---|
| `N°` | 2020–2026 | Correlativo del export |
| `USUARIO` | 2022–2026 | Usuario del sistema |
| `FECHA_REGISTRO` | 2022–2026 | Fecha de registro del export |
| `INF_EVAL` | 2019–2026 | Casi vacío en el corte vigente |
| `FECHA_INF_EVAL` | 2019–2026 | Igual que `INF_EVAL` |
| `ID_UF` (`SUR…`) | 2019–2026 | La columna fuente ya no se publica. `ID_UF` de la tabla sale de `ID_UF_UNIDAD_REV` e `IDUF_SIG` |
| `RECOMENDACION DE MEDIDAS ADMINISTRATIVAS` | 2026 | Ya no alimenta `RECOMENDACION_MEDIDAS_ADMIN` |

## OD — corte 2025/2026

Ningún campo del archivo vigente queda fuera. Los que se listan abajo no están en `ODInf` de 2025 ni de 2026.

## Sede — solo años anteriores

| Campo | Años | Motivo |
|---|---|---|
| `FEANUL_SIIA`, `FEAPROB_SIIA`, `FEREG_SIIA`, `FERPT` | 2019 | Fechas SIIA |
| `FGSUPUPD_1ERTIEMPO`, `FGSUPUPD_2DOTIEMPO`, `FGSUP_ORIENTATIVA` | 2019 | Marcas de supervisión del esquema viejo |
| `FGSUP_ORIENTATIVA_REV`, `ID_SUR_UNIDAD_REV`, `TXADMINISTRADO_ADM_REV`, `TXUNIDAD_REV` | 2019 | Copia de revisión. `IDADMINISTRADO_REV` e `ID_UF_UNIDAD_REV` sí entran al coalesce |
| `ID`, `IDACTIVIDAD`, `IDUNIDAD`, `RUC`, `TXNUMDOC_ADM` | 2019 | Identificadores del esquema viejo |
| `RD_ACTA_MEDIDA` | 2019 | Nombre viejo. El vigente entra como `RES_ACTA_MEDIDA`. `RECOM_MEDIDA` sí alimenta `RECOMENDACION_MEDIDAS_ADMIN` |
| `TXACTIVIDAD_UND`, `TXACTIVIDADES_VINCULADAS`, `TXCOFEMA`, `TXDENUNCIA`, `TXESTADO`, `TXESTADO_UF`, `TXETAPA_UF`, `TXFUENTE`, `TXMES`, `TXMOTIVOANULA`, `TXMUESTREO`, `TXNOMBRE_ANAL_LEGAL`, `TXNOMBRE_JEFE_ACTIVIDAD`, `TXNOMBRE_RESP_COMISION`, `TXNOMBRE_RESP_MONITOREO`, `TXNVL_CMPLJ`, `TXOBJETIVO`, `TXOTRAFUENTE`, `TXUBIGEO_UND` | 2019 | Bloque SIIA |
| `VALIDADO_META` | 2019 | Meta del esquema viejo |

## OD — solo años anteriores

| Campo | Años | Motivo |
|---|---|---|
| `N°` | 2019–2023 | Correlativo del export |
| `COMPETENCIA` | 2019–2023 | El vigente se llama `COMPET` y sí entra |
| `ESPECIALISTA` | 2019–2021 | No está en OD 2025/2026 |
| `JEFE` | 2019–2022 | No está en OD 2025/2026 |
| `FECHA_ELAB` | 2019–2021 | No está en OD 2025/2026 |
| `ULTIMO_DOC_ELAB` | 2019–2021 | No está en OD 2025/2026 |
| `CUENTA` | 2020–2021 | Cuenta de sistema |
| `MES_META_DERIV` | 2021 | Mes de derivación del esquema viejo |
| `VALIDADO_META` | 2020, 2022 | Meta del esquema viejo |
| `ADMIN_REV`, `IDAMIN_REV`, `UF_REV` | 2019 | Copia de revisión. `IDUF_REV` sí entra al coalesce de `ID_UF` |
| `FEANUL_SIIA`, `FEAPROB_SIIA`, `FEREG_SIIA`, `FERPT`, `FGSUPUPD_1ERTIEMPO`, `FGSUPUPD_2DOTIEMPO`, `FGSUP_ORIENTATIVA` | 2020 | Fechas y marcas SIIA |
| `IDACTIVIDAD`, `IDUNIDAD`, `TXNUMDOC_ADM` | 2020 | Identificadores del esquema viejo |
| `TXACTIVIDAD_UND`, `TXACTIVIDADES_VINCULADAS`, `TXCOFEMA`, `TXDENUNCIA`, `TXESTADO`, `TXESTADO_UF`, `TXETAPA_UF`, `TXFUENTE`, `TXMES`, `TXMOTIVOANULA`, `TXMUESTREO`, `TXNOMBRE_ANAL_LEGAL`, `TXNOMBRE_JEFE_ACTIVIDAD`, `TXNOMBRE_RESP_COMISION`, `TXNOMBRE_RESP_MONITOREO`, `TXNVL_CMPLJ`, `TXOBJETIVO`, `TXOTRAFUENTE`, `TXUBIGEO_UND` | 2020 | Bloque SIIA |
