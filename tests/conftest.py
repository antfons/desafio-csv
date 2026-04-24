"""
conftest.py — Fixtures compartilhadas entre os testes.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from vendas_cli.parser import SaleRecord


# ─── Fixtures de SaleRecord ───────────────────────────────────────────────────

@pytest.fixture
def record_camiseta() -> SaleRecord:
    return SaleRecord(
        produto="Camiseta",
        quantidade=3,
        preco_unitario=49.90,
        total=149.70,
        data_venda=date(2025, 1, 15),
    )


@pytest.fixture
def record_tenis() -> SaleRecord:
    return SaleRecord(
        produto="Tênis",
        quantidade=1,
        preco_unitario=199.90,
        total=199.90,
        data_venda=date(2025, 2, 10),
    )


@pytest.fixture
def record_calca() -> SaleRecord:
    return SaleRecord(
        produto="Calça",
        quantidade=2,
        preco_unitario=99.90,
        total=199.80,
        data_venda=date(2025, 3, 5),
    )


@pytest.fixture
def sample_records(record_camiseta, record_tenis, record_calca) -> list[SaleRecord]:
    return [record_camiseta, record_tenis, record_calca]


# ─── Fixtures de arquivos CSV ─────────────────────────────────────────────────

def _write_csv(tmp_path: Path, content: str, filename: str = "vendas.csv") -> Path:
    """Escreve conteúdo num arquivo temporário e retorna o Path."""
    p = tmp_path / filename
    p.write_text(content, encoding="utf-8")
    return p


@pytest.fixture
def csv_sem_data(tmp_path: Path) -> Path:
    """CSV válido sem coluna data_venda."""
    content = (
        "produto,quantidade,preco_unitario\n"
        "Camiseta,3,49.9\n"
        "Calça,2,99.9\n"
        "Camiseta,1,49.9\n"
        "Tênis,1,199.9\n"
    )
    return _write_csv(tmp_path, content)


@pytest.fixture
def csv_com_data(tmp_path: Path) -> Path:
    """CSV válido com coluna data_venda."""
    content = (
        "produto,quantidade,preco_unitario,data_venda\n"
        "Camiseta,3,49.9,2025-01-15\n"
        "Calça,2,99.9,2025-02-10\n"
        "Tênis,1,199.9,2025-03-05\n"
    )
    return _write_csv(tmp_path, content)


@pytest.fixture
def csv_com_erros(tmp_path: Path) -> Path:
    """CSV com algumas linhas inválidas misturadas às válidas."""
    content = (
        "produto,quantidade,preco_unitario\n"
        "Camiseta,3,49.9\n"
        ",2,99.9\n"           # produto vazio
        "Tênis,abc,199.9\n"   # quantidade inválida
        "Calça,1,-10.0\n"     # preço negativo
        "Meia,5,19.9\n"
    )
    return _write_csv(tmp_path, content)
