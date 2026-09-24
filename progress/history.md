# Bitácora harness (append-only)

---

## Plantilla

Al cerrar una feature, append aquí: fecha, id, resumen, evidencia (`progress/impl_<id>.md`).

---

## 2026-09-18 — fase-2-rdata-stg + fase-3-oracle-consol

- 14 RData (BD+OD 2019–2025) → mapa canónico → `STG_INF_CONSOL` → `APP.DW_INF_CONSOL_RDATA`
- Evidencia: `progress/impl_fase-3-oracle-consol.md`
- Conteo: **101749** filas Oracle = suma RData; desglose FUENTE/ANIO OK

---

## 2026-09-18 — fase-4-schema-gradual-2026

- Estructura gradual anclada a esquema 2025/2026 (+30 cols, `MES_CORTE`)
- Incluye Agosto 2026; histórico con NULL en extras nuevas
- Evidencia: `progress/impl_fase-4-schema-gradual-2026.md`
- Oracle: **111091** filas × **80** cols (BD+OD 2019–2026)

---

## 2026-09-18 — fase-5-union-vigente-2026

- Unión vigente: +`ESTADO`, `ANALISTA_LEGAL`, `RESPONSABLE_COMISION`
- Fuera: `N°` / `USUARIO` / `FECHA_REGISTRO` / `INF_EVAL*`
- Evidencia: `progress/impl_fase-5-union-vigente-2026.md`
- Oracle: **111091** filas × **83** cols; `./init.sh` → HARNESS OK

---

## 2026-09-21 — fase-6-mysql-form

- MySQL HEC SQL → `STG_INF_CONSOL_FORM` → `APP.DW_INF_CONSOL_FORM` (paralelo a RData)
- Evidencia: `progress/impl_fase-6-mysql-form.md`
- Oracle FORM: **17** filas (BD 15 + OD 2); RData sigue **111091**; `./init.sh` → HARNESS OK

---

## 2026-09-22 — fase-7-hop-csep-informes

- Hop: vista `CSEP_INFORMES_VIEW` → tabla `DW_INF_CSEP_INFORMES_VIEW` (`wf_main` + `ddl_csep_informes.py`)
- Evidencia: `progress/impl_fase-7-hop-csep-informes.md`
- Independiente de `init.sh` / `wf_main`

---

## 2026-09-22 — hop-canonico-form-csep

- FORM/CSEP canónicos en Hop (`pl_form_informes`, `pl_csep_informes`); hard-fail; TRUNCATE
- Eliminado Python `stage_mysql` / `csep/`; `escribir_oracle` solo TRUNCATE; DDL en `sql/dw/`
- `init.sh`/`init.bat`: hop-run pl_form + pl_csep tras RData
- Evidencia: plan Hop FORM CSEP

## 2026-09-22 — rdata bajo demanda

- RData (backup) solo en `wf_create_stg*`; `wf_main*` / `init` diario = FORM + CSEP Hop
- DATE MySQL: NULL en vez de `--` para pl_form (ORA-01858)

## 2026-09-24 — fase-8-mysql-dw-mirror

- Dual-write `DW_INF_*` a `oracle_dw` + `mysql_dw` (`DB_MYSQL_DW_*`; ≠ fuente HEC)
- Hop copy FORM/CSEP; RDATA `escribir_mysql` vía `main.py`; ensure CREATE MySQL
- Evidencia: `progress/impl_fase-8-mysql-dw-mirror.md`; init HARNESS OK (FORM 19 + CSEP 53288 en MySQL)
