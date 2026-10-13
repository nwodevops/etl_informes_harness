# impl — fase-12-form-csep-doc-previo

Rama `feature/mysql-dw-mirror`.

- CTE `csep` sobre `DW_INF_CSEP_INFORMES_VIEW` deduplicado 1:1 por `TRIM(TXINFORME)` (`ROW_NUMBER()` priorizando filas con datos poblados y mayor `IDACTIVIDAD`).
- `LEFT JOIN csep ON csep.TXINFORME_KEY = TRIM(i.TX_NUMINFORME) AND csep.rn = 1`.
- Los 6 campos en `DW_INF_CONSOL_FORM` provienen directamente de `csep`:
  - `TX_DOCUMENTO_PREVIO`
  - `TX_NUMERO_DOCUMENTO_PREVIO`
  - `FE_DOCUMENTO_PREVIO`
  - `FE_REGISTRO_DOCUMENTO_PREVIO`
  - `TX_OTRO_DOCUMENTO_PREVIO`
  - `FE_DERIV_DOC_DERIVACION`
- Aplicado en paridad sobre `input/input_mysql/vw_inf_consol_simil.sql` y `pipelines/pl_form_informes.hpl`. Eliminado `create_vw_inf_consol_simil.sql` (DDL de vista en fuente: deprecated, nada lo ejecutaba).
- Orden invertido en `workflows/wf_main.hwf`, `workflows/wf_main_windows.hwf`, `init.sh` e `init.bat`: `pl_csep_informes` se ejecuta antes de `pl_form_informes`.
