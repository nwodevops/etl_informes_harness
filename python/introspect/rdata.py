"""Introspección RData: esquema canónico fijo (docs/rdata_column_map.md). No extrae filas."""

from __future__ import annotations

from pathlib import Path

from rdata.schema import CANONICAL

from .h2_ddl import Column


def introspect(source: dict, variables: dict[str, str], root: Path | None = None) -> list[Column]:
    del variables  # schema fijo
    if root is None:
        raise ValueError("rdata: falta root del proyecto")

    raw_path = (source.get("path") or "input/input_rdata").strip()
    path = Path(raw_path)
    if not path.is_absolute():
        path = (root / path).resolve()
    if not path.is_dir():
        raise FileNotFoundError(f"Carpeta RData no encontrada: {path}")

    pattern = (source.get("glob") or "*.RData").strip()
    files = sorted(path.glob(pattern))
    if not files:
        raise FileNotFoundError(f"Sin archivos {pattern} en {path}")

    return [Column(name=n, h2_type=h2) for n, h2, _ora in CANONICAL]
