"""
test_core.py — Testes unitários para vendas_cli.core.
"""

from __future__ import annotations

from datetime import date

import pytest

from vendas_cli.core import ProductSummary, SalesReport, build_report
from vendas_cli.parser import SaleRecord


def _make_record(
    produto: str,
    quantidade: int,
    preco_unitario: float,
    data_venda: date | None = None,
) -> SaleRecord:
    return SaleRecord(
        produto=produto,
        quantidade=quantidade,
        preco_unitario=preco_unitario,
        total=round(quantidade * preco_unitario, 2),
        data_venda=data_venda,
    )


# ─── ProductSummary ───────────────────────────────────────────────────────────

class TestProductSummary:
    def test_add_acumula_valores(self):
        ps = ProductSummary(produto="Camiseta")
        r1 = _make_record("Camiseta", 3, 49.9)
        r2 = _make_record("Camiseta", 1, 49.9)
        ps.add(r1.quantidade, r1.total)
        ps.add(r2.quantidade, r2.total)
        assert ps.total_quantidade == 4
        assert ps.total_receita == pytest.approx(4 * 49.9)

    def test_valores_iniciais_zerados(self):
        ps = ProductSummary(produto="X")
        assert ps.total_quantidade == 0
        assert ps.total_receita == 0.0


# ─── build_report ─────────────────────────────────────────────────────────────

class TestBuildReport:
    def test_relatorio_vazio(self):
        report = build_report([])
        assert report.total_records == 0
        assert report.grand_total == 0.0
        assert report.products == {}

    def test_contagem_de_registros(self, sample_records):
        report = build_report(sample_records)
        assert report.total_records == 3

    def test_grand_total(self, sample_records):
        report = build_report(sample_records)
        expected = sum(r.total for r in sample_records)
        assert report.grand_total == pytest.approx(expected)

    def test_produtos_distintos_agrupados(self):
        records = [
            _make_record("Camiseta", 3, 49.9),
            _make_record("Camiseta", 2, 49.9),
            _make_record("Tênis", 1, 199.9),
        ]
        report = build_report(records)
        assert len(report.products) == 2
        assert report.products["Camiseta"].total_quantidade == 5
        assert report.products["Tênis"].total_quantidade == 1

    def test_receita_por_produto(self):
        records = [
            _make_record("Meia", 10, 12.5),
            _make_record("Meia", 5, 12.5),
        ]
        report = build_report(records)
        assert report.products["Meia"].total_receita == pytest.approx(187.5)

    def test_grand_total_acumulado(self):
        records = [
            _make_record("A", 2, 10.0),
            _make_record("B", 3, 20.0),
        ]
        report = build_report(records)
        assert report.grand_total == pytest.approx(80.0)

    def test_aceita_gerador(self):
        """build_report deve funcionar com qualquer iterável, não apenas listas."""
        def gen():
            yield _make_record("X", 1, 5.0)
            yield _make_record("Y", 2, 10.0)

        report = build_report(gen())
        assert report.total_records == 2


# ─── SalesReport.top_by_quantity / top_by_revenue ────────────────────────────

class TestSalesReportProperties:
    def test_top_by_quantity_retorna_mais_vendido(self):
        records = [
            _make_record("A", 10, 5.0),
            _make_record("B", 3, 50.0),
        ]
        report = build_report(records)
        assert report.top_by_quantity.produto == "A"

    def test_top_by_revenue_retorna_maior_receita(self):
        records = [
            _make_record("A", 10, 5.0),   # receita 50
            _make_record("B", 3, 50.0),   # receita 150
        ]
        report = build_report(records)
        assert report.top_by_revenue.produto == "B"

    def test_top_none_quando_sem_produtos(self):
        report = build_report([])
        assert report.top_by_quantity is None
        assert report.top_by_revenue is None

    def test_sorted_products_ordem_decrescente(self):
        records = [
            _make_record("Barato", 100, 1.0),   # receita 100
            _make_record("Caro", 1, 500.0),     # receita 500
            _make_record("Medio", 10, 20.0),    # receita 200
        ]
        report = build_report(records)
        sorted_names = [p.produto for p in report.sorted_products]
        assert sorted_names == ["Caro", "Medio", "Barato"]
