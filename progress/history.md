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

- Hop: `CSEP_INFORMES_VIEW` → `CSEP_INFORMES` (`wf_csep_informes` + `ddl_csep_informes.py`)
- Evidencia: `progress/impl_fase-7-hop-csep-informes.md`
- Independiente de `init.sh` / `wf_main`
