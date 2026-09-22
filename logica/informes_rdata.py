# Lógica post-STG — informes RData + FORM (MySQL HEC).
# Capa: logica/ (sin conexiones). Entradas INF_RDATA / INF_FORM; salidas RESULTADO*.
#
# RData: mapa canónico ya aplicado en stage_rdata.py; aquí QA suave.
# FORM: passthrough puro (SQL MySQL ya trae canónico + FG_SIN_INFORME).

RESULTADO = INF_RDATA.copy()

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

# FORM: sin re-mapear ni mezclar con RData
RESULTADO_FORM = INF_FORM.copy()

if len(RESULTADO_FORM):
    QA_RESUMEN_FORM = (
        RESULTADO_FORM.groupby(["FUENTE", "ANIO"], dropna=False)
        .agg(N=("INFORME", "size"))
        .reset_index()
    )
else:
    QA_RESUMEN_FORM = pd.DataFrame(columns=["FUENTE", "ANIO", "N"])
