#!/usr/bin/env python3
"""MySQL HEC (SQL multi-CTE) → STG_INF_CONSOL_FORM en H2.

Extract en Python (no Hop TableInput). Esquema = CANONICAL de rdata.schema.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from config import (  # noqa: E402
    load_sources,
    load_vars,
    project_root,
    require_live_conn,
)
from h2_conn import connect_h2  # noqa: E402
from rdata.schema import CANONICAL_NAMES, DATE_COLS  # noqa: E402

STG_DEFAULT = "STG_INF_CONSOL_FORM"


def _java_null(v):
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(v, pd.Timestamp):
        return v.to_pydatetime()
    return v


def _insert_h2(conn, table: str, df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    cols = list(df.columns)
    placeholders = ", ".join(["?"] * len(cols))
    col_sql = ", ".join(f'"{c}"' for c in cols)
    sql = f"INSERT INTO {table} ({col_sql}) VALUES ({placeholders})"
    cur = conn.cursor()
    try:
        cur.execute(f"TRUNCATE TABLE {table}")
    except Exception:
        cur.execute(f"DELETE FROM {table}")
    n = 0
    batch: list[tuple] = []
    for row in df.itertuples(index=False, name=None):
        cleaned = []
        for c, v in zip(cols, row):
            v = _java_null(v)
            if v is None:
                cleaned.append(None)
            elif c in DATE_COLS and hasattr(v, "strftime"):
                cleaned.append(v.strftime("%Y-%m-%d %H:%M:%S"))
            else:
                cleaned.append(v)
        batch.append(tuple(cleaned))
        n += 1
        if len(batch) >= 500:
            cur.executemany(sql, batch)
            batch.clear()
    if batch:
        cur.executemany(sql, batch)
    cur.close()
    conn.commit()
    return n


def _connect_mysql(variables: dict[str, str]):
    try:
        import pymysql
    except ImportError as exc:
        raise SystemExit(
            "Falta pymysql. Instala: pip install -r python/requirements.txt"
        ) from exc
    cv = require_live_conn("mysql", variables)
    return pymysql.connect(
        host=cv["host"],
        port=int(cv["port"] or "3306"),
        user=cv["username"],
        password=cv["password"],
        database=cv["database"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.Cursor,
    )


def load_mysql_canonical(sql_path: Path, variables: dict[str, str]) -> pd.DataFrame:
    sql = sql_path.read_text(encoding="utf-8")
    print(f"MySQL: ejecutando {sql_path.name}...", flush=True)
    conn = _connect_mysql(variables)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
        df = pd.DataFrame.from_records(rows, columns=cols)
    finally:
        conn.close()
    # Homologar nombres a CANONICAL (MySQL puede devolver minúsculas)
    rename = {c: str(c).upper() for c in df.columns}
    df = df.rename(columns=rename)
    missing = [c for c in CANONICAL_NAMES if c not in df.columns]
    if missing:
        raise ValueError(
            f"SQL MySQL no trae columnas canónicas: {missing[:10]}"
            + ("..." if len(missing) > 10 else "")
        )
    out = df.reindex(columns=CANONICAL_NAMES)
    # Sentinels del SQL ('--') no son TIMESTAMP válidos en H2
    for c in DATE_COLS:
        s = out[c].astype(str).str.strip()
        bad = s.isin(["", "--", "None", "nan", "NaT", "<NA>"]) | out[c].isna()
        out[c] = pd.to_datetime(out[c], errors="coerce")
        out.loc[bad, c] = pd.NaT
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MySQL → STG_INF_CONSOL_FORM")
    parser.add_argument("--root", default=None)
    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root else project_root()
    variables = load_vars(root)
    sources = load_sources(root, variables)
    mysql_srcs = [s for s in sources if s.get("type") == "mysql"]
    if not mysql_srcs:
        raise SystemExit("inputs.yaml sin sources type=mysql")

    src = mysql_srcs[0]
    stg = str(src.get("stg_table") or STG_DEFAULT).strip().upper()
    raw_sql = (src.get("sql_path") or "").strip()
    if not raw_sql:
        raise SystemExit("mysql source sin sql_path")
    sql_path = Path(raw_sql)
    if not sql_path.is_absolute():
        sql_path = (root / sql_path).resolve()

    df = load_mysql_canonical(sql_path, variables)
    print(f"Total MySQL: {len(df)} filas x {len(df.columns)} cols", flush=True)

    conn = connect_h2(root, variables)
    try:
        n = _insert_h2(conn, stg, df)
        print(f"H2 {stg}: {n} filas insertadas", flush=True)
    finally:
        conn.close()

    if "FUENTE" in df.columns and "ANIO" in df.columns:
        g = df.groupby(["FUENTE", "ANIO"], dropna=False).size().reset_index(name="N")
        for row in g.itertuples(index=False):
            print(f"  {row.FUENTE} {row.ANIO}: {row.N}", flush=True)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, ValueError, KeyError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
