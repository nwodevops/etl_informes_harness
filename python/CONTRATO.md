# Contrato capas — informes RData + FORM (MySQL HEC)

## Dónde va cada cosa

| Capa | Carpeta | Responsabilidad | No hace |
|---|---|---|---|
| **STG / DDL** | `python/create_stg.py`, `python/introspect/` | DDL H2 desde contrato | Filas, negocio |
| **Extract RData** | `python/stage_rdata.py` | Rscript → homologar cols (`rdata.map`) → H2 | KPIs, Oracle |
| **Extract MySQL** | `python/stage_mysql.py` | SQL HEC → reindex CANONICAL → H2 | KPIs, Oracle |
| **Contrato cols** | `python/rdata/schema.py` | CANONICAL, tipos, DDL/COMMENT Oracle | I/O |
| **Adapter mapa** | `python/rdata/map.py` | EQUIV + `map_to_canonical` | Conexiones |
| **I/O post** | `python/io/` | Leer H2, escribir Oracle/Excel | Reglas |
| **Negocio** | `logica/informes_rdata.py` | QA RData + passthrough FORM | Conexiones, drivers |

## Flujo

```
python/create_stg.py          → DDL STG_INF_CONSOL + STG_INF_CONSOL_FORM
python/stage_rdata.py         → RData → rdata.map → H2
python/stage_mysql.py         → MySQL SQL → H2
python/main.py
  → io/leer_h2.py             (INF_RDATA, INF_FORM)
  → logica/informes_rdata.py  (RESULTADO, RESULTADO_FORM, QA_*)
  → io/escribir_oracle.py     (DW_INF_CONSOL_RDATA + DW_INF_CONSOL_FORM)
  → io/escribir_excel.py      (opcional, solo RData)
```

## Entrada

| Clave | Origen H2 |
|---|---|
| `INF_RDATA` | `PUBLIC.STG_INF_CONSOL` |
| `INF_FORM` | `PUBLIC.STG_INF_CONSOL_FORM` |

## Salida

| Nombre | Destino Oracle | Descripción |
|---|---|---|
| `RESULTADO` | `APP.DW_INF_CONSOL_RDATA` | Consolidado RData + `FG_SIN_INFORME` |
| `RESULTADO_FORM` | `APP.DW_INF_CONSOL_FORM` | Passthrough SQL MySQL; **siempre** se escribe (0 filas si MySQL cae) |

Tras `main` / `wf_main`, oracle_dw debe tener también `DW_INF_CSEP_INFORMES_VIEW` (DDL+Hop/load).

Opcional: `QA_RESUMEN`, `QA_RESUMEN_FORM` (conteos por `FUENTE`/`ANIO`).

## Reglas

- Un solo `.py` en `logica/`.
- Sin conexiones ni drivers en `logica/` (I/O en `python/io/`).
- `pandas` inyectado como `pd`.
- Homologación RData = `python/rdata/` + `stage_rdata.py`; FORM = SQL ya canónico.
- No mezclar RData y FORM en una sola tabla.
