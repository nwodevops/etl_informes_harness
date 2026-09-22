# Lógica post-STG — informes RData.
# Capa: logica/ (sin conexiones). Entrada INF_RDATA; salidas RESULTADO / QA_*.
#
# RData: mapa canónico ya aplicado en stage_rdata.py; aquí QA suave.
# FORM y CSEP no pasan por aqui (Hop: pl_form_informes / pl_csep_informes).

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
