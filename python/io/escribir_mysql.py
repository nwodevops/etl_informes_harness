"""SALIDA: DataFrame → mysql_dw.<tabla> (mirror DW).

Full refresh: TRUNCATE + INSERT. La tabla debe existir (ensure_dw_tables / sql/dw/mysql/).
Tabla típica: DW_INF_CONSOL_RDATA.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from core.config import load_vars, project_root, require_live_conn
from rdata.schema import CLOB_COLS, DATE_COLS, NUMBER_COLS

TABLE_DEFAULT = "DW_INF_CONSOL_RDATA"


def _connect(root: Path):
    variables = load_vars(root)
    cv = require_live_conn("mysql_dw", variables)
    try:
        import pymysql
    except ImportError as exc:
        raise SystemExit(
            "Falta pymysql. Instala: pip install -r python/requirements.txt"
        ) from exc
    port = int(cv["port"]) if str(cv["port"]).isdigit() else 3306
    conn = pymysql.connect(
        host=cv["host"],
        port=port,
        user=cv["username"],
        password=cv["password"],
        database=cv["database"],
        charset="utf8mb4",
        autocommit=False,
    )
    return conn, cv


def _table_exists(cur, table: str) -> bool:
    cur.execute(
        """
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = DATABASE() AND table_name = %s
        """,
        (table,),
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
    return _trunc_varchar(s, 2000)


def escribir_mysql(
    df: pd.DataFrame,
    root: Path | None = None,
    table: str = TABLE_DEFAULT,
) -> int:
    """TRUNCATE + INSERT `<table>` en mysql_dw. Falla si la tabla no existe."""
    root = root or project_root()
    if df is None:
        raise ValueError("escribir_mysql: df es None")
    table = str(table).strip()
    if not table:
        raise ValueError("escribir_mysql: table vacío")

    conn, cv = _connect(root)
    try:
        cur = conn.cursor()
        if not _table_exists(cur, table):
            raise RuntimeError(
                f"No existe {cv['database']}.{table} en mysql_dw. "
                f"Créala con ensure_dw_tables / sql/dw/mysql/."
            )

        cur.execute(f"TRUNCATE TABLE `{table}`")
        print(f"MySQL DW: TRUNCATE {table}", flush=True)

        cols = list(df.columns)
        if cols and len(df):
            placeholders = ", ".join(["%s"] * len(cols))
            col_sql = ", ".join(f"`{c}`" for c in cols)
            sql = f"INSERT INTO `{table}` ({col_sql}) VALUES ({placeholders})"

            rows = []
            for tup in df.itertuples(index=False, name=None):
                rows.append(tuple(_coerce(v, c) for c, v in zip(cols, tup)))

            if rows:
                cur.executemany(sql, rows)
        conn.commit()

        cur.execute(f"SELECT COUNT(*) FROM `{table}`")
        n_bd = int(cur.fetchone()[0])
        print(
            f"MySQL DW: {cv['database']}.{table} = {n_bd} filas "
            f"(df={len(df)}) @ {cv['host']}:{cv['port']}/{cv['database']}",
            flush=True,
        )
        if n_bd != len(df):
            raise RuntimeError(
                f"Conteo MySQL {n_bd} != DataFrame {len(df)} — carga incompleta"
            )

        if n_bd and cols and "FUENTE" in cols and "ANIO" in cols:
            cur.execute(
                f"SELECT FUENTE, ANIO, COUNT(*) FROM `{table}` "
                f"GROUP BY FUENTE, ANIO ORDER BY FUENTE, ANIO"
            )
            for fuente, anio, n in cur.fetchall():
                print(f"MySQL DW:   {fuente} {anio}: {n}", flush=True)
        elif n_bd == 0:
            print("MySQL DW:   (tabla vacía)", flush=True)

        cur.close()
        return n_bd
    finally:
        conn.close()
