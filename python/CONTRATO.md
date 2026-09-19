# Contrato capas — informes RData

## Dónde va cada cosa

| Capa | Carpeta | Responsabilidad | No hace |
|---|---|---|---|
| **STG / DDL** | `python/create_stg.py`, `python/introspect/` | DDL H2 desde contrato | Filas, negocio |
| **Extract RData** | `python/stage_rdata.py` | Rscript → homologar cols (`rdata.map`) → H2 | KPIs, Oracle |
| **Contrato cols** | `python/rdata/schema.py` | CANONICAL, tipos, DDL/COMMENT Oracle | I/O |
| **Adapter mapa** | `python/rdata/map.py` | EQUIV + `map_to_canonical` | Conexiones |
| **I/O post** | `python/io/` | Leer H2, escribir Oracle/Excel | Reglas |
| **Negocio** | `logica/informes_rdata.py` | QA / transform post-STG | Conexiones, drivers |

## Flujo

```
python/create_stg.py          → DDL STG_INF_CONSOL (rdata.schema)
python/stage_rdata.py         → RData → rdata.map → H2
python/main.py
  → io/leer_h2.py             (INF_RDATA)
  → logica/informes_rdata.py  (RESULTADO, QA_*, FG_SIN_INFORME)
  → io/escribir_oracle.py     (APP.INF_CONSOL_RDATA + COMMENT)
  → io/escribir_excel.py      (opcional)
```

## Entrada

| Clave | Origen H2 |
|---|---|
| `INF_RDATA` | `PUBLIC.STG_INF_CONSOL` |

## Salida obligatoria

| Nombre | Descripción |
|---|---|
| `RESULTADO` | Consolidado canónico (mapa en `docs/rdata_column_map.md`) |

Opcional: `QA_RESUMEN` (conteos por `FUENTE`/`ANIO`).

## Reglas

- Un solo `.py` en `logica/`.
- Sin conexiones ni drivers en `logica/` (I/O en `python/io/`).
- `pandas` inyectado como `pd`.
- Homologación de columnas R heterogéneas = adapter de staging (`python/`), no lógica de negocio.
