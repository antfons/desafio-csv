"""
validators.py — Funções de validação e conversão de campos do CSV.
"""

from __future__ import annotations

from datetime import date, datetime

from vendas_cli.parser.models import SaleRecord

DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y")


def parse_date(raw: str, line_number: int) -> date:
    """Tenta múltiplos formatos de data; levanta ValueError se nenhum funcionar."""
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError(
        f"linha {line_number}: 'data_venda' inválida ({raw!r}). "
        f"Formatos aceitos: {', '.join(DATE_FORMATS)}"
    )


def build_record(
    row: dict[str, str],
    line_number: int,
    has_date_column: bool = False,
) -> SaleRecord:
    """
    Valida e constrói um SaleRecord a partir de um dict do csv.DictReader.
    Levanta ValueError com mensagem descritiva se qualquer campo for inválido.
    """
    from typing import Optional

    produto = row.get("produto", "").strip()
    if not produto:
        raise ValueError(f"linha {line_number}: campo 'produto' vazio")

    raw_qty = row.get("quantidade", "").strip()
    try:
        quantidade = int(raw_qty)
        if quantidade < 0:
            raise ValueError("quantidade negativa")
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"linha {line_number}: 'quantidade' inválida ({raw_qty!r}) — {exc}"
        ) from exc

    raw_price = row.get("preco_unitario", "").strip().replace(",", ".")
    try:
        preco_unitario = float(raw_price)
        if preco_unitario < 0:
            raise ValueError("preço negativo")
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"linha {line_number}: 'preco_unitario' inválido ({raw_price!r}) — {exc}"
        ) from exc

    data_venda: Optional[date] = None
    if has_date_column:
        raw_date = row.get("data_venda", "").strip()
        if raw_date:
            data_venda = parse_date(raw_date, line_number)

    return SaleRecord(
        produto=produto,
        quantidade=quantidade,
        preco_unitario=preco_unitario,
        total=round(quantidade * preco_unitario, 2),
        data_venda=data_venda,
    )
