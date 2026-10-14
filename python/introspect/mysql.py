"""Introspección MySQL HEC: esquema canónico fijo (mismo CANONICAL que RData).

No extrae filas; valida que exista el SQL referenciado en inputs.yaml.
"""

from __future__ import annotations

from pathlib import Path

from rdata.schema import CANONICAL

from .h2_ddl import Column


def introspect(source: dict, variables: dict[str, str], root: Path | None = None) -> list[Column]:
    del variables  # schema fijo
    if root is None:
        raise ValueError("mysql: falta root del proyecto")

    raw_sql = (source.get("sql_path") or "").strip()
    if not raw_sql:
        raise ValueError("mysql: falta sql_path en inputs.yaml")
    path = Path(raw_sql)
    if not path.is_absolute():
        path = (root / path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"SQL MySQL no encontrado: {path}")

    return [Column(name=n, h2_type=h2) for n, h2, _ora in CANONICAL]
