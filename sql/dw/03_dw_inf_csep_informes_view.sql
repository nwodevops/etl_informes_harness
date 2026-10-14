-- Crear una vez en oracle_dw (usuario APP / REPOCSEP).
-- Preferible: crear desde metadatos de la vista en SISUD (mismas columnas/tipos).
-- Opción A (desde sesión con grant SELECT a la vista fuente):
--
--   CREATE TABLE DW_INF_CSEP_INFORMES_VIEW AS
--   SELECT * FROM CSEP_INFORMES_VIEW WHERE 1 = 0;
--
-- Opción B: DBA exporta DDL de CSEP_INFORMES_VIEW y adapta a tabla.
--
-- Runtime: Hop pl_csep_informes (TRUNCATE + INSERT). Sin DROP en corrida.
--
-- Placeholder (solo si aún no hay acceso a la vista; reemplazar antes de producción):
CREATE TABLE DW_INF_CSEP_INFORMES_VIEW (
  _ETL_PLACEHOLDER VARCHAR2(4000)
);
