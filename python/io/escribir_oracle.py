"""SALIDA: DataFrame → APP.<tabla> (DW / oracle_dw).

Full refresh: TRUNCATE + INSERT. La tabla debe existir (sql/dw/ una vez).
Tabla típica: DW_INF_CONSOL_RDATA.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from core.config import load_vars, project_root, require_live_conn
from rdata.schema import CLOB_COLS, DATE_COLS, NUMBER_COLS

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


def _table_exists(cur, table: str) -> bool:
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
    return _trunc_varchar(s, 2000)


def escribir_oracle(
    df: pd.DataFrame,
    root: Path | None = None,
    table: str = TABLE_DEFAULT,
) -> int:
    """TRUNCATE + INSERT APP.<table>. Falla si la tabla no existe."""
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

        if not _table_exists(cur, table):
            raise RuntimeError(
                f"No existe {schema}.{table}. "
                f"Créala una vez con sql/dw/ (no se hace DROP+CREATE en corrida)."
            )

        cur.execute(f"TRUNCATE TABLE {schema}.{table}")
        print(f"DW: TRUNCATE {schema}.{table}", flush=True)

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

        if n_bd and cols and "FUENTE" in cols and "ANIO" in cols:
            cur.execute(
                f"SELECT FUENTE, ANIO, COUNT(*) FROM {schema}.{table} "
                f"GROUP BY FUENTE, ANIO ORDER BY FUENTE, ANIO"
            )
            for fuente, anio, n in cur.fetchall():
                print(f"DW:   {fuente} {anio}: {n}", flush=True)
        elif n_bd == 0:
            print("DW:   (tabla vacía)", flush=True)

        cur.close()
        return n_bd
    finally:
        conn.close()
