#!/usr/bin/env python3
"""Compuerta diaria: DW_INF_CONSOL_FORM en mysql_dw tiene PK_OFICINA poblada.

Lo llama init.sh / init.bat después de pl_form. No cubre RData (wf_create_stg).
"""

from __future__ import annotations

import sys
from pathlib import Path

_PY = Path(__file__).resolve().parent
if str(_PY) not in sys.path:
    sys.path.insert(0, str(_PY))

from core.config import load_vars, project_root, require_live_conn  # noqa: E402


def main() -> int:
    root = project_root()
    cv = require_live_conn("mysql_dw", load_vars(root))
    try:
        import pymysql
    except ImportError as exc:
        print("FAIL: falta pymysql", file=sys.stderr)
        raise SystemExit(1) from exc
    port = int(cv["port"]) if str(cv["port"]).isdigit() else 3306
    conn = pymysql.connect(
        host=cv["host"],
        port=port,
        user=cv["username"],
        password=cv["password"],
        database=cv["database"],
        charset="utf8mb4",
    )
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = 'DW_INF_CONSOL_FORM'
              AND column_name = 'PK_OFICINA'
            """
        )
        if int(cur.fetchone()[0]) != 1:
            print("FAIL: DW_INF_CONSOL_FORM sin columna PK_OFICINA", file=sys.stderr)
            return 1
        cur.execute("SELECT COUNT(*) FROM DW_INF_CONSOL_FORM")
        n = int(cur.fetchone()[0])
        cur.execute(
            """
            SELECT COUNT(*) FROM DW_INF_CONSOL_FORM
            WHERE PK_OFICINA IS NOT NULL AND TRIM(PK_OFICINA) <> ''
            """
        )
        pk = int(cur.fetchone()[0])
        print(f"FORM PK_OFICINA: {pk}/{n} @ {cv['host']}:{cv['port']}/{cv['database']}")
        cur.execute(
            """
            SELECT PK_OFICINA, COUNT(*) FROM DW_INF_CONSOL_FORM
            GROUP BY PK_OFICINA ORDER BY 2 DESC
            """
        )
        for code, cnt in cur.fetchall():
            print(f"  {code}: {cnt}")
        if n and pk == 0:
            print(
                "FAIL: FORM tiene filas y ninguna PK_OFICINA",
                file=sys.stderr,
            )
            return 1
        cur.close()
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
