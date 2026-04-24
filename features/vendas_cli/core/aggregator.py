"""
aggregator.py — Lógica de agregação: constrói SalesReport a partir de SaleRecords.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Iterable

from vendas_cli.parser import SaleRecord
from vendas_cli.core.models import ProductSummary, SalesReport

logger = logging.getLogger(__name__)


def build_report(records: Iterable[SaleRecord]) -> SalesReport:
    """
    Agrega uma sequência de SaleRecords em um SalesReport.
    Aceita qualquer iterável — não carrega tudo na memória.
    """
    report = SalesReport()
    aggregator: dict[str, ProductSummary] = defaultdict(lambda: ProductSummary(produto=""))

    for record in records:
        if record.produto not in aggregator:
            aggregator[record.produto] = ProductSummary(produto=record.produto)

        aggregator[record.produto].add(record.quantidade, record.total)
        report.grand_total = round(report.grand_total + record.total, 2)
        report.total_records += 1

    report.products = dict(aggregator)

    logger.info(
        "Relatório gerado: %d produtos, %d registros, receita total R$ %.2f",
        len(report.products),
        report.total_records,
        report.grand_total,
    )
    return report
