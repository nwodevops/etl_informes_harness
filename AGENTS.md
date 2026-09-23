# AGENTS.md — mapa para agentes (cascarón Hop + H2 + Python)

ETL **Apache Hop + H2 in-memory + Python**. Arquitectura: [`docs/arquitectura.md`](docs/arquitectura.md).

**Verificación diaria:** [`./init.sh`](init.sh) / [`./init.bat`](init.bat) → **`HARNESS OK`** (FORM + CSEP). Criterios: [`CHECKPOINTS.md`](CHECKPOINTS.md).

## Harness

| Archivo | Propósito |
|---|---|
| [`feature_list.json`](feature_list.json) | Alcance; **una** `in_progress` a la vez |
| [`progress/current.md`](progress/current.md) | Plan de sesión activa |
| [`progress/history.md`](progress/history.md) | Bitácora append-only |
| [`docs/harness/workflow.md`](docs/harness/workflow.md) | Roles líder / implementador / revisor |
| [`docs/harness/platform.md`](docs/harness/platform.md) | Hop, H2, variables |

## Skill

- [`.agents/skills/hop-python-etl/SKILL.md`](.agents/skills/hop-python-etl/SKILL.md)

## Preferir Apache Hop

**Siempre intentar Hop primero** para extract/load 1:1. Python solo para RData (homologación) / `logica/`.

| Workflow | Rol |
|---|---|
| [`wf_create_stg.hwf`](workflows/wf_create_stg.hwf) / [`wf_create_stg_windows.hwf`](workflows/wf_create_stg_windows.hwf) | **Bajo demanda:** DDL STG/DW + carga backup RData → `DW_INF_CONSOL_RDATA`. Primera vez, falten tablas, o cambien `.RData`. |
| [`wf_main.hwf`](workflows/wf_main.hwf) / [`wf_main_windows.hwf`](workflows/wf_main_windows.hwf) | **Diario:** solo FORM + CSEP (Hop truncate). |

## Inicio rápido

**Linux**

```bash
./switch-env.sh local
# Bajo demanda (RData/DDL): Hop → wf_create_stg.hwf
./init.sh                 # diario FORM+CSEP
~/apps/hop/hop-gui.sh     # → wf_main.hwf
```

**Windows**

```powershell
.\switch-env.ps1 local
# Bajo demanda: Hop → wf_create_stg_windows.hwf
.\init.bat                # diario FORM+CSEP
# Hop GUI → wf_main_windows.hwf
```

## Verificación

`init.sh` / `init.bat` → **HARNESS OK** diario:

1. `DW_INF_CONSOL_FORM` — Hop `pl_form_informes`
2. `DW_INF_CSEP_INFORMES_VIEW` — Hop `pl_csep_informes`

`DW_INF_CONSOL_RDATA` se refresca solo con `wf_create_stg*` (input_rdata es backup; no diario).

Requiere **hop-run**, Oracle DW, MySQL y SISUD vivos. RData/H2/Rscript solo para `wf_create_stg*`.

## Reglas críticas

1. **Un solo `.py`** en `logica/` — solo reglas post-STG RData.
2. **Sin secretos** en git.
3. **Sin `${VAR}` literal** en logs Hop.
4. `logica/` no abre conexiones. Homologación RData en `python/rdata/` + `stage_rdata.py`.
5. No `import io` (stdlib).
6. Destino Oracle: **TRUNCATE** en carga; CREATE si faltan → `ensure_dw_tables` en `wf_create_stg*`.
7. FORM/CSEP → pipelines Hop.

## Orden de ejecución

### Primera vez / cuando cambien los `.RData`

Play **`wf_create_stg.hwf`** (Linux) o **`wf_create_stg_windows.hwf`** (Windows):

1. Reset H2  
2. CREATE `STG_*`  
3. CREATE `DW_INF_*` si faltan  
4. Stage RData → H2  
5. Python → `DW_INF_CONSOL_RDATA`

### Todos los días

Play **`wf_main.hwf`** / **`wf_main_windows.hwf`** (o `./init.sh` / `init.bat`):

1. Hop FORM → `DW_INF_CONSOL_FORM`  
2. Hop CSEP → `DW_INF_CSEP_INFORMES_VIEW`

| OS | Bajo demanda | Diario |
|---|---|---|
| Linux | `wf_create_stg.hwf` | `wf_main.hwf` / `init.sh` |
| Windows | `wf_create_stg_windows.hwf` | `wf_main_windows.hwf` / `init.bat` |
