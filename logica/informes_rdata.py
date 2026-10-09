# Lógica post-STG — informes RData.
# Capa: logica/ (sin conexiones). Entrada INF_RDATA; salidas RESULTADO / QA_*.
#
# RData: mapa canónico ya aplicado en stage_rdata.py; aquí QA suave.
# FORM y CSEP no pasan por aqui (Hop: pl_form_informes / pl_csep_informes).

# TODO /step 7 — trabajar sobre la tabla canónica cargada desde H2, sin conexiones externas.
RESULTADO = INF_RDATA.copy()

# TODO /step 8 — agregar QA suave: marcar filas cuyo INFORME está vacío o nulo.
_informe = RESULTADO["INFORME"].astype(str).str.strip()
RESULTADO["FG_SIN_INFORME"] = (
    RESULTADO["INFORME"].isna()
    | (_informe == "")
    | (_informe.str.lower() == "nan")
).astype(int)

# TODO /step 9 — resumir filas y faltantes por fuente y año para la verificación.
QA_RESUMEN = (
    RESULTADO.groupby(["FUENTE", "ANIO"], dropna=False)
    .agg(
        N=("INFORME", "size"),
        SIN_INFORME=("FG_SIN_INFORME", "sum"),
    )
    .reset_index()
)
