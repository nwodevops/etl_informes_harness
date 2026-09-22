"""SALIDA: DataFrame → APP.<tabla> (DW / oracle_dw).

Full refresh: DROP + CREATE + INSERT. Verifica COUNT(*) post-carga.
Tablas típicas: DW_INF_CONSOL_RDATA, DW_INF_CONSOL_FORM.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from config import load_vars, project_root, require_live_conn
from rdata.schema import (
    CLOB_COLS,
    DATE_COLS,
    NUMBER_COLS,
    oracle_comment_statements,
    oracle_ddl,
)

TABLE_DEFAULT = "DW_INF_CONSOL_RDATA"
ESQUEMA_DEFAULT = "APP"


def _connect(root: Path):
    variables = load_vars(root)
    cv = require_live_conn("oracle_dw", variables)
    try:
        import oracledb
    except ImportError as exc:
        raise SystemExit(
            "Falta oracledb. Instala: pip install -r python/requirements.txt"
        ) from exc
    dsn = oracledb.makedsn(
        cv["host"], int(cv["port"] or "1521"), service_name=cv["database"]
    )
    conn = oracledb.connect(user=cv["username"], password=cv["password"], dsn=dsn)
    return conn, cv


def _bind_schema(cur) -> str:
    cur.execute("SELECT USER FROM DUAL")
    return str(cur.fetchone()[0])


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


def _table_exists(cur, schema: str, table: str) -> bool:
    cur.execute(
        "SELECT COUNT(*) FROM user_tables WHERE table_name = :1",
        [table.upper()],
    )
    return int(cur.fetchone()[0]) > 0


def _trunc_varchar(val: str, limit: int) -> str:
    if len(val.encode("utf-8")) <= limit:
        return val
    cut = val
    while cut and len(cut.encode("utf-8")) > limit:
        cut = cut[:-1]
    return cut


def _coerce(v, col: str):
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, pd.Timestamp):
        v = v.to_pydatetime()
    if col in DATE_COLS:
        if isinstance(v, datetime):
            return v
        try:
            ts = pd.Timestamp(v)
            if pd.isna(ts):
                return None
            return ts.to_pydatetime()
        except Exception:
            return None
    if col in NUMBER_COLS:
        try:
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                return v
            return float(v)
        except (TypeError, ValueError):
            return None
    if col in CLOB_COLS or col == "HECHO_VERIF":
        return None if v is None else str(v)
    s = str(v)
    # Alinear con DDL (VARCHAR2 500/1000/2000); truncar por bytes UTF-8
    return _trunc_varchar(s, 2000)


def escribir_oracle(
    df: pd.DataFrame,
    root: Path | None = None,
    table: str = TABLE_DEFAULT,
) -> int:
    """Wipe+DDL+INSERT APP.<table>. Devuelve filas en BD."""
    root = root or project_root()
    if df is None:
        raise ValueError("escribir_oracle: df es None")
    table = str(table).strip().upper()
    if not table:
        raise ValueError("escribir_oracle: table vacío")

    conn, cv = _connect(root)
    try:
        cur = conn.cursor()
        schema = _bind_schema(cur)
        if schema.upper() != ESQUEMA_DEFAULT.upper():
            print(f"DW: esquema sesión = {schema} (esperado {ESQUEMA_DEFAULT})", flush=True)

        ts = _user_tablespace(cur)
        if _table_exists(cur, schema, table):
            cur.execute(f"DROP TABLE {schema}.{table} PURGE")
            print(f"DW: DROP TABLE {schema}.{table}", flush=True)

        ddl = oracle_ddl(schema, table)
        # inject tablespace before end
        ddl_ts = ddl.rstrip() + f" TABLESPACE {ts}"
        print(f"DW: CREATE {schema}.{table} (TABLESPACE {ts})...", flush=True)
        cur.execute(ddl_ts)

        comment_stmts = oracle_comment_statements(schema, table)
        for stmt in comment_stmts:
            cur.execute(stmt)
        print(
            f"DW: COMMENT ON {schema}.{table} "
            f"({len(comment_stmts) - 1} columnas)",
            flush=True,
        )

        cols = list(df.columns)
        if cols and len(df):
            placeholders = ", ".join([f":{i + 1}" for i in range(len(cols))])
            col_sql = ", ".join(cols)
            sql = f"INSERT INTO {schema}.{table} ({col_sql}) VALUES ({placeholders})"

            rows = []
            for tup in df.itertuples(index=False, name=None):
                rows.append(tuple(_coerce(v, c) for c, v in zip(cols, tup)))

            if rows:
                cur.executemany(sql, rows, batcherrors=False)
        conn.commit()

        cur.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
        n_bd = int(cur.fetchone()[0])
        print(
            f"DW: {schema}.{table} = {n_bd} filas "
            f"(df={len(df)}) @ {cv['host']}:{cv['port']}/{cv['database']}",
            flush=True,
        )
        if n_bd != len(df):
            raise RuntimeError(
                f"Conteo Oracle {n_bd} != DataFrame {len(df)} — carga incompleta"
            )

        # Desglose (tablas canónicas con FUENTE/ANIO)
        if n_bd and cols and "FUENTE" in cols and "ANIO" in cols:
            cur.execute(
                f"SELECT FUENTE, ANIO, COUNT(*) FROM {schema}.{table} "
                f"GROUP BY FUENTE, ANIO ORDER BY FUENTE, ANIO"
            )
            for fuente, anio, n in cur.fetchall():
                print(f"DW:   {fuente} {anio}: {n}", flush=True)
        elif n_bd == 0:
            print(f"DW:   (tabla vacía)", flush=True)

        cur.close()
        return n_bd
    finally:
        conn.close()
