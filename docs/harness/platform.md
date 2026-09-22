# Plataforma y ejecución (cascarón)

Divulgación progresiva desde [`AGENTS.md`](../../AGENTS.md).

## Linux

- Apache Hop en `~/apps/hop` (GUI: `~/apps/hop/hop-gui.sh`).
- Java en PATH (H2).
- Python: `.venv/` + `python/requirements.txt`.

## Preferir Apache Hop

Intentar siempre cargas 1:1 con pipelines Hop. Python solo para post-staging / casos que Hop no resuelve limpio.

## Workflows

| Workflow | Uso |
|---|---|
| `workflows/wf_create_stg.hwf` | **Diseño:** crea tablas `STG_*` en H2; deja H2 vivo en 9092 para mapear. No es la corrida habitual. |
| `workflows/wf_main.hwf` | **Corrida habitual:** se ejecuta siempre; STG ya definido por create_stg/`inputs.yaml`; stage + lógica + FORM/CSEP Hop. |

DDL Oracle DW una vez: [`sql/dw/`](../../sql/dw/). En corrida solo TRUNCATE.

Smoke (requiere hop-run + `sql/dw/` precreado):

```bash
./switch-env.sh local
./init.sh
```

## Capa de lógica

- Un solo `.py` en `logica/` (demo: `demo.py`).
- Entrada: DataFrames `LECTURAS` (`python/io/leer_h2.py`).
- Contrato: [`python/CONTRATO.md`](../../python/CONTRATO.md).

## H2

- BD in-memory `mem:csep`, TCP `9092`, modo Oracle.
- Reset: `h2/scripts/reset_and_create.sh` → `00_reset.sql` + `01_schema.sql`.
- **Gotcha:** `start_h2.sh` debe usar `nohup` y redirigir stdout; si no, Hop se queda colgado en Reset.

## Variables

- Fuente única: `project-config.json` → `config.variables`.
- Entorno: `./switch-env.sh local|remote` (copia `environments/*.json`).
- `${VAR}` literal en log = variable no definida o proyecto Hop equivocado.

## Secretos

No commitear `project-config.json` ni `client_secret.json`. En `environments/` solo placeholders `<...>`.
