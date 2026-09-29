# CHECKPOINTS

Compuertas globales. El criterio de cada feature está solo en [`feature_list.json`](feature_list.json).

## Global

- [ ] `./init.sh` o `init.bat` termina en **HARNESS OK**
- [ ] Como máximo una feature `in_progress`
- [ ] Un solo `.py` en `logica/`
- [ ] Log Hop sin literales `${VAR}`
- [ ] El ítem de `feature_list.json` y su `progress/impl_<id>.md` se cierran en el mismo trabajo que el cambio

## Qué prueba HARNESS OK

1. Hop `pl_form_informes` y `pl_csep_informes` (Oracle + MySQL DW)
2. `python/check_form_pk.py`: `DW_INF_CONSOL_FORM` en `mysql_dw` tiene `PK_OFICINA` y, si hay filas, al menos una con código

## Qué no prueba

`DW_INF_CONSOL_RDATA` y el cruce de `TXCOORDINACION` en `python/rdata/oficina.py`. Eso corre con `wf_create_stg` / `wf_create_stg_windows`.
