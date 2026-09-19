"""Compat shim — preferir `from rdata.schema import …` / `from rdata.map import …`."""

from rdata import *  # noqa: F403
from rdata import (  # noqa: F401
    CANONICAL,
    CANONICAL_NAMES,
    CLOB_COLS,
    COLUMN_COMMENTS,
    DATE_COLS,
    DIRECT_COLS,
    EQUIV,
    NUMBER_COLS,
    TABLE_COMMENT,
    map_to_canonical,
    normalize_colname,
    normalize_frame_columns,
    oracle_comment_statements,
    oracle_ddl,
    parse_anio_from_name,
    parse_fuente_from_name,
    parse_mes_corte_from_name,
)
