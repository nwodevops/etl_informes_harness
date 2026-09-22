# Mapa de columnas RData → DW_INF_CONSOL_RDATA

Destino lógico: `APP.DW_INF_CONSOL_RDATA` (DW / `oracle_dw`).  
FQN Oracle: `APP.DW_INF_CONSOL_RDATA` (conexión `oracle_dw` / user `app`).

## Estructura gradual (prioridad 2025/2026)

Los cortes **2025 y 2026** son los más consumidos. La **forma** de la tabla se ancla al esquema vigente (`BDInf`/`ODInf` Dic-2025 ≡ Ago-2026: 83 / 51 columnas fuente).

| Capa | Qué hace |
|---|---|
| **Vigente** | Define CORE + EXTRAS BD/OD; máxima completitud en filas 2025–2026 |
| **Histórica** | Mismos nombres; 2019–2024 aportan valor si existe / vía EQUIV / NULL si no |
| **Sistema** | Fuera del DW (`N°`, `USUARIO`, …) |

Implementación: [`python/rdata/schema.py`](../python/rdata/schema.py) + [`python/rdata/map.py`](../python/rdata/map.py) — **83 columnas** canónicas (unión vigente BD∪OD + EQUIV; sin meta de export).  
Comentarios Oracle (`COMMENT ON TABLE/COLUMN`) se aplican en cada full refresh vía `escribir_oracle.py`.  
QA `FG_SIN_INFORME` se calcula en [`logica/informes_rdata.py`](../logica/informes_rdata.py).

---

## Proveniencia (ETL)

| Columna | Origen |
|---|---|
| `FUENTE` | Prefijo archivo `BD` / `OD` |
| `ANIO` | Año en el nombre (`2026`) |
| `MES_CORTE` | Mes en el nombre (`AGOSTO`, `DICIEMBRE`, …) |
| `ARCHIVO` | Basename `.RData` |
| `OBJETO_R` | Objeto R |
| `FG_SIN_INFORME` | QA suave (1 si `INFORME` vacío) |

## CORE — BD ∩ OD vigente (2025/2026)

Presentes en ambos esquemas actuales (nombres directos):

`INFORME`, `FECHA_INFORME`, `EXPEDIENTE`, `CUC_INAPS`, `ADMIN`, `UF`, `HECHO_VERIF`, `TIPIFICA_HECHO`, `CLASIF_HECHO`, `RESULT_HECHO`, `MOTIVO_ARCHIV_CONOC`, `RECOM_INFORME`, `DOC_CIERRE`, `NRO_DOC_CIERRE`, `FECHA_DOC_CIERRE`, `FECHA_DERIV`, `FEINICIO`, `FEFIN`, `TIPOSUP_INAPS`, `SUPERV_ORIENTATIVA`, `MES_META`, `TIPO_INF`, `TXCOORDINACION`, `OBLIG_CUMPL`, `OBL_INCUMPLIDA`, `SUBSANA`, `SUBS_LEVE`, `SUBS_TRAS`, `SUBSANADO`, `CUMPLIM_ADD`, `FILTRO_INF_UNIQ`, `TIPOACCION_INAPS`, `FECHA_REAL`, `YEAR_APROB`, `FEINI_ELAB_INF`, `TX_DOCUMENTO_PREVIO`, `TX_NUMERO_DOCUMENTO_PREVIO`, `FE_DOCUMENTO_PREVIO`, `FE_REGISTRO_DOCUMENTO_PREVIO`, `TX_OTRO_DOCUMENTO_PREVIO`, `FE_DERIV_DOC_DERIVACION`.

## EXTRAS_EQUIV (coalesce → canónica)

| Canónica | Fuentes (orden) |
|---|---|
| `ID_ADMINISTRADO` | `IDADMIN`, `IDAMIN`, `ID_ADMIN`, `IDADMINISTRADO` |
| `ID_UF` | `IDUF`, `ID_UF`, `IDUF_SIG` |
| `ADMIN` | `ADMIN`, `ADMINISTRADO_INAPS`, `TXADMINISTRADO_ADM` |
| `UF` | `UF`, `UF_INAPS`, `TXUNIDAD` |
| `RECOM_ACCION` | `RECOM_INAPS`, `RECOM_MA`, `RECOM_MEDIDAS` |
| `SECTOR_O_SUBSECTOR` | `SECTOR`, `SUBSECTOR`, `TXSUBSECTOR_UND` |
| `TXCOORDINACION` | `TXCOORDINACION`, `COORDINACION` |
| `TIPOACCION_INAPS` | `TIPOACCION_INAPS`, `TXACCION` |
| `TIPOSUP_INAPS` | `TIPOSUP_INAPS`, `TXTIPSUP` |
| `EXPEDIENTE` | `EXPEDIENTE`, `TXNUMEXP` |
| `TIPO_OD` | `TIPO` (solo OD; no confundir con `TIPO_INF`) |
| `RECOMENDACION_MEDIDAS_ADMIN` | `RECOMENDACION_DE_MEDIDAS_ADMINISTRATIVAS` |

## EXTRAS_BD (prioridad consumo BD reciente)

NULL en filas OD y en histórico sin el campo:

`DIREC`, `COORDINADOR`, `DIRECTOR`, `DOC_INICIO_ELA`, `FECHA_INICIO_ELA`, `PROVEIDO`, `FECHA_PROV`, `TIPO_INFRACCION`, `DAÑO_RIESGO_ASOCIADO`, `HUMANOS`, `AIRE`, `FLORA`, `FAUNA`, `AGUA`, `SUELO`, `TIPO_SUBSANACION`, `PRESUNTOS_INCUMPL`, `TOTAL_HECHOS`, `ACTA_TRANSF`, `FECHA_ACTA_TRASNF`, `RPS`, `FECHA_RPS`, `RECOMENDACION_MEDIDAS_ADMIN`, `RES_ACTA_MEDIDA`, `FECHA_MEDIDA`, `ESTADO`, `ANALISTA_LEGAL`, `RESPONSABLE_COMISION`.

## EXTRAS_OD (prioridad consumo OD reciente)

NULL en filas BD: `OD`, `CATEG`, `COMPET`, `TIPO_OD`.

---

## Expectativa por zona de datos

| Zona | Completitud esperada |
|---|---|
| 2025–2026 | Alta en CORE + extras de su familia (`FUENTE`) |
| 2019–2024 | CORE vía nombre/EQUIV; extras vigentes a menudo NULL |
| Sistema / vacío | No cargados (ver marginadas) |

---

## Columnas marginadas (siguen fuera)

### Códigos de motivo

| Código | Significado | Implicancia | Cómo reincorporar |
|---|---|---|---|
| `R4_REVISION` | Mirror `*_REV` | No aporta negocio al consumidor vigente | Solo si se audita cruce SIIA |
| `R5_SISTEMA_META` | Usuario, cuenta, `N°`, registro | No es hecho de supervisión | Auditoría de corrida aparte |
| `R6_VACIA_O_CASI` | Casi vacía en vigente | Ensanchar sin señal | Promover si el origen la puebla |
| `R7_SPARSE_LEGACY` | Solo en esquemas viejos (SIIA 2019–20) | NULL estructural en 2025/2026 | `EXTRAS` si se acepta sparse |
| `R1_CUBIERTO_EQUIV` | Alias ya absorbido en EQUIV | No se pierde si el alias está en la lista | Ampliar EQUIV si falta un alias |

### Marginadas (respecto a la unión histórica de RData)

| Columna | Motivo | Nota |
|---|---|---|
| `N°` | `R5_SISTEMA_META` | Correlativo de export; no negocio |
| `USUARIO` | `R5_SISTEMA_META` | Usuario de sistema (lleno en BD vigente; auditoría aparte) |
| `FECHA_REGISTRO` | `R5_SISTEMA_META` | Timestamp de registro/export |
| `INF_EVAL` | `R6_VACIA_O_CASI` | ~1% en Ago-2026; sin señal |
| `FECHA_INF_EVAL` | `R6_VACIA_O_CASI` | Idem |
| `ADMIN_REV`, `IDAMIN_REV`, `IDUF_REV`, `UF_REV`, `TXUNIDAD_REV`, `IDADMINISTRADO_REV`, `ID_SUR_UNIDAD_REV`, `ID_UF_UNIDAD_REV`, `TXADMINISTRADO_ADM_REV`, `FGSUP_ORIENTATIVA_REV` | `R4_REVISION` | Mirrors de revisión |
| `FEREG_SIIA`, `FEAPROB_SIIA`, `FEANUL_SIIA`, `FERPT`, `FGSUPUPD_*`, `TXFUENTE`, `TXOBJETIVO`, `TXUBIGEO_UND`, `TXMES`, `TXESTADO`, `TXESTADO_UF`, `TXETAPA_UF`, `TXDENUNCIA`, `TXMUESTREO`, `TXNVL_CMPLJ`, `TXOTRAFUENTE`, `TXACTIVIDAD_UND`, `TXACTIVIDADES_VINCULADAS`, `TXNOMBRE_*`, `TXCOFEMA`, `TXMOTIVOANULA`, `IDACTIVIDAD`, `IDUNIDAD`, `CUENTA`, `VALIDADO_META`, `MES_META_DERIV`, `FGSUP_ORIENTATIVA` | `R7_SPARSE_LEGACY` | Bloque SIIA / solo años antiguos; **ausente en plantilla 2025/2026** |
| `ESPECIALISTA`, `JEFE`, `FECHA_ELAB`, `ULTIMO_DOC_ELAB`, `COMPETENCIA` | `R7_SPARSE_LEGACY` | OD antiguos; no en OD 2025/2026 (sí están `COMPET`/`CATEG`/`OD`) |
| `COORDINACION`, `TXACCION`, `TXTIPSUP`, `TXNUMEXP` | `R1_CUBIERTO_EQUIV` | Absorbidos hacia canónicas vigentes |
| `SECTOR`, `SUBSECTOR` | `R1_CUBIERTO_EQUIV` | → `SECTOR_O_SUBSECTOR` |
| `RECOM_INAPS`, `RECOM_MA` | `R1_CUBIERTO_EQUIV` | → `RECOM_ACCION` |
| `ADMINISTRADO_INAPS`, `UF_INAPS`, `IDADMIN`, `IDUF_SIG` | `R1_CUBIERTO_EQUIV` | → `ADMIN` / `UF` / `ID_*` |

---

## Cómo reincorporar

1. Acordar canónica o ampliar `EQUIV`.
2. Actualizar este doc + `python/rdata/schema.py` / `map.py`.
3. Recargar: `create_stg` → `stage_rdata` → `main` (full refresh).
