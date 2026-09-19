# Lógica post-STG — informes RData.
# Capa: logica/ (sin conexiones). Entrada INF_RDATA; salidas RESULTADO + QA_*.
#
# El mapa canónico (EQUIV / columnas) ya lo aplicó python/stage_rdata.py.
# Aquí: reglas de negocio / QA sobre el consolidado.

RESULTADO = INF_RDATA.copy()

# QA suave: marcar filas sin número de informe
_informe = RESULTADO["INFORME"].astype(str).str.strip()
RESULTADO["FG_SIN_INFORME"] = (
    RESULTADO["INFORME"].isna()
    | (_informe == "")
    | (_informe.str.lower() == "nan")
).astype(int)

QA_RESUMEN = (
    RESULTADO.groupby(["FUENTE", "ANIO"], dropna=False)
    .agg(
        N=("INFORME", "size"),
        SIN_INFORME=("FG_SIN_INFORME", "sum"),
    )
    .reset_index()
)
