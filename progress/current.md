# Sesión activa

**Feature:** `fase-12-form-csep-doc-previo` (done)
**Rama:** `feature/mysql-dw-mirror`

`DW_INF_CONSOL_FORM` toma los 6 campos de documento previo y derivación (`TX_DOCUMENTO_PREVIO`, `TX_NUMERO_DOCUMENTO_PREVIO`, `FE_DOCUMENTO_PREVIO`, `FE_REGISTRO_DOCUMENTO_PREVIO`, `TX_OTRO_DOCUMENTO_PREVIO`, `FE_DERIV_DOC_DERIVACION`) desde `DW_INF_CSEP_INFORMES_VIEW` por `TRIM(TXINFORME) = TRIM(TX_NUMINFORME)`. `pl_csep_informes` corre antes de `pl_form_informes`. Ver `progress/impl_fase-12-form-csep-doc-previo.md`.
