"""
Subpacote core — lógica de negócio e agregações de vendas.

API pública:
    ProductSummary : resumo agregado por produto.
    SalesReport    : relatório consolidado com totais e destaques.
    build_report   : constrói um SalesReport a partir de um iterável de SaleRecords.
"""

from vendas_cli.core.models import ProductSummary, SalesReport
from vendas_cli.core.aggregator import build_report

__all__ = ["ProductSummary", "SalesReport", "build_report"]
