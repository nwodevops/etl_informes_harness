"""Cruce TXCOORDINACION (nombre o sigla) → PK_OFICINA usando T_SEP_OFICINA.

Catálogo vivo: MySQL fuente HEC (`mysql` / DB_MYSQL_*), tabla T_SEP_OFICINA.
Alias externos: python/rdata/oficina_alias.yaml (siglas y nombres).
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd
import yaml

from core.config import load_vars, require_live_conn

_ALIAS_PATH = Path(__file__).with_name("oficina_alias.yaml")


def cargar_alias(path: Path | None = None) -> tuple[dict[str, str], dict[str, list[str]]]:
    """Lee siglas y reglas desde oficina_alias.yaml."""
    alias_path = path or _ALIAS_PATH
    data = yaml.safe_load(alias_path.read_text(encoding="utf-8")) or {}
    siglas = {
        str(k).strip().upper(): str(v).strip()
        for k, v in (data.get("siglas") or {}).items()
        if v is not None and str(v).strip()
    }
    reglas: dict[str, list[str]] = {}
    for k, v in (data.get("reglas") or {}).items():
        code = str(k).strip().upper()
        if isinstance(v, str):
            nombres = [v]
        else:
            nombres = [str(x) for x in (v or [])]
        reglas[code] = [n.strip() for n in nombres if n and str(n).strip()]
    return siglas, reglas


_WS = re.compile(r"\s+")


def _norm(text: str) -> str:
    folded = unicodedata.normalize("NFD", text.strip().upper())
    plain = "".join(c for c in folded if unicodedata.category(c) != "Mn")
    return _WS.sub(" ", plain)


class _Indice:
    def __init__(self) -> None:
        self.pks: set[str] = set()
        self.por_texto: dict[str, str] = {}

    def add(self, pk: str, texto: str | None) -> None:
        code = str(pk).strip().upper()
        if not code:
            return
        self.pks.add(code)
        if texto is None:
            return
        key = _norm(str(texto))
        if key and key not in self.por_texto:
            self.por_texto[key] = code

    def resolve(self, value) -> str | None:
        if value is None:
            return None
        try:
            if pd.isna(value):
                return None
        except (TypeError, ValueError):
            pass
        raw = str(value).strip()
        if not raw or raw.lower() == "nan":
            return None
        code = raw.upper()
        if code in self.pks:
            return code
        return self.por_texto.get(_norm(raw))


def _conectar(root: Path):
    variables = load_vars(root)
    cv = require_live_conn("mysql", variables)
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
    )
    return conn


def cargar_indice(root: Path) -> _Indice:
    idx = _Indice()
    conn = _conectar(root)
    try:
        cur = conn.cursor()
        cur.execute("SELECT PK_OFICINA, TX_DESCRIPCION FROM T_SEP_OFICINA")
        for pk, desc in cur.fetchall():
            idx.add(pk, desc)
        cur.close()
    finally:
        conn.close()
    siglas, reglas = cargar_alias()
    for pk, sigla in siglas.items():
        idx.add(pk, sigla)
    for pk, nombres in reglas.items():
        for nombre in nombres:
            idx.add(pk, nombre)
    return idx


def aplicar_pk_oficina(df: pd.DataFrame, root: Path) -> pd.DataFrame:
    """Llena PK_OFICINA desde TXCOORDINACION. Sin match deja NULL y lo registra."""
    if "TXCOORDINACION" not in df.columns:
        print("PK_OFICINA: sin columna TXCOORDINACION; no se cruza", flush=True)
        return df
    idx = cargar_indice(root)
    unmatched: set[str] = set()

    def one(value):
        pk = idx.resolve(value)
        if pk is None:
            try:
                empty = value is None or pd.isna(value) or str(value).strip() == ""
            except (TypeError, ValueError):
                empty = value is None
            if not empty and str(value).strip().lower() != "nan":
                unmatched.add(str(value).strip())
        return pk

    df["PK_OFICINA"] = df["TXCOORDINACION"].map(one)
    n_ok = int(df["PK_OFICINA"].notna().sum())
    print(
        f"PK_OFICINA: {n_ok}/{len(df)} filas cruzadas "
        f"({len(idx.pks)} oficinas en T_SEP_OFICINA)",
        flush=True,
    )
    if unmatched:
        muestra = sorted(unmatched)[:20]
        extra = "" if len(unmatched) <= 20 else f" (+{len(unmatched) - 20} más)"
        print(
            f"PK_OFICINA: sin cruce {len(unmatched)} textos: {muestra}{extra}",
            flush=True,
        )
    return df
