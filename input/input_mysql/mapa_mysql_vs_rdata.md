# MySQL gappsdb → símil `DW_INF_CONSOL_RDATA`

Query: [`vw_inf_consol_simil.sql`](vw_inf_consol_simil.sql)  
Contrato: [`docs/rdata_column_map.md`](../../docs/rdata_column_map.md) (83 cols).

## Snapshot data (2026-09-21)

| Tabla | Filas |
|---|---|
| `T_MVC_INFORME_HEC` | 9 |
| `T_MVC_HECHOS_HEC` | 17 |
| `T_MVC_ADMUF_HEC` | 9 (1:1 con informe) |
| `T_MVC_DOCUMENTOS_HEC` | 17 |
| `T_MVC_OBLIGACIONES_HEC` | 14 |
| `T_MVC_COMPONENTES_HEC` | 27 |
| `T_MVC_MECANISMOS_HEC` | 5 |
| `T_MVC_MECANISMOS_OBLIGACION_HEC` | 6 |
| Resultado query | **17 × 83** (grano = hecho) |

Desglose `FUENTE`: **BD 15** / **OD 2** (1 informe OD × 2 hechos).  
`FILTRO_INF_UNIQ=1` en **9** filas (= nº informes).

## OD vs SEDE (BD)

No hay flag `FG_OD`. Se infiere con `T_SEP_OFICINA` (extra al listado HEC):

| Señal | SEDE → `FUENTE='BD'` | OD → `FUENTE='OD'` |
|---|---|---|
| `TX_COORDINACION` → oficina | padre ≠ `SUO00006` (ej. `COR065` Agricultura) | padre `SUO00006` o nombre “Oficina Desconcentrada/Enlace” (ej. `COR040` Cusco) |
| `TX_SECTOR_OD` | vacío | poblado (ej. Cultura) → también `TIPO_OD` |
| Nº informe | `.../DSAP-...` | `.../ODES-...` |
| Columna `OD` | NULL | descripción oficina |

## Docs (`NU_IDTIPODOC`)

| Tipo | Uso en query | Ejemplo |
|---|---|---|
| 1 (+ detalle 1/2/3 = Carta/Memo/Oficio) | `DOC_CIERRE` / `NRO_DOC_CIERRE` | MEMORANDO / CARTA |
| 2 | `DOC_INICIO_ELA` + `PROVEIDO` | nº corto `125-2026-OEFA/DSAP` |
| 3 | `TX_NUMERO_DOCUMENTO_PREVIO` | nº corto / DEAM |

## Modelo ER

```text
T_MVC_INFORME_HEC 1──* T_MVC_HECHOS_HEC
       │                └──* T_MVC_COMPONENTES_HEC → T_MAP_COMPONENTE_HEC
       │                └──* T_MVC_MECANISMOS_HEC
       ├── 1 T_MVC_ADMUF_HEC → T_MAP_ADMINISTRADO / T_MAP_UNIDAD_FISCALIZABLE
       ├──* T_MVC_DOCUMENTOS_HEC
       ├──* T_MVC_OBLIGACIONES_HEC → T_MVC_MECANISMOS_OBLIGACION_HEC
       ├──? T_MVC_INFORMACIONMEDIDAS_MED (FK NU_IDMEDIDA; aún 0 links)
       └── TX_COORDINACION → T_SEP_OFICINA  (FUENTE BD|OD)
```

## Mejoras vs v1 del query

1. `FUENTE` real `BD`/`OD` (antes hardcode `BD`)
2. `OD` / `TIPO_OD` / `TXCOORDINACION` con nombre de oficina
3. Documentos por tipo (cierre / inicio / previo)
4. `FILTRO_INF_UNIQ` solo en el 1.er hecho del informe
5. Join `T_MAP_MES` para normalizar mes
6. `TIPO_INF` si `FG_INFORMEEVALUACION`

## Siguen NULL / débiles

`CUC_INAPS`/`FEFIN`/medidas (ningún informe con `NU_IDMEDIDA`), `COORDINADOR`/`DIRECTOR`, `DIREC`, `RPS`/`ACTA_TRANSF`, `CATEG`/`COMPET`, `ANALISTA_LEGAL`/`RESPONSABLE_COMISION`, `SUBS_LEVE`/`SUBS_TRAS` (mecanismos existen pero no mapean 1:1 a esos conteos RData), `TIPOSUP` cuando código=`0`.
