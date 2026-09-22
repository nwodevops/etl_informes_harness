#!/usr/bin/env python3
"""DDL destino: DROP+CREATE CSEP_INFORMES desde columnas de CSEP_INFORMES_VIEW.

Hop TableOutput no crea tablas; este script aplica el DDL en oracle_dw.
Las filas las copia pipelines/pl_csep_informes.hpl.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from config import load_vars, project_root, require_live_conn  # noqa: E402

SRC_VIEW = "CSEP_INFORMES_VIEW"
DST_TABLE = "CSEP_INFORMES"
SRC_CONN = "oracle_sisud"
DST_CONN = "oracle_dw"


def _connect(connection: str, variables: dict[str, str]):
    try:
        import oracledb
    except ImportError as exc:
        raise SystemExit(
            "Falta oracledb. Instala: pip install -r python/requirements.txt"
        ) from exc
    try:
        oracledb.init_oracle_client()
    except Exception:
        pass
    cv = require_live_conn(connection, variables)
    port = int(cv["port"]) if str(cv["port"]).isdigit() else 1521
    conn = oracledb.connect(
        user=cv["username"],
        password=cv["password"],
        host=cv["host"],
        port=port,
        service_name=cv["database"],
    )
    return conn, cv


def _ora_col_type(
    data_type: str,
    data_length,
    data_precision,
    data_scale,
    char_length,
) -> str:
    dt = (data_type or "").upper()
    if dt in ("VARCHAR2", "NVARCHAR2", "CHAR", "NCHAR"):
        n = int(char_length or data_length or 4000)
        return f"{dt}({n})"
    if dt == "NUMBER":
        if data_precision is None:
            return "NUMBER"
        p = int(data_precision)
        if data_scale is None:
            return f"NUMBER({p})"
        s = int(data_scale)
        if s == 0:
            return f"NUMBER({p})"
        return f"NUMBER({p},{s})"
    if dt in ("FLOAT", "BINARY_FLOAT", "BINARY_DOUBLE"):
        return dt
    if dt == "DATE":
        return "DATE"
    if dt.startswith("TIMESTAMP"):
        return data_type  # p.ej. TIMESTAMP(6)
    if dt in ("CLOB", "NCLOB", "BLOB", "XMLTYPE", "LONG", "RAW"):
        if dt == "RAW" and data_length:
            return f"RAW({int(data_length)})"
        return dt
    # fallback seguro
    if data_length:
        return f"VARCHAR2({min(int(data_length), 4000)})"
    return "VARCHAR2(4000)"


def _fetch_view_columns(cur, view_name: str) -> list[tuple]:
    cur.execute(
        """
        SELECT OWNER, COLUMN_NAME, DATA_TYPE, DATA_LENGTH,
               DATA_PRECISION, DATA_SCALE, CHAR_LENGTH, NULLABLE, COLUMN_ID
        FROM ALL_TAB_COLUMNS
        WHERE TABLE_NAME = :tname
          AND OWNER IN (USER, 'SISUD', 'CSEPDV')
        ORDER BY
          CASE OWNER
            WHEN USER THEN 0
            WHEN 'SISUD' THEN 1
            ELSE 2
          END,
          COLUMN_ID
        """,
        {"tname": view_name.upper()},
    )
    rows = cur.fetchall()
    if not rows:
        raise ValueError(
            f"No se hallaron columnas de {view_name} "
            f"(¿grant / synonym para el usuario fuente?)"
        )
    owner0 = rows[0][0]
    cols = [r for r in rows if r[0] == owner0]
    return cols


def build_create_sql(cols: list[tuple], table: str) -> str:
    parts: list[str] = []
    for (
        _owner,
        name,
        data_type,
        data_length,
        data_precision,
        data_scale,
        char_length,
        nullable,
        _cid,
    ) in cols:
        typ = _ora_col_type(
            str(data_type), data_length, data_precision, data_scale, char_length
        )
        null_sql = "" if (nullable or "Y") == "Y" else " NOT NULL"
        parts.append(f'  "{name}" {typ}{null_sql}')
    body = ",\n".join(parts)
    return f"CREATE TABLE {table} (\n{body}\n)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=f"DDL {DST_TABLE} desde {SRC_VIEW}"
    )
    parser.add_argument("--root", default=None)
    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root else project_root()
    variables = load_vars(root)

    src, src_cv = _connect(SRC_CONN, variables)
    try:
        cur = src.cursor()
        cols = _fetch_view_columns(cur, SRC_VIEW)
        owner = cols[0][0]
        print(
            f"Fuente: {owner}.{SRC_VIEW} ({len(cols)} cols) "
            f"@ {src_cv['host']}:{src_cv['port']}/{src_cv['database']}",
            flush=True,
        )
        ddl = build_create_sql(cols, DST_TABLE)
        cur.close()
    finally:
        src.close()

    dst, dst_cv = _connect(DST_CONN, variables)
    try:
        cur = dst.cursor()
        cur.execute(
            f"""
            BEGIN
              EXECUTE IMMEDIATE 'DROP TABLE {DST_TABLE} PURGE';
            EXCEPTION
              WHEN OTHERS THEN
                IF SQLCODE != -942 THEN RAISE; END IF;
            END;
            """
        )
        print(f"Destino: DROP {DST_TABLE} (si existía)", flush=True)
        cur.execute(ddl)
        dst.commit()
        print(
            f"Destino: CREATE {DST_TABLE} "
            f"@ {dst_cv['host']}:{dst_cv['port']}/{dst_cv['database']} "
            f"user={dst_cv['username']}",
            flush=True,
        )
        cur.close()
    finally:
        dst.close()

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError, KeyError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as exc:
        # oracledb.OperationalError y similares
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
