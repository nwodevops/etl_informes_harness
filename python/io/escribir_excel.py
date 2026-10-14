"""SALIDA: DataFrame(s) -> Excel en output/."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

_SHEET_MAX = 31
_ILLEGAL_XML = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _clean_cell(v):
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, (bytes, bytearray)):
        v = v.decode("utf-8", errors="replace")
    if not isinstance(v, str):
        return v
    # openpyxl rechaza controles XML 1.0 (incl. \\x02 en textos HECHO_VERIF)
    return _ILLEGAL_XML.sub("", v)


def _sanitize_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        out[col] = out[col].map(_clean_cell)
    return out


def escribir_excel(df: pd.DataFrame, root: Path, *, nombre: str = "resultado.xlsx") -> Path:
    out_dir = root / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / nombre
    # Muestra acotada: 101k x 50 tumba openpyxl y arrastra controles ilegales
    to_write = _sanitize_df(df.head(5000))
    to_write.to_excel(path, index=False, engine="openpyxl")
    print(
        f"Excel: {len(to_write)} filas (muestra de {len(df)}) x {len(to_write.columns)} "
        f"columnas -> {path.relative_to(root)}"
    )
    return path


def _sheet_name(name: str) -> str:
    clean = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in str(name))
    return (clean or "HOJA")[:_SHEET_MAX]


def escribir_libro(
    hojas: dict[str, pd.DataFrame],
    root: Path,
    *,
    nombre: str = "fase1.xlsx",
) -> Path:
    """Escribe un xlsx con una hoja por DataFrame. Nombres de hoja <= 31 chars."""
    if not hojas:
        raise ValueError("escribir_libro: no hay hojas")
    out_dir = root / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / nombre
    usados: set[str] = set()
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for raw, df in hojas.items():
            sheet = _sheet_name(raw)
            base = sheet
            n = 1
            while sheet in usados:
                suf = f"_{n}"
                sheet = (base[: _SHEET_MAX - len(suf)] + suf)
                n += 1
            usados.add(sheet)
            _sanitize_df(df).to_excel(writer, sheet_name=sheet, index=False)
            print(f"Excel[{sheet}]: {len(df)} x {len(df.columns)}")
    print(f"Excel: {len(hojas)} hojas -> {path.relative_to(root)}")
    return path
