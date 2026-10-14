# Contrato capas — informes RData + FORM (Hop) + CSEP (Hop)

## Dónde va cada cosa

| Capa | Carpeta | Responsabilidad | No hace |
|---|---|---|---|
| **STG / DDL** | `python/stg/create_stg.py`, `python/introspect/` | DDL H2 `STG_INF_CONSOL` | Filas, negocio |
| **Extract RData** | `python/stage/stage_rdata.py` | Rscript → homologar cols (`rdata.map`) → H2 | KPIs, Oracle |
| **Contrato cols** | `python/rdata/schema.py` | CANONICAL, tipos, DDL/COMMENT Oracle | I/O runtime |
| **Adapter mapa** | `python/rdata/map.py` | EQUIV + `map_to_canonical` | Conexiones |
| **I/O post** | `python/io/` | Leer H2, TRUNCATE+INSERT Oracle + MySQL DW / Excel | Reglas |
| **Negocio** | `logica/informes_rdata.py` | QA RData (`FG_SIN_INFORME`) | Conexiones, FORM, CSEP |
| **FORM Hop** | `pipelines/pl_form_informes.hpl` | MySQL HEC → `oracle_dw` + `mysql_dw` FORM truncate | H2, logica |
| **CSEP Hop** | `pipelines/pl_csep_informes.hpl` | Vista SISUD → `oracle_dw` + `mysql_dw` CSEP truncate | Python load |

## Flujo

```
python/stg/create_stg.py          → DDL STG_INF_CONSOL
python/stage/stage_rdata.py       → RData → rdata.map → H2
python/main.py
  → io/leer_h2.py             (INF_RDATA)
  → logica/informes_rdata.py  (RESULTADO, QA_*)
  → io/escribir_oracle.py     (TRUNCATE DW_INF_CONSOL_RDATA @ oracle_dw)
  → io/escribir_mysql.py      (TRUNCATE DW_INF_CONSOL_RDATA @ mysql_dw)
pipelines/pl_form_informes.hpl    → TRUNCATE FORM @ oracle_dw + mysql_dw
pipelines/pl_csep_informes.hpl    → TRUNCATE CSEP @ oracle_dw + mysql_dw
```

DDL destino: una vez vía `ensure_dw_tables` / [`sql/dw/`](../sql/dw/) (Oracle + MySQL mirror).

## Entrada (Python / logica)

| Clave | Origen H2 |
|---|---|
| `INF_RDATA` | `PUBLIC.STG_INF_CONSOL` |

## Salida

| Nombre | Destino | Cómo |
|---|---|---|
| `RESULTADO` | `oracle_dw` + `mysql_dw` `DW_INF_CONSOL_RDATA` | Python TRUNCATE+INSERT |
| (Hop) | `oracle_dw` + `mysql_dw` `DW_INF_CONSOL_FORM` | `pl_form_informes` (copy) |
| (Hop) | `oracle_dw` + `mysql_dw` `DW_INF_CSEP_INFORMES_VIEW` | `pl_csep_informes` (copy) |

## Reglas

- Un solo `.py` en `logica/`.
- Sin conexiones ni drivers en `logica/` (I/O en `python/io/`).
- `pandas` inyectado como `pd`.
- Homologación RData = `python/rdata/` + `python/stage/stage_rdata.py`.
- FORM/CSEP: Hop puro (copy a Oracle + MySQL DW); hard-fail si fuente o destinos caen.
- Fuente HEC = `mysql` / `DB_MYSQL_*`; mirror DW = `mysql_dw` / `DB_MYSQL_DW_*` (no mezclar).
- No mezclar RData y FORM en una sola tabla.
