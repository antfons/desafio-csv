"""
core.py — Mantido para compatibilidade. A lógica foi distribuída em:
    - models.py     : ProductSummary, SalesReport
    - aggregator.py : build_report
"""

from vendas_cli.core.models import ProductSummary, SalesReport
from vendas_cli.core.aggregator import build_report

__all__ = ["ProductSummary", "SalesReport", "build_report"]
