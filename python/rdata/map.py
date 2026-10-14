"""Homologación RData → columnas canónicas (adapter de staging).

Capa: python/ — usado por stage_rdata.py al aterrizar en STG_INF_CONSOL.
No abre conexiones. Reglas post-STG (QA, KPIs) van en logica/.
"""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

from rdata.schema import (
    CANONICAL_NAMES,
    CORE,
    DATE_COLS,
    EXTRAS_BD,
    EXTRAS_EQUIV,
    NUMBER_COLS,
)

# Copia directa si el nombre fuente (normalizado) == canónica
DIRECT_COLS = (
    {c[0] for c in CORE}
    | {c[0] for c in EXTRAS_BD}
    | {c[0] for c in EXTRAS_EQUIV}
) - {"RECOMENDACION_MEDIDAS_ADMIN"}  # solo vía EQUIV
# Claves de EQUIV se saltan en el bucle directo; IDUF_SIG se copia.

# TODO /step 4 — nombres distintos, un solo campo. Primer valor lleno gana.
# Tabla: docs/equivalencias_sede_od.md
# ID_ADMINISTRADO e ID_UF dependen de la fuente (EQUIV_POR_FUENTE).
EQUIV: dict[str, list[str]] = {
    "ADMIN": ["ADMIN", "ADMINISTRADO_INAPS", "TXADMINISTRADO_ADM"],
    "UF": ["UF", "UF_INAPS", "TXUNIDAD"],
    "RECOM_ACCION": ["RECOM_INAPS", "RECOM_MA", "RECOM_MEDIDAS"],
    "SECTOR_O_SUBSECTOR": ["SECTOR", "SUBSECTOR", "TXSUBSECTOR_UND"],
    "TXCOORDINACION": ["TXCOORDINACION", "COORDINACION"],
    "TIPOACCION_INAPS": ["TIPOACCION_INAPS", "TXACCION"],
    "TIPOSUP_INAPS": ["TIPOSUP_INAPS", "TXTIPSUP"],
    "EXPEDIENTE": ["EXPEDIENTE", "TXNUMEXP"],
    "RECOMENDACION_MEDIDAS_ADMIN": [
        "RECOM_MA",
        "RECOMENDACIÓN_MEDIDAS",
        "RECOM_MEDIDAS",
        "RECOM_MEDIDA",
    ],
}

# Sede (BD) y OD no comparten el orden de estos dos campos.
# UNK usa la lista de sede. El SUR de la columna fuente ID_UF no entra.
EQUIV_POR_FUENTE: dict[str, dict[str, list[str]]] = {
    "BD": {
        "ID_ADMINISTRADO": [
            "IDADMINISTRADO_REV",
            "IDADMIN",
            "IDAMIN",
            "ID_ADMIN",
            "IDADMINISTRADO",
        ],
        "ID_UF": ["ID_UF_UNIDAD_REV", "IDUF_SIG"],
    },
    "OD": {
        "ID_ADMINISTRADO": ["IDADMIN", "IDADMINISTRADO"],
        "ID_UF": ["IDUF_REV", "IDUF_SIG"],
    },
}

_CR_RE = re.compile(r"[\r\n]+")
_YEAR_RE = re.compile(r"(20\d{2})")
_MES_RE = re.compile(
    r"(ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|JULIO|AGOSTO|SEPTIEMBRE|SETIEMBRE|"
    r"OCTUBRE|NOVIEMBRE|DICIEMBRE)",
    re.IGNORECASE,
)


def normalize_colname(name: Any) -> str:
    s = "" if name is None else str(name)
    s = _CR_RE.sub("", s).strip()
    s = re.sub(r"[^A-Za-z0-9_ÁÉÍÓÚÑáéíóúñ°º]", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if s.upper() in {"N", "N_"}:
        s = "N_ORD"
    return s.upper()


def normalize_frame_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    used: dict[str, int] = {}
    new_cols: list[str] = []
    for c in out.columns:
        base = normalize_colname(c)
        if base in used:
            used[base] += 1
            base = f"{base}_{used[base]}"
        else:
            used[base] = 1
        new_cols.append(base)
    out.columns = new_cols
    return out


def parse_anio_from_name(filename: str) -> int | None:
    m = _YEAR_RE.search(filename)
    return int(m.group(1)) if m else None


def parse_mes_corte_from_name(filename: str) -> str | None:
    m = _MES_RE.search(filename)
    if not m:
        return None
    mes = m.group(1).upper()
    if mes == "SETIEMBRE":
        return "SEPTIEMBRE"
    return mes


def parse_fuente_from_name(filename: str) -> str:
    u = filename.upper()
    if u.startswith("BDINF"):
        return "BD"
    if u.startswith("ODINF"):
        return "OD"
    return "UNK"


def _coalesce_series(df: pd.DataFrame, sources: list[str], n: int) -> pd.Series:
    present = [s for s in sources if s in df.columns]
    if not present:
        return pd.Series([pd.NA] * n)
    out = df[present[0]].copy()
    for s in present[1:]:
        empty = out.isna()
        if out.dtype == object or str(out.dtype) == "string":
            empty = empty | out.astype(str).str.strip().isin(["", "nan", "None", "<NA>"])
        out = out.where(~empty, df[s])
    return out


def _to_nullable_number(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def _to_datetime(s: pd.Series) -> pd.Series:
    """ISO (export R) primero; resto con dayfirst (fechas PE dd/mm)."""
    parsed = pd.to_datetime(s, errors="coerce", format="ISO8601")
    miss = parsed.isna() & s.notna() & (s.astype(str).str.strip() != "")
    if miss.any():
        with pd.option_context("mode.chained_assignment", None):
            parsed = parsed.copy()
            parsed.loc[miss] = pd.to_datetime(
                s.loc[miss], errors="coerce", dayfirst=True
            )
    return parsed


def map_to_canonical(
    df: pd.DataFrame,
    *,
    fuente: str,
    anio: int | None,
    archivo: str,
    objeto_r: str,
    mes_corte: str | None = None,
) -> pd.DataFrame:
    """Adapter staging: data.frame R → forma canónica STG (sin QA de negocio)."""
    # TODO /step 2 — unificar el nombre (espacio → _). SEDE y OD quedan comparables.
    raw = normalize_frame_columns(df)
    n = len(raw)
    data: dict[str, Any] = {
        "FUENTE": [fuente] * n,
        "ANIO": [anio] * n,
        "MES_CORTE": [mes_corte] * n,
        "ARCHIVO": [archivo] * n,
        "OBJETO_R": [objeto_r] * n,
    }

    # TODO /step 3 — mismo nombre en SEDE y OD: copia directa.
    # Si la columna no está en ese archivo, queda vacía (solo sede o solo OD).
    # TODO /step 3 — IDUF_SIG no es clave de EQUIV: también se copia aquí.
    for col in DIRECT_COLS:
        if col in EQUIV:
            continue
        if col in raw.columns:
            data[col] = raw[col]
        else:
            data[col] = pd.Series([pd.NA] * n)

    # TODO /step 4 — aplicar la tabla EQUIV. ID_ADMINISTRADO e ID_UF según fuente.
    equiv = dict(EQUIV)
    equiv.update(EQUIV_POR_FUENTE.get(fuente, EQUIV_POR_FUENTE["BD"]))
    for canon, sources in equiv.items():
        data[canon] = _coalesce_series(raw, sources, n)

    out = pd.DataFrame(data)
    for name in CANONICAL_NAMES:
        if name not in out.columns:
            out[name] = pd.NA

    out = out[CANONICAL_NAMES]

    for c in DATE_COLS:
        out[c] = _to_datetime(out[c])
    for c in NUMBER_COLS:
        out[c] = _to_nullable_number(out[c])

    # FG_SIN_INFORME lo calcula logica/ (post-STG)
    return out
