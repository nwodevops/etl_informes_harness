# Contrato capas — informes RData + FORM (Hop) + CSEP (Hop)

## Dónde va cada cosa

| Capa | Carpeta | Responsabilidad | No hace |
|---|---|---|---|
| **STG / DDL** | `python/stg/create_stg.py`, `python/introspect/` | DDL H2 `STG_INF_CONSOL` | Filas, negocio |
| **Extract RData** | `python/stage/stage_rdata.py` | Rscript → homologar cols (`rdata.map`) → H2 | KPIs, Oracle |
| **Contrato cols** | `python/rdata/schema.py` | CANONICAL, tipos, DDL/COMMENT Oracle | I/O runtime |
| **Adapter mapa** | `python/rdata/map.py` | EQUIV + `map_to_canonical` | Conexiones |
| **I/O post** | `python/io/` | Leer H2, TRUNCATE+INSERT Oracle/Excel | Reglas |
| **Negocio** | `logica/informes_rdata.py` | QA RData (`FG_SIN_INFORME`) | Conexiones, FORM, CSEP |
| **FORM Hop** | `pipelines/pl_form_informes.hpl` | MySQL SQL → `DW_INF_CONSOL_FORM` truncate | H2, logica |
| **CSEP Hop** | `pipelines/pl_csep_informes.hpl` | Vista SISUD → `DW_INF_CSEP_INFORMES_VIEW` truncate | Python load |

## Flujo

```
python/stg/create_stg.py          → DDL STG_INF_CONSOL
python/stage/stage_rdata.py       → RData → rdata.map → H2
python/main.py
  → io/leer_h2.py             (INF_RDATA)
  → logica/informes_rdata.py  (RESULTADO, QA_*)
  → io/escribir_oracle.py     (TRUNCATE DW_INF_CONSOL_RDATA)
pipelines/pl_form_informes.hpl    → TRUNCATE DW_INF_CONSOL_FORM
pipelines/pl_csep_informes.hpl    → TRUNCATE DW_INF_CSEP_INFORMES_VIEW
```

DDL Oracle destino: una vez en [`sql/dw/`](../sql/dw/).

## Entrada (Python / logica)

| Clave | Origen H2 |
|---|---|
| `INF_RDATA` | `PUBLIC.STG_INF_CONSOL` |

## Salida

| Nombre | Destino Oracle | Cómo |
|---|---|---|
| `RESULTADO` | `APP.DW_INF_CONSOL_RDATA` | Python TRUNCATE+INSERT |
| (Hop) | `APP.DW_INF_CONSOL_FORM` | `pl_form_informes` |
| (Hop) | `DW_INF_CSEP_INFORMES_VIEW` | `pl_csep_informes` |

## Reglas

- Un solo `.py` en `logica/`.
- Sin conexiones ni drivers en `logica/` (I/O en `python/io/`).
- `pandas` inyectado como `pd`.
- Homologación RData = `python/rdata/` + `python/stage/stage_rdata.py`.
- FORM/CSEP: Hop puro; hard-fail si MySQL/SISUD caen.
- No mezclar RData y FORM en una sola tabla.
