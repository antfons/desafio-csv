"""
parser.py — Mantido para compatibilidade. A lógica foi distribuída em:
    - models.py     : SaleRecord
    - validators.py : parse_date, build_record
    - reader.py     : read_csv
"""

from vendas_cli.parser.models import SaleRecord
from vendas_cli.parser.validators import parse_date as _parse_date, build_record
from vendas_cli.parser.reader import read_csv

__all__ = ["SaleRecord", "_parse_date", "build_record", "read_csv"]
