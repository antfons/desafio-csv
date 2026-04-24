"""
models.py — Estruturas de dados do subpacote core.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProductSummary:
    """Resumo agregado de um produto."""

    produto: str
    total_quantidade: int = 0
    total_receita: float = 0.0

    def add(self, quantidade: int, total: float) -> None:
        self.total_quantidade += quantidade
        self.total_receita = round(self.total_receita + total, 2)


@dataclass
class SalesReport:
    """Relatório consolidado de vendas."""

    products: dict[str, ProductSummary] = field(default_factory=dict)
    grand_total: float = 0.0
    total_records: int = 0

    @property
    def top_by_quantity(self) -> Optional[ProductSummary]:
        if not self.products:
            return None
        return max(self.products.values(), key=lambda p: p.total_quantidade)

    @property
    def top_by_revenue(self) -> Optional[ProductSummary]:
        if not self.products:
            return None
        return max(self.products.values(), key=lambda p: p.total_receita)

    @property
    def sorted_products(self) -> list[ProductSummary]:
        return sorted(self.products.values(), key=lambda p: p.total_receita, reverse=True)
