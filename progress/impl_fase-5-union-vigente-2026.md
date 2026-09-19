# impl fase-5-union-vigente-2026

## Qué

Cerrar la unión BD∪OD vigente: +3 columnas de negocio BD 2025/2026.

## Cómo

- `python/rdata_schema.py` — `EXTRAS_BD`: `ESTADO`, `ANALISTA_LEGAL`, `RESPONSABLE_COMISION`
- `docs/rdata_column_map.md` — 83 cols; marginadas solo meta/vacías
- Full refresh H2 + Oracle

## Fuera (a propósito)

`N°`, `USUARIO`, `FECHA_REGISTRO`, `INF_EVAL`, `FECHA_INF_EVAL`

## Evidencia

- `./init.sh` → **HARNESS OK**
- Oracle: **111091** filas × **83** cols
- BD 2026: `ESTADO` 5508/5508, `ANALISTA_LEGAL` 5500/5508, `RESPONSABLE_COMISION` 5502/5508
- OD vigente: NULL en las tres (esperado; solo-BD)
