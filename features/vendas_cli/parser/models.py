"""
models.py — Estruturas de dados do subpacote parser.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class SaleRecord:
    """Representa uma linha válida do CSV de vendas."""

    produto: str
    quantidade: int
    preco_unitario: float
    total: float
    data_venda: Optional[date] = None
