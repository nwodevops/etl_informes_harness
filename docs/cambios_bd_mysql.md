# Cambios en el MySQL de origen (`gappsdb`)

Consulta hecha el 2026-10-14 sobre la conexión `mysql` (origen HEC), base `gappsdb`. No es el MySQL DW (`mysql_dw`).

El contraste es el snapshot del 2026-09-21 en [`input/input_mysql/mapa_mysql_vs_rdata.md`](../input/input_mysql/mapa_mysql_vs_rdata.md).

## Informe recreado

`T_MVC_INFORME_HEC` se creó de nuevo el **2026-10-13 18:07**. Quedó vacía (0 filas). El 21 de septiembre tenía 9 informes.

Columnas actuales (31):

`NU_IDINFORME`, `TX_NUMINFORME`, `FE_FECHAINICIO`, `FE_FECHAAPROBACION`, `TX_NUMEXPEDIENTE`, `TX_CUC`, `TX_ACCIONESVINCULADAS`, `TX_COORDINACION`, `TX_SECTOR_OD`, `TX_IDTIPOSUPERVISION`, `TX_TIPOACCION`, `FG_SUPORIENTATIVA`, `FG_INFORMEEVALUACION`, `TX_IDCOORDINADOR`, `TX_IDDIRECTOR`, `TX_TOTAL_HECHOS`, `NU_OBLIGACIONESDECLARADAS`, `NU_OBLIGCUMPLIDAS`, `NU_PRESUNTINCUMPLIMIENTOS`, `TX_RECOMENDACIONINAF`, `TX_RECOMENDACIONMANUAL`, `FE_FECHADOCCIERRE`, `FE_FECHADERIVACION`, `FG_ESTADO`, `TX_MES`, `NU_ANIO`, `FE_FECHA_CREACION`, `TX_USUARIO_CREACION`, `FE_FECHA_MODIFICACION`, `TX_USUARIO_MODIFICACION`, `NU_VERSION`.

## Antes y después

Tres columnas salieron de `T_MVC_INFORME_HEC`. No hubo rename dentro de esa tabla. El SELECT de FORM las leía sobre el alias `i`.

| Campo | Antes (2026-09-21, en el informe `i`) | Después (2026-10-14) |
|---|---|---|
| `NU_IDMEDIDA` | Columna del informe. FK hacia `T_MVC_INFORMACIONMEDIDAS_MED`. | Eliminada. Sin columna equivalente. El cruce pasa a `i.TX_CUC` = `med.TX_CUC`. |
| `TX_DOCMEDIDA` | Columna del informe. El SQL hacía `COALESCE(i.TX_DOCMEDIDA, med.TX_DOCMA)`. | Eliminada. El dato queda solo en `T_MVC_INFORMACIONMEDIDAS_MED.TX_DOCMA`. |
| `FE_FECHAMEDIDA` | Columna del informe. El SQL hacía `COALESCE(i.FE_FECHAMEDIDA, med.FE_DOCMA)`. | Eliminada. El dato queda solo en `T_MVC_INFORMACIONMEDIDAS_MED.FE_DOCMA`. |

`TX_DOCMA` y `FE_DOCMA` no son columnas nuevas: ya estaban en la tabla de medidas. `TX_CUC` ya estaba en el informe; antes no unía y ahora es la llave del cruce.

`T_MVC_INFORMACIONMEDIDAS_MED` no se recreó (sigue desde el 2026-08-05). Tiene 50 filas. Su llave es `NU_IDMEDIDAS`, más `TX_CUC`, `TX_DOCMA` y `FE_DOCMA`. No tiene `NU_IDINFORME`.

## Antes y después de campos

Solo columnas que salieron de `T_MVC_INFORME_HEC`. No hubo rename dentro de esa tabla.

| Campo | Antes (2026-09-21) | Después (2026-10-14) |
|---|---|---|
| `NU_IDMEDIDA` | Columna de `T_MVC_INFORME_HEC` | Eliminada. Sin columna equivalente en esa tabla. |
| `TX_DOCMEDIDA` | Columna de `T_MVC_INFORME_HEC` | Eliminada de esa tabla. En `T_MVC_INFORMACIONMEDIDAS_MED` el campo es `TX_DOCMA`. |
| `FE_FECHAMEDIDA` | Columna de `T_MVC_INFORME_HEC` | Eliminada de esa tabla. En `T_MVC_INFORMACIONMEDIDAS_MED` el campo es `FE_DOCMA`. |

## Tablas HEC vacías

Estas tablas no se recrearon en octubre (siguen con fecha de agosto), pero hoy tienen 0 filas. El 21 de septiembre sí tenían datos.

| Tabla | Filas el 2026-09-21 | Filas el 2026-10-14 |
|---|---|---|
| `T_MVC_INFORME_HEC` | 9 | 0 |
| `T_MVC_HECHOS_HEC` | 17 | 0 |
| `T_MVC_ADMUF_HEC` | 9 | 0 |
| `T_MVC_DOCUMENTOS_HEC` | 17 | 0 |
| `T_MVC_OBLIGACIONES_HEC` | 14 | 0 |
| `T_MVC_COMPONENTES_HEC` | 27 | 0 |
| `T_MVC_MECANISMOS_HEC` | 5 | 0 |
| `T_MVC_MECANISMOS_OBLIGACION_HEC` | 6 | 0 |

Las tablas de medidas (`T_MVC_*_MED`) siguen con filas. Por ejemplo `T_MVC_MEDIDAS_MED` tiene 19 y `T_MVC_INFORMACIONMEDIDAS_MED` tiene 50.

## Auditoría

`T_AUD_INFORME_HEC` guarda cada cambio del informe en `JS_DATOS_NUEVOS` (JSON), con `TX_OPERACION`, `TX_LOGIN` y `FE_FECHA_AUDITORIA`.

- Creada el 2026-10-10 10:51.
- Último cambio el 2026-10-13 18:27, unos 20 minutos después de recrear el informe.
- Hoy tiene **0 filas**. El JSON anterior ya no está, así que no se puede ver el esquema viejo desde ahí.
- No hay trigger sobre `T_MVC_INFORME_HEC`. Lo que se cargue ahora no entra solo a esa auditoría.

`DW_M_AUD_F4_FORM` y el resto de `DW_M_AUD_*` son bitácoras de multas. No registran el esquema HEC.

## `DW_INF_CSEP_INFORMES_VIEW` en este servidor

El 2026-10-14 por la mañana la tabla no existía y el `CREATE VIEW vw_inf_consol_simil` fallaba por eso. A las **08:49** del mismo día apareció como tabla base, con las columnas de CSEP (`TXINFORME`, `TXCUC`, `TX_DOCUMENTO_PREVIO`, `FE_DERIV_DOC_DERIVACION`, etc.) y **0 filas**.

Esa tabla, en el ETL, la llena `pl_csep_informes` en el destino (`oracle_dw` y `mysql_dw`), no en este MySQL de origen.
