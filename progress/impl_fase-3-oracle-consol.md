# impl fase-3-oracle-consol

## Qué

Consolidar 14 RData (BD+OD 2019–2025) → `APP.DW_INF_CONSOL_RDATA` vía mapa canónico.

## Cómo

1. `inputs.yaml` type `rdata`
2. `create_stg.py` + `introspect/rdata.py` → DDL `STG_INF_CONSOL`
3. `stage_rdata.py` (Rscript) → H2
4. `logica/informes_rdata.py` → `escribir_oracle.py`

Mapa: `docs/rdata_column_map.md`
