# impl_fase-7-hop-csep-informes

## Qué

Copia 1:1 `CSEP_INFORMES_VIEW` (oracle_sisud) → `CSEP_INFORMES` (oracle_dw) vía Hop.

## Piezas

- `environments/local.json`: `DB_ORA_SISUD_*` (localhost:1523/XEPDB1)
- `environments/remote.json`: placeholders; descripciones apuntan a CSEPDV / REPOCSEP (`docs/credenciales/remote.txt`)
- `python/ddl_csep_informes.py`: DROP+CREATE (Hop TableOutput no crea tablas)
- `pipelines/pl_csep_informes.hpl`: TableInput → TableOutput truncate
- `workflows/wf_csep_informes.hwf`: Shell DDL → Pipeline → Success

## Corrida

```bash
./switch-env.sh local
# Hop GUI → wf_csep_informes.hwf
```

No forma parte de `./init.sh`.
