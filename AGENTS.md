# AGENTS.md — mapa para agentes (ETL Hop + H2 + Python)

ETL **Apache Hop + H2 in-memory + Python**. Antes de editar, confirma que el archivo o workflow mencionado existe en este checkout. Arquitectura: [`docs/arquitectura.md`](docs/arquitectura.md).

**Verificación diaria:** [`./init.sh`](init.sh) / [`./init.bat`](init.bat) → **`HARNESS OK`**. Criterio de cada feature: [`feature_list.json`](feature_list.json). Compuertas globales: [`CHECKPOINTS.md`](CHECKPOINTS.md).

## Ruta rápida para agentes

1. Leer [`progress/current.md`](progress/current.md) y el criterio de la feature en [`feature_list.json`](feature_list.json).
2. Identificar la capa propietaria: Hop para extract/load 1:1; Python para staging RData y reglas de negocio.
3. Revisar [`python/CONTRATO.md`](python/CONTRATO.md) antes de cambiar columnas o destinos.
4. Ejecutar la prueba del criterio; para el flujo diario, usar `./init.sh` y confirmar `HARNESS OK`.
5. Registrar el resultado en `progress/impl_<id>.md` y actualizar `progress/history.md` al cerrar la feature.

Si faltan Oracle, MySQL, SISUD, Hop o credenciales, no inventes resultados: ejecuta la validación local disponible y deja explícito el bloqueo.

## Harness

| Archivo | Propósito |
|---|---|
| [`feature_list.json`](feature_list.json) | Alcance; **una** `in_progress` a la vez |
| [`progress/current.md`](progress/current.md) | Plan de sesión activa |
| [`progress/history.md`](progress/history.md) | Bitácora append-only |
| [`docs/harness/workflow.md`](docs/harness/workflow.md) | Roles líder / implementador / revisor |
| [`docs/harness/platform.md`](docs/harness/platform.md) | Hop, H2, variables |

## Skills


- [`.agents/skills/hop-python-etl/SKILL.md`](.agents/skills/hop-python-etl/SKILL.md) — capas Hop / H2 / Python
- [`.agents/skills/linux-windows-parity/SKILL.md`](.agents/skills/linux-windows-parity/SKILL.md) — usar solo cuando el checkout incluya el espejo Windows correspondiente
- [`.agents/skills/etl-run-logs/SKILL.md`](.agents/skills/etl-run-logs/SKILL.md) — cada corrida deja bitácora en `logs/`
- [`.agents/skills/release-etl/SKILL.md`](.agents/skills/release-etl/SKILL.md) — corta la rama `release` solo con el ETL

## Preferir Apache Hop

**Siempre intentar Hop primero** para extract/load 1:1. Python queda para DDL/staging RData, homologación y reglas de negocio en `logica/`.

| Workflow | Rol |
|---|---|
| [`wf_create_stg.hwf`](workflows/wf_create_stg.hwf) | **Bajo demanda:** DDL STG/DW + carga backup RData → `DW_INF_CONSOL_RDATA`. Primera vez, falten tablas, o cambien `.RData`. |
| [`wf_main.hwf`](workflows/wf_main.hwf) | **Diario:** solo FORM + CSEP (Hop truncate). |

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
.\init.bat                # diario FORM+CSEP
```

## Verificación

`init.sh` / `init.bat` → **HARNESS OK** diario:

1. `DW_INF_CONSOL_FORM` — Hop `pl_form_informes` → **oracle_dw + mysql_dw**, luego conteo `PK_OFICINA` en MySQL DW
2. `DW_INF_CSEP_INFORMES_VIEW` — Hop `pl_csep_informes` → **oracle_dw + mysql_dw**

`DW_INF_CONSOL_RDATA` (incluido el cruce `PK_OFICINA`) se refresca solo con `wf_create_stg.hwf`. **HARNESS OK no lo cubre.**

Requiere **hop-run**, Oracle DW, **MySQL HEC** (`mysql`), **MySQL DW** (`mysql_dw`) y SISUD vivos. RData/H2/Rscript solo para `wf_create_stg*`.

## Reglas críticas

1. **Un solo `.py`** en `logica/` — solo reglas post-STG RData.
2. **Sin secretos** en git.
3. **Sin `${VAR}` literal** en logs Hop.
4. `logica/` no abre conexiones. Homologación RData en `python/rdata/` + `python/stage/stage_rdata.py`.
5. No `import io` (stdlib).
6. Destinos **oracle_dw** y **mysql_dw**: **TRUNCATE** en carga; CREATE si faltan → `ensure_dw_tables` en `wf_create_stg*`.
7. FORM/CSEP → pipelines Hop (copy a ambos destinos). Fuente HEC ≠ `mysql_dw`.
8. Cambio de alcance: ítem en `feature_list.json` (criterio + `progress/impl_<id>.md`) en el mismo trabajo. El criterio de esa lista es la prueba; [`CHECKPOINTS.md`](CHECKPOINTS.md) solo fija compuertas globales.
9. Cada corrida debe dejar log en `logs/`; aplicar [`etl-run-logs`](.agents/skills/etl-run-logs/SKILL.md) al tocar scripts de ejecución o workflows.

## Orden de ejecución

### Primera vez / cuando cambien los `.RData`

Play **`wf_create_stg.hwf`**:

1. Reset H2  
2. CREATE `STG_*`  
3. CREATE `DW_INF_*` si faltan (**Oracle + MySQL DW**)  
4. Stage RData → H2  
5. Python → `DW_INF_CONSOL_RDATA` (**oracle_dw + mysql_dw**)

### Todos los días

Play **`wf_main.hwf`** (o `./init.sh` / `init.bat`):

1. Hop FORM → `DW_INF_CONSOL_FORM` (Oracle + MySQL DW)  
2. Hop CSEP → `DW_INF_CSEP_INFORMES_VIEW` (Oracle + MySQL DW)

| Entorno | Bajo demanda | Diario |
|---|---|---|
| Checkout actual | `wf_create_stg.hwf` | `wf_main.hwf` / `init.sh` / `init.bat` |
