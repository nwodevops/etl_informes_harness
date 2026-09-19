"""Contrato de columnas canónicas RData (H2 STG + Oracle DW).

Capa: python/ — esquema / DDL / comentarios. Sin I/O ni reglas de negocio.
Fuente humana: docs/rdata_column_map.md
"""

from __future__ import annotations

# (nombre, h2_type, oracle_type_hint) — oracle: VARCHAR2 | CLOB | NUMBER | DATE

PROVENANCE: list[tuple[str, str, str]] = [
    ("FUENTE", "VARCHAR", "VARCHAR2"),
    ("ANIO", "BIGINT", "NUMBER"),
    ("MES_CORTE", "VARCHAR", "VARCHAR2"),
    ("ARCHIVO", "VARCHAR", "VARCHAR2"),
    ("OBJETO_R", "VARCHAR", "VARCHAR2"),
]

# CORE = BD∩OD vigente 2025/2026 (nombres directos; ids/aliases van por EQUIV)
CORE: list[tuple[str, str, str]] = [
    ("INFORME", "VARCHAR", "VARCHAR2"),
    ("FECHA_INFORME", "TIMESTAMP", "DATE"),
    ("EXPEDIENTE", "VARCHAR", "VARCHAR2"),
    ("CUC_INAPS", "VARCHAR", "VARCHAR2"),
    ("ADMIN", "VARCHAR", "VARCHAR2"),
    ("UF", "VARCHAR", "VARCHAR2"),
    ("HECHO_VERIF", "VARCHAR", "CLOB"),
    ("TIPIFICA_HECHO", "VARCHAR", "VARCHAR2"),
    ("CLASIF_HECHO", "VARCHAR", "VARCHAR2"),
    ("RESULT_HECHO", "VARCHAR", "VARCHAR2"),
    ("MOTIVO_ARCHIV_CONOC", "VARCHAR", "VARCHAR2"),
    ("RECOM_INFORME", "VARCHAR", "VARCHAR2"),
    ("DOC_CIERRE", "VARCHAR", "VARCHAR2"),
    ("NRO_DOC_CIERRE", "VARCHAR", "VARCHAR2"),
    ("FECHA_DOC_CIERRE", "TIMESTAMP", "DATE"),
    ("FECHA_DERIV", "TIMESTAMP", "DATE"),
    ("FEINICIO", "TIMESTAMP", "DATE"),
    ("FEFIN", "TIMESTAMP", "DATE"),
    ("TIPOSUP_INAPS", "VARCHAR", "VARCHAR2"),
    ("SUPERV_ORIENTATIVA", "VARCHAR", "VARCHAR2"),
    ("MES_META", "VARCHAR", "VARCHAR2"),
    ("TIPO_INF", "VARCHAR", "VARCHAR2"),
    ("TXCOORDINACION", "VARCHAR", "VARCHAR2"),
    ("OBLIG_CUMPL", "BIGINT", "NUMBER"),
    ("OBL_INCUMPLIDA", "BIGINT", "NUMBER"),
    ("SUBSANA", "VARCHAR", "VARCHAR2"),
    ("SUBS_LEVE", "BIGINT", "NUMBER"),
    ("SUBS_TRAS", "BIGINT", "NUMBER"),
    ("SUBSANADO", "BIGINT", "NUMBER"),
    ("CUMPLIM_ADD", "BIGINT", "NUMBER"),
    ("FILTRO_INF_UNIQ", "BIGINT", "NUMBER"),
    ("TIPOACCION_INAPS", "VARCHAR", "VARCHAR2"),
    ("FECHA_REAL", "TIMESTAMP", "DATE"),
    ("YEAR_APROB", "BIGINT", "NUMBER"),
    ("FEINI_ELAB_INF", "TIMESTAMP", "DATE"),
    ("TX_DOCUMENTO_PREVIO", "VARCHAR", "VARCHAR2"),
    ("TX_NUMERO_DOCUMENTO_PREVIO", "VARCHAR", "VARCHAR2"),
    ("FE_DOCUMENTO_PREVIO", "TIMESTAMP", "DATE"),
    ("FE_REGISTRO_DOCUMENTO_PREVIO", "TIMESTAMP", "DATE"),
    ("TX_OTRO_DOCUMENTO_PREVIO", "VARCHAR", "VARCHAR2"),
    ("FE_DERIV_DOC_DERIVACION", "TIMESTAMP", "DATE"),
]

EXTRAS_EQUIV: list[tuple[str, str, str]] = [
    ("ID_ADMINISTRADO", "VARCHAR", "VARCHAR2"),
    ("ID_UF", "VARCHAR", "VARCHAR2"),
    ("RECOM_ACCION", "VARCHAR", "VARCHAR2"),
    ("SECTOR_O_SUBSECTOR", "VARCHAR", "VARCHAR2"),
]

EXTRAS_BD: list[tuple[str, str, str]] = [
    ("DIREC", "VARCHAR", "VARCHAR2"),
    ("COORDINADOR", "VARCHAR", "VARCHAR2"),
    ("DIRECTOR", "VARCHAR", "VARCHAR2"),
    ("DOC_INICIO_ELA", "VARCHAR", "VARCHAR2"),
    ("FECHA_INICIO_ELA", "TIMESTAMP", "DATE"),
    ("PROVEIDO", "VARCHAR", "VARCHAR2"),
    ("FECHA_PROV", "TIMESTAMP", "DATE"),
    ("TIPO_INFRACCION", "VARCHAR", "VARCHAR2"),
    ("DAÑO_RIESGO_ASOCIADO", "VARCHAR", "VARCHAR2"),
    ("HUMANOS", "BIGINT", "NUMBER"),
    ("AIRE", "BIGINT", "NUMBER"),
    ("FLORA", "BIGINT", "NUMBER"),
    ("FAUNA", "BIGINT", "NUMBER"),
    ("AGUA", "BIGINT", "NUMBER"),
    ("SUELO", "BIGINT", "NUMBER"),
    ("TIPO_SUBSANACION", "VARCHAR", "VARCHAR2"),
    ("PRESUNTOS_INCUMPL", "BIGINT", "NUMBER"),
    ("TOTAL_HECHOS", "BIGINT", "NUMBER"),
    ("ACTA_TRANSF", "VARCHAR", "VARCHAR2"),
    ("FECHA_ACTA_TRASNF", "TIMESTAMP", "DATE"),
    ("RPS", "VARCHAR", "VARCHAR2"),
    ("FECHA_RPS", "TIMESTAMP", "DATE"),
    ("RECOMENDACION_MEDIDAS_ADMIN", "VARCHAR", "VARCHAR2"),
    ("RES_ACTA_MEDIDA", "VARCHAR", "VARCHAR2"),
    ("FECHA_MEDIDA", "TIMESTAMP", "DATE"),
    ("ESTADO", "VARCHAR", "VARCHAR2"),
    ("ANALISTA_LEGAL", "VARCHAR", "VARCHAR2"),
    ("RESPONSABLE_COMISION", "VARCHAR", "VARCHAR2"),
]

EXTRAS_OD: list[tuple[str, str, str]] = [
    ("OD", "VARCHAR", "VARCHAR2"),
    ("CATEG", "VARCHAR", "VARCHAR2"),
    ("COMPET", "VARCHAR", "VARCHAR2"),
    ("TIPO_OD", "VARCHAR", "VARCHAR2"),
]

EXTRAS_QA: list[tuple[str, str, str]] = [
    ("FG_SIN_INFORME", "BIGINT", "NUMBER"),
]

EXTRAS: list[tuple[str, str, str]] = [
    *EXTRAS_EQUIV,
    *EXTRAS_BD,
    *EXTRAS_OD,
    *EXTRAS_QA,
]

CANONICAL: list[tuple[str, str, str]] = [*PROVENANCE, *CORE, *EXTRAS]
CANONICAL_NAMES: list[str] = [c[0] for c in CANONICAL]

DATE_COLS = {n for n, _, o in CANONICAL if o == "DATE"}
NUMBER_COLS = {n for n, _, o in CANONICAL if o == "NUMBER"}
CLOB_COLS = {n for n, _, o in CANONICAL if o == "CLOB"}

TABLE_COMMENT = (
    "Informes consolidados BD+OD (RData 2019–2026). "
    "Estructura anclada a esquema vigente 2025/2026; histórico vía EQUIV/NULL. "
    "ETL: Hop+H2+Python → full refresh."
)

COLUMN_COMMENTS: dict[str, str] = {
    "FUENTE": "Origen del corte: BD (boletin central) u OD (oficinas desconcentradas).",
    "ANIO": "Año del corte extraído del nombre del archivo RData.",
    "MES_CORTE": "Mes del corte (ej. AGOSTO, DICIEMBRE) desde el nombre del archivo.",
    "ARCHIVO": "Basename del archivo .RData de origen.",
    "OBJETO_R": "Nombre del data.frame R cargado desde el RData.",
    "INFORME": "Identificador / número del informe de supervisión.",
    "FECHA_INFORME": "Fecha del informe.",
    "EXPEDIENTE": "Número de expediente (EQUIV: EXPEDIENTE, TXNUMEXP).",
    "CUC_INAPS": "Código único de caso (CUC) en INAPS.",
    "ADMIN": "Administrado / administrado INAPS (EQUIV: ADMIN, ADMINISTRADO_INAPS, TXADMINISTRADO_ADM).",
    "UF": "Unidad fiscalizable (EQUIV: UF, UF_INAPS, TXUNIDAD).",
    "HECHO_VERIF": "Descripción del hecho verificado (texto largo).",
    "TIPIFICA_HECHO": "Tipificación del hecho.",
    "CLASIF_HECHO": "Clasificación del hecho.",
    "RESULT_HECHO": "Resultado del hecho.",
    "MOTIVO_ARCHIV_CONOC": "Motivo de archivamiento / conocimiento.",
    "RECOM_INFORME": "Recomendación consignada en el informe.",
    "DOC_CIERRE": "Documento de cierre.",
    "NRO_DOC_CIERRE": "Número del documento de cierre.",
    "FECHA_DOC_CIERRE": "Fecha del documento de cierre.",
    "FECHA_DERIV": "Fecha de derivación.",
    "FEINICIO": "Fecha de inicio de la supervisión / acción.",
    "FEFIN": "Fecha de fin de la supervisión / acción.",
    "TIPOSUP_INAPS": "Tipo de supervisión INAPS (EQUIV: TIPOSUP_INAPS, TXTIPSUP).",
    "SUPERV_ORIENTATIVA": "Indicador / marca de supervisión orientativa.",
    "MES_META": "Mes meta asociado al informe.",
    "TIPO_INF": "Tipo de informe.",
    "TXCOORDINACION": "Coordinación (EQUIV: TXCOORDINACION, COORDINACION).",
    "OBLIG_CUMPL": "Cantidad de obligaciones cumplidas.",
    "OBL_INCUMPLIDA": "Cantidad de obligaciones incumplidas.",
    "SUBSANA": "Marca / texto de subsanación.",
    "SUBS_LEVE": "Conteo de subsanaciones leves.",
    "SUBS_TRAS": "Conteo de subsanaciones trascendentales.",
    "SUBSANADO": "Conteo / flag de hechos subsanados.",
    "CUMPLIM_ADD": "Cumplimiento adicional (conteo).",
    "FILTRO_INF_UNIQ": "Flag de filtro para informe único.",
    "TIPOACCION_INAPS": "Tipo de acción INAPS (EQUIV: TIPOACCION_INAPS, TXACCION).",
    "FECHA_REAL": "Fecha real de la acción / supervisión.",
    "YEAR_APROB": "Año de aprobación.",
    "FEINI_ELAB_INF": "Fecha de inicio de elaboración del informe.",
    "TX_DOCUMENTO_PREVIO": "Tipo / descripción del documento previo.",
    "TX_NUMERO_DOCUMENTO_PREVIO": "Número del documento previo.",
    "FE_DOCUMENTO_PREVIO": "Fecha del documento previo.",
    "FE_REGISTRO_DOCUMENTO_PREVIO": "Fecha de registro del documento previo.",
    "TX_OTRO_DOCUMENTO_PREVIO": "Otro documento previo (texto).",
    "FE_DERIV_DOC_DERIVACION": "Fecha de derivación del documento de derivación.",
    "ID_ADMINISTRADO": "Id del administrado (EQUIV: IDADMIN, IDAMIN, ID_ADMIN, IDADMINISTRADO).",
    "ID_UF": "Id de la unidad fiscalizable (EQUIV: IDUF, ID_UF, IDUF_SIG).",
    "RECOM_ACCION": "Recomendación de acción / medidas (EQUIV: RECOM_INAPS, RECOM_MA, RECOM_MEDIDAS).",
    "SECTOR_O_SUBSECTOR": "Sector (BD) o subsector (OD) coalescido (EQUIV: SECTOR, SUBSECTOR, TXSUBSECTOR_UND).",
    "DIREC": "[BD] Dirección / área orgánica.",
    "COORDINADOR": "[BD] Coordinador responsable.",
    "DIRECTOR": "[BD] Director responsable.",
    "DOC_INICIO_ELA": "[BD] Documento de inicio de elaboración.",
    "FECHA_INICIO_ELA": "[BD] Fecha de inicio de elaboración.",
    "PROVEIDO": "[BD] Proveído.",
    "FECHA_PROV": "[BD] Fecha del proveído.",
    "TIPO_INFRACCION": "[BD] Tipo de infracción.",
    "DAÑO_RIESGO_ASOCIADO": "[BD] Daño o riesgo asociado al hecho.",
    "HUMANOS": "[BD] Flag/conteo componente humanos.",
    "AIRE": "[BD] Flag/conteo componente aire.",
    "FLORA": "[BD] Flag/conteo componente flora.",
    "FAUNA": "[BD] Flag/conteo componente fauna.",
    "AGUA": "[BD] Flag/conteo componente agua.",
    "SUELO": "[BD] Flag/conteo componente suelo.",
    "TIPO_SUBSANACION": "[BD] Tipo de subsanación.",
    "PRESUNTOS_INCUMPL": "[BD] Presuntos incumplimientos (conteo).",
    "TOTAL_HECHOS": "[BD] Total de hechos.",
    "ACTA_TRANSF": "[BD] Acta de transferencia.",
    "FECHA_ACTA_TRASNF": "[BD] Fecha del acta de transferencia.",
    "RPS": "[BD] RPS / resolución asociada.",
    "FECHA_RPS": "[BD] Fecha del RPS.",
    "RECOMENDACION_MEDIDAS_ADMIN": "[BD] Recomendación de medidas administrativas (EQUIV nombre con espacios).",
    "RES_ACTA_MEDIDA": "[BD] Resolución / acta de medida.",
    "FECHA_MEDIDA": "[BD] Fecha de la medida.",
    "ESTADO": "[BD] Estado del registro en el export vigente.",
    "ANALISTA_LEGAL": "[BD] Analista legal asignado.",
    "RESPONSABLE_COMISION": "[BD] Responsable de comisión.",
    "OD": "[OD] Oficina desconcentrada.",
    "CATEG": "[OD] Categoría.",
    "COMPET": "[OD] Competencia.",
    "TIPO_OD": "[OD] Tipo OD (fuente TIPO; no confundir con TIPO_INF).",
    "FG_SIN_INFORME": "QA ETL (logica/): 1 si INFORME vacío/nulo; 0 en caso contrario.",
}


def _sql_quote(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def oracle_comment_statements(schema: str, table: str) -> list[str]:
    """COMMENT ON TABLE/COLUMN para APP.INF_CONSOL_RDATA."""
    stmts = [f"COMMENT ON TABLE {schema}.{table} IS {_sql_quote(TABLE_COMMENT)}"]
    missing = [n for n in CANONICAL_NAMES if n not in COLUMN_COMMENTS]
    if missing:
        raise ValueError(f"COLUMN_COMMENTS incompleto: {missing}")
    for name in CANONICAL_NAMES:
        stmts.append(
            f"COMMENT ON COLUMN {schema}.{table}.{name} IS "
            f"{_sql_quote(COLUMN_COMMENTS[name])}"
        )
    return stmts


def oracle_ddl(schema: str, table: str) -> str:
    """CREATE TABLE APP.INF_CONSOL_RDATA …"""
    wide_1000 = {
        "ARCHIVO",
        "OBJETO_R",
        "TXCOORDINACION",
        "UF",
        "ADMIN",
        "COORDINADOR",
        "DIRECTOR",
        "OD",
        "ADMINISTRADO_INAPS",
        "PROVEIDO",
        "NRO_DOC_CIERRE",
        "EXPEDIENTE",
        "INFORME",
        "CUC_INAPS",
        "ANALISTA_LEGAL",
        "RESPONSABLE_COMISION",
    }
    wide_2000 = {
        "TIPIFICA_HECHO",
        "MOTIVO_ARCHIV_CONOC",
        "TX_DOCUMENTO_PREVIO",
        "TX_OTRO_DOCUMENTO_PREVIO",
        "RECOMENDACION_MEDIDAS_ADMIN",
        "DOC_INICIO_ELA",
        "DOC_CIERRE",
        "HECHO_VERIF",
        "RESULT_HECHO",
        "RECOM_INFORME",
        "RECOM_ACCION",
        "RES_ACTA_MEDIDA",
    }
    lines: list[str] = []
    for name, _h2, ora in CANONICAL:
        if ora == "CLOB" or name == "HECHO_VERIF":
            lines.append(f"  {name} CLOB")
        elif ora == "DATE":
            lines.append(f"  {name} DATE")
        elif ora == "NUMBER":
            lines.append(f"  {name} NUMBER")
        elif name in wide_2000:
            lines.append(f"  {name} VARCHAR2(2000)")
        elif name in wide_1000:
            lines.append(f"  {name} VARCHAR2(1000)")
        else:
            lines.append(f"  {name} VARCHAR2(500)")
    body = ",\n".join(lines)
    return f"CREATE TABLE {schema}.{table} (\n{body}\n)"
