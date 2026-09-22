# impl fase-4-schema-gradual-2026

## Qué

Redefinir `APP.DW_INF_CONSOL_RDATA` como estructura gradual anclada a BD/OD 2025–2026 (+30 cols, `MES_CORTE`).

## Cómo

- `python/rdata_schema.py` — CORE vigente + EXTRAS_BD/OD + EQUIV R1
- `docs/rdata_column_map.md` — documenta gradualidad
- Carga incluye `BDInf_Agosto_2026` / `ODInf_Agosto_2026`

## Evidencia

- Oracle: **111091** filas × **80** columnas
- Agosto 2026: BD 5508 (`DIREC` lleno), OD 3834 (`OD` lleno)
- Dic 2025: BD 8916 + OD 6032
