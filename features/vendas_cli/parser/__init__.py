"""
Subpacote parser — leitura e validação do CSV de vendas.

API pública:
    SaleRecord  : dataclass que representa uma linha válida.
    read_csv    : gerador que produz SaleRecords a partir de um arquivo CSV.
"""

from vendas_cli.parser.models import SaleRecord
from vendas_cli.parser.reader import read_csv

__all__ = ["SaleRecord", "read_csv"]
