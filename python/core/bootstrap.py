"""Bootstrap: añade python/ al sys.path para imports `core.*`, `rdata.*`, etc.

Los entry points (stg/, stage/, csep/) deben insertar `parents[1]` en sys.path
*antes* de importar este módulo. Uso típico tras el insert:

    from core.bootstrap import ensure_path
    ensure_path()  # idempotente
"""

from __future__ import annotations

import sys
from pathlib import Path


def python_root() -> Path:
    """Directorio python/ (padre de core/)."""
    return Path(__file__).resolve().parent.parent


def ensure_path() -> Path:
    root = python_root()
    s = str(root)
    if s not in sys.path:
        sys.path.insert(0, s)
    return root
