"""
test_output.py — Testes unitários para vendas_cli.output.
"""

from __future__ import annotations

import io
import json

import pytest

from vendas_cli.core import build_report, SalesReport
from vendas_cli.output import render
from vendas_cli.parser import SaleRecord


def _make_record(produto: str, quantidade: int, preco_unitario: float) -> SaleRecord:
    return SaleRecord(
        produto=produto,
        quantidade=quantidade,
        preco_unitario=preco_unitario,
        total=round(quantidade * preco_unitario, 2),
    )


def _report_sample() -> SalesReport:
    records = [
        _make_record("Camiseta", 4, 49.9),
        _make_record("Tênis", 1, 199.9),
        _make_record("Calça", 2, 99.9),
    ]
    return build_report(records)


# ─── Saída texto ──────────────────────────────────────────────────────────────

class TestRenderText:
    def test_contem_nomes_dos_produtos(self):
        report = _report_sample()
        stream = io.StringIO()
        render(report, fmt="text", stream=stream)
        output = stream.getvalue()
        assert "Camiseta" in output
        assert "Tênis" in output
        assert "Calça" in output

    def test_contem_total_geral(self):
        report = _report_sample()
        stream = io.StringIO()
        render(report, fmt="text", stream=stream)
        assert "TOTAL GERAL" in stream.getvalue()

    def test_contem_destaque_mais_vendido(self):
        report = _report_sample()
        stream = io.StringIO()
        render(report, fmt="text", stream=stream)
        assert "Mais vendido" in stream.getvalue()

    def test_relatorio_vazio(self):
        report = build_report([])
        stream = io.StringIO()
        render(report, fmt="text", stream=stream)
        assert "Nenhum registro" in stream.getvalue()

    def test_formato_padrao_e_text(self):
        """Sem especificar fmt, deve usar text."""
        report = _report_sample()
        stream = io.StringIO()
        render(report, stream=stream)
        output = stream.getvalue()
        assert "RELATÓRIO DE VENDAS" in output


# ─── Saída JSON ───────────────────────────────────────────────────────────────

class TestRenderJson:
    def _get_json(self, report: SalesReport) -> dict:
        stream = io.StringIO()
        render(report, fmt="json", stream=stream)
        return json.loads(stream.getvalue())

    def test_json_valido(self):
        report = _report_sample()
        data = self._get_json(report)
        assert isinstance(data, dict)

    def test_estrutura_resumo(self):
        report = _report_sample()
        data = self._get_json(report)
        assert "resumo" in data
        assert "receita_total" in data["resumo"]
        assert "total_registros" in data["resumo"]

    def test_estrutura_produtos(self):
        report = _report_sample()
        data = self._get_json(report)
        assert "produtos" in data
        assert isinstance(data["produtos"], list)
        assert len(data["produtos"]) == 3

    def test_campos_produto(self):
        report = _report_sample()
        data = self._get_json(report)
        primeiro = data["produtos"][0]
        assert "produto" in primeiro
        assert "total_quantidade" in primeiro
        assert "total_receita" in primeiro

    def test_receita_total_correta(self):
        report = _report_sample()
        data = self._get_json(report)
        expected = (4 * 49.9) + (1 * 199.9) + (2 * 99.9)
        assert data["resumo"]["receita_total"] == pytest.approx(expected)

    def test_produto_mais_vendido_por_quantidade(self):
        report = _report_sample()
        data = self._get_json(report)
        top = data["resumo"]["produto_mais_vendido_quantidade"]
        assert top["produto"] == "Camiseta"  # 4 unidades

    def test_produto_maior_receita(self):
        report = _report_sample()
        data = self._get_json(report)
        top = data["resumo"]["produto_maior_receita"]
        # Tênis: 1 × 199.9 = 199.90 > Camiseta: 4 × 49.9 = 199.60
        assert top["produto"] == "Tênis"

    def test_relatorio_vazio_json(self):
        report = build_report([])
        data = self._get_json(report)
        assert data["resumo"]["total_registros"] == 0
        assert data["resumo"]["receita_total"] == 0.0
        assert data["resumo"]["produto_mais_vendido_quantidade"] is None
        assert data["produtos"] == []

    def test_produtos_ordenados_por_receita(self):
        records = [
            _make_record("Barato", 100, 1.0),
            _make_record("Caro", 1, 500.0),
        ]
        report = build_report(records)
        data = self._get_json(report)
        assert data["produtos"][0]["produto"] == "Caro"
