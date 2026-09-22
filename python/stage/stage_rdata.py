#!/usr/bin/env python3
"""Carga .RData → STG_INF_CONSOL (extract + homologación de columnas).

Capa python/ STG: lee R vía Rscript, aplica rdata.map, inserta H2.
Requieren H2 vivo y DDL (create_stg.py). Reglas post-STG → logica/.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
_PY = HERE.parent
if str(_PY) not in sys.path:
    sys.path.insert(0, str(_PY))

from core.config import load_sources, load_vars, project_root  # noqa: E402
from core.h2_conn import connect_h2  # noqa: E402
from rdata.map import (  # noqa: E402
    map_to_canonical,
    parse_anio_from_name,
    parse_fuente_from_name,
    parse_mes_corte_from_name,
)
from rdata.schema import CANONICAL_NAMES, DATE_COLS  # noqa: E402

STG_DEFAULT = "STG_INF_CONSOL"

_R_EXPORT = r"""
args <- commandArgs(trailingOnly = TRUE)
path <- args[[1]]
out  <- args[[2]]
e <- new.env()
load(path, envir = e)
nms <- ls(e)
if (length(nms) < 1) stop("RData sin objetos: ", path)
obj_name <- nms[[1]]
x <- e[[obj_name]]
if (!is.data.frame(x)) stop("Objeto no es data.frame: ", obj_name)
for (cn in names(x)) {
  col <- x[[cn]]
  if (inherits(col, "POSIXt") || inherits(col, "Date")) {
    x[[cn]] <- format(col, "%Y-%m-%d %H:%M:%S")
  } else if (is.factor(col)) {
    x[[cn]] <- as.character(col)
  } else if (is.logical(col)) {
    x[[cn]] <- ifelse(is.na(col), NA_character_, ifelse(col, "TRUE", "FALSE"))
  }
}
writeLines(obj_name, paste0(out, ".obj"))
utils::write.csv(x, out, row.names = FALSE, na = "", fileEncoding = "UTF-8")
"""


def _rscript_available() -> bool:
    try:
        subprocess.run(
            ["Rscript", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _load_rdata_via_r(path: Path) -> tuple[pd.DataFrame, str]:
    """Devuelve (DataFrame, nombre_objeto_R)."""
    with tempfile.TemporaryDirectory(prefix="rdata_") as tmp:
        tmp_path = Path(tmp)
        csv_path = tmp_path / "export.csv"
        script_path = tmp_path / "export.R"
        script_path.write_text(_R_EXPORT, encoding="utf-8")
        proc = subprocess.run(
            ["Rscript", str(script_path), str(path), str(csv_path)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"Rscript falló en {path.name}: {proc.stderr.strip() or proc.stdout.strip()}"
            )
        obj_name = (tmp_path / "export.csv.obj").read_text(encoding="utf-8").strip()
        df = pd.read_csv(csv_path, dtype=str, keep_default_na=True)
        return df, obj_name


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


def load_all_mapped(rdata_dir: Path, pattern: str = "*.RData") -> pd.DataFrame:
    files = sorted(rdata_dir.glob(pattern))
    if not files:
        raise FileNotFoundError(f"Sin {pattern} en {rdata_dir}")
    frames: list[pd.DataFrame] = []
    for path in files:
        fuente = parse_fuente_from_name(path.name)
        anio = parse_anio_from_name(path.name)
        mes = parse_mes_corte_from_name(path.name)
        print(f"Leyendo {path.name} ({fuente}/{anio}/{mes})...", flush=True)
        raw, obj = _load_rdata_via_r(path)
        mapped = map_to_canonical(
            raw,
            fuente=fuente,
            anio=anio,
            archivo=path.name,
            objeto_r=obj,
            mes_corte=mes,
        )
        print(f"  -> {len(mapped)} filas, objeto={obj}", flush=True)
        frames.append(mapped)
    out = pd.concat(frames, ignore_index=True)
    return out[CANONICAL_NAMES]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RData → STG_INF_CONSOL")
    parser.add_argument("--root", default=None)
    args = parser.parse_args(argv)

    if not _rscript_available():
        raise SystemExit("Rscript no está en PATH (necesario para leer .RData)")

    root = Path(args.root).resolve() if args.root else project_root()
    variables = load_vars(root)
    sources = load_sources(root, variables)
    rdata_srcs = [s for s in sources if s.get("type") == "rdata"]
    if not rdata_srcs:
        raise SystemExit("inputs.yaml sin sources type=rdata")

    src = rdata_srcs[0]
    stg = str(src.get("stg_table") or STG_DEFAULT).strip().upper()
    raw_path = (src.get("path") or "input/input_rdata").strip()
    path = Path(raw_path)
    if not path.is_absolute():
        path = (root / path).resolve()
    pattern = (src.get("glob") or "*.RData").strip()

    df = load_all_mapped(path, pattern)
    print(f"Total consolidado: {len(df)} filas x {len(df.columns)} cols", flush=True)

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
