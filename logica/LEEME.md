# logica/

**Un solo `.py`** (auto-descubierto por `python/main.py`). Sin conexiones ni drivers.
Aquí va la lógica de procesamiento de datos **post-STG RData** (QA, flags, KPIs).

FORM y CSEP no pasan por aquí (Hop: `pl_form_informes` / `pl_csep_informes`).

| Archivo | Rol |
|---|---|
| [`informes_rdata.py`](informes_rdata.py) | RData: `FG_SIN_INFORME` + `QA_RESUMEN` → `RESULTADO` |
| Plantilla | [`../python/plantilla_logica.py`](../python/plantilla_logica.py) |
| Contrato | [`../python/CONTRATO.md`](../python/CONTRATO.md) |

**No va aquí**

| Qué | Dónde |
|---|---|
| Homologación columnas RData (`EQUIV`, rename) | `python/rdata/map.py` + `python/stage/stage_rdata.py` |
| Extract / DDL / I/O RData | `python/stg/`, `python/stage/`, `python/io/` |
| FORM / CSEP | `pipelines/pl_form_informes.hpl`, `pipelines/pl_csep_informes.hpl` |
