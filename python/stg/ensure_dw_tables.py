#!/usr/bin/env python3
"""Asegura tablas DW en oracle_dw (CREATE si no existen; nunca DROP).

Lo llama wf_create_stg (diseño) antes de mapear / de la primera corrida.
Runtime (wf_main) solo TRUNCATE+INSERT.

  DW_INF_CONSOL_RDATA / DW_INF_CONSOL_FORM — DDL desde rdata.schema
  DW_INF_CSEP_INFORMES_VIEW — columnas de CSEP_INFORMES_VIEW (oracle_sisud)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_PY = Path(__file__).resolve().parents[1]
if str(_PY) not in sys.path:
    sys.path.insert(0, str(_PY))

from core.config import load_vars, project_root, require_live_conn  # noqa: E402
from rdata.schema import oracle_comment_statements, oracle_ddl  # noqa: E402

ESQUEMA = "APP"
TABLE_RDATA = "DW_INF_CONSOL_RDATA"
TABLE_FORM = "DW_INF_CONSOL_FORM"
TABLE_CSEP = "DW_INF_CSEP_INFORMES_VIEW"
SRC_VIEW = "CSEP_INFORMES_VIEW"


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


def _table_exists(cur, table: str) -> bool:
    cur.execute(
        "SELECT COUNT(*) FROM user_tables WHERE table_name = :1",
        [table.upper()],
    )
    return int(cur.fetchone()[0]) > 0


def _user_tablespace(cur) -> str:
    cur.execute(
        """
        SELECT tablespace_name FROM user_ts_quotas
        WHERE max_bytes = -1 OR bytes > 0
        ORDER BY CASE WHEN tablespace_name = 'USERS' THEN 0 ELSE 1 END, tablespace_name
        """
    )
    rows = [r[0] for r in cur.fetchall()]
    return rows[0] if rows else "USERS"


def _ensure_canonical(cur, schema: str, table: str, ts: str) -> str:
    if _table_exists(cur, table):
        return "exists"
    ddl = oracle_ddl(schema, table).rstrip() + f" TABLESPACE {ts}"
    cur.execute(ddl)
    for stmt in oracle_comment_statements(schema, table):
        cur.execute(stmt)
    return "created"


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
        return data_type
    if dt in ("CLOB", "NCLOB", "BLOB", "XMLTYPE", "LONG", "RAW"):
        if dt == "RAW" and data_length:
            return f"RAW({int(data_length)})"
        return dt
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
    return [r for r in rows if r[0] == owner0]


def _build_csep_ddl(cols: list[tuple], table: str, ts: str) -> str:
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
    return f"CREATE TABLE {table} (\n{body}\n) TABLESPACE {ts}"


def _ensure_csep(variables: dict[str, str]) -> str:
    dst, dst_cv = _connect("oracle_dw", variables)
    try:
        cur = dst.cursor()
        if _table_exists(cur, TABLE_CSEP):
            cur.close()
            return "exists"
        ts = _user_tablespace(cur)
        src, src_cv = _connect("oracle_sisud", variables)
        try:
            scur = src.cursor()
            cols = _fetch_view_columns(scur, SRC_VIEW)
            scur.close()
        finally:
            src.close()
        ddl = _build_csep_ddl(cols, TABLE_CSEP, ts)
        cur.execute(ddl)
        dst.commit()
        print(
            f"DW: CREATE {TABLE_CSEP} ({len(cols)} cols desde {SRC_VIEW}) "
            f"@ {dst_cv['host']}:{dst_cv['port']}/{dst_cv['database']}",
            flush=True,
        )
        cur.close()
        return "created"
    finally:
        dst.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="CREATE tablas DW en oracle_dw si no existen (sin DROP)"
    )
    parser.add_argument("--root", default=None)
    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root else project_root()
    variables = load_vars(root)

    conn, cv = _connect("oracle_dw", variables)
    try:
        cur = conn.cursor()
        cur.execute("SELECT USER FROM DUAL")
        schema = str(cur.fetchone()[0])
        if schema.upper() != ESQUEMA:
            print(f"DW: esquema sesión = {schema} (esperado {ESQUEMA})", flush=True)
        ts = _user_tablespace(cur)
        for table in (TABLE_RDATA, TABLE_FORM):
            status = _ensure_canonical(cur, schema, table, ts)
            if status == "created":
                conn.commit()
                print(
                    f"DW: CREATE {schema}.{table} "
                    f"@ {cv['host']}:{cv['port']}/{cv['database']}",
                    flush=True,
                )
            else:
                print(f"DW: {schema}.{table} ya existe (ok)", flush=True)
        cur.close()
    finally:
        conn.close()

    try:
        status = _ensure_csep(variables)
        if status == "exists":
            print(f"DW: {TABLE_CSEP} ya existe (ok)", flush=True)
    except Exception as exc:
        print(
            f"ERROR: no se pudo asegurar {TABLE_CSEP} ({exc}). "
            f"Revisa oracle_sisud / grants o crea manualmente sql/dw/03_*.sql",
            file=sys.stderr,
        )
        return 1

    print("DW: tablas destino listas (CREATE solo si faltaban).", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError, KeyError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
