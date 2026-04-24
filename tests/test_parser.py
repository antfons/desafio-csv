"""
test_parser.py — Testes unitários para vendas_cli.parser.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from vendas_cli.parser import SaleRecord, read_csv
from vendas_cli.parser.validators import build_record
from vendas_cli.parser.validators import parse_date as _parse_date


# ─── _parse_date ──────────────────────────────────────────────────────────────

class TestParseDate:
    def test_formato_iso(self):
        assert _parse_date("2025-06-15", 1) == date(2025, 6, 15)

    def test_formato_br_barra(self):
        assert _parse_date("15/06/2025", 1) == date(2025, 6, 15)

    def test_formato_br_hifen(self):
        assert _parse_date("15-06-2025", 1) == date(2025, 6, 15)

    def test_formato_invalido_levanta_erro(self):
        with pytest.raises(ValueError, match="data_venda"):
            _parse_date("2025/06/15", 5)

    def test_string_vazia_levanta_erro(self):
        with pytest.raises(ValueError):
            _parse_date("", 1)


# ─── build_record ──────────────────────────────────────────────────────

class TestSaleRecordFromRow:
    def test_linha_valida_sem_data(self):
        row = {"produto": "Camiseta", "quantidade": "3", "preco_unitario": "49.9"}
        record = build_record(row, 2, has_date_column=False)
        assert record.produto == "Camiseta"
        assert record.quantidade == 3
        assert record.preco_unitario == 49.9
        assert record.total == pytest.approx(149.7)
        assert record.data_venda is None

    def test_linha_valida_com_data(self):
        row = {
            "produto": "Tênis",
            "quantidade": "1",
            "preco_unitario": "199.9",
            "data_venda": "2025-03-01",
        }
        record = build_record(row, 2, has_date_column=True)
        assert record.data_venda == date(2025, 3, 1)

    def test_preco_com_virgula(self):
        row = {"produto": "Meia", "quantidade": "10", "preco_unitario": "12,50"}
        record = build_record(row, 2)
        assert record.preco_unitario == 12.50

    def test_produto_vazio_levanta_erro(self):
        row = {"produto": "", "quantidade": "1", "preco_unitario": "10.0"}
        with pytest.raises(ValueError, match="produto"):
            build_record(row, 3)

    def test_quantidade_invalida_levanta_erro(self):
        row = {"produto": "X", "quantidade": "abc", "preco_unitario": "10.0"}
        with pytest.raises(ValueError, match="quantidade"):
            build_record(row, 4)

    def test_quantidade_negativa_levanta_erro(self):
        row = {"produto": "X", "quantidade": "-5", "preco_unitario": "10.0"}
        with pytest.raises(ValueError, match="quantidade"):
            build_record(row, 5)

    def test_preco_negativo_levanta_erro(self):
        row = {"produto": "X", "quantidade": "1", "preco_unitario": "-10.0"}
        with pytest.raises(ValueError, match="preco_unitario"):
            build_record(row, 6)

    def test_preco_invalido_levanta_erro(self):
        row = {"produto": "X", "quantidade": "1", "preco_unitario": "xyz"}
        with pytest.raises(ValueError, match="preco_unitario"):
            build_record(row, 7)

    def test_total_calculado_corretamente(self):
        row = {"produto": "P", "quantidade": "7", "preco_unitario": "3.33"}
        record = build_record(row, 2)
        assert record.total == pytest.approx(23.31)

    def test_data_invalida_com_coluna_levanta_erro(self):
        row = {
            "produto": "P",
            "quantidade": "1",
            "preco_unitario": "10.0",
            "data_venda": "nao-e-data",
        }
        with pytest.raises(ValueError, match="data_venda"):
            build_record(row, 2, has_date_column=True)


# ─── read_csv ─────────────────────────────────────────────────────────────────

class TestReadCsv:
    def test_arquivo_inexistente_levanta_erro(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            list(read_csv(tmp_path / "nao_existe.csv"))

    def test_leitura_sem_data(self, csv_sem_data: Path):
        records = list(read_csv(csv_sem_data))
        assert len(records) == 4
        assert all(r.data_venda is None for r in records)

    def test_leitura_com_data(self, csv_com_data: Path):
        records = list(read_csv(csv_com_data))
        assert len(records) == 3
        assert all(r.data_venda is not None for r in records)

    def test_produtos_corretos(self, csv_sem_data: Path):
        records = list(read_csv(csv_sem_data))
        produtos = [r.produto for r in records]
        assert "Camiseta" in produtos
        assert "Calça" in produtos
        assert "Tênis" in produtos

    def test_linhas_invalidas_sao_ignoradas(self, csv_com_erros: Path):
        records = list(read_csv(csv_com_erros))
        # Apenas "Camiseta" e "Meia" são válidos (3 linhas inválidas)
        assert len(records) == 2

    def test_filtro_start_date(self, csv_com_data: Path):
        records = list(read_csv(csv_com_data, start_date=date(2025, 2, 1)))
        # Remove Camiseta (2025-01-15)
        assert len(records) == 2
        assert all(r.data_venda >= date(2025, 2, 1) for r in records)

    def test_filtro_end_date(self, csv_com_data: Path):
        records = list(read_csv(csv_com_data, end_date=date(2025, 2, 28)))
        # Remove Tênis (2025-03-05)
        assert len(records) == 2
        assert all(r.data_venda <= date(2025, 2, 28) for r in records)

    def test_filtro_intervalo(self, csv_com_data: Path):
        records = list(
            read_csv(csv_com_data, start_date=date(2025, 2, 1), end_date=date(2025, 2, 28))
        )
        assert len(records) == 1
        assert records[0].produto == "Calça"

    def test_filtro_data_sem_coluna_nao_filtra(self, csv_sem_data: Path):
        """Filtros de data devem ser ignorados se a coluna não existe."""
        records = list(
            read_csv(csv_sem_data, start_date=date(2025, 1, 1), end_date=date(2025, 1, 31))
        )
        # Sem coluna de data, todos os 4 registros devem passar
        assert len(records) == 4


    def test_csv_sem_coluna_obrigatoria(self, tmp_path: Path):
        p = tmp_path / "invalido.csv"
        p.write_text("produto,quantidade\nX,1\n")
        with pytest.raises(ValueError, match="preco_unitario"):
            list(read_csv(p))

    def test_csv_vazio(self, tmp_path: Path):
        p = tmp_path / "vazio.csv"
        p.write_text("")
        with pytest.raises(ValueError, match="vazio"):
            list(read_csv(p))

    def test_totais_corretos(self, csv_sem_data: Path):
        records = list(read_csv(csv_sem_data))
        totais = {r.produto: r.total for r in records}
        # Camiseta aparece 2x; checamos registros individuais
        camisetas = [r for r in records if r.produto == "Camiseta"]
        assert camisetas[0].total == pytest.approx(3 * 49.9)
        assert camisetas[1].total == pytest.approx(1 * 49.9)
