"""
text.py — Renderização do relatório como tabela ASCII.
"""

from __future__ import annotations

from typing import TextIO

from vendas_cli.core.models import SalesReport

_COL_PRODUTO = 30
_COL_QTD = 12
_COL_RECEITA = 16
_SEP_CHAR = "─"
_HEADER_CHAR = "═"


def render_text(report: SalesReport, stream: TextIO) -> None:
    w_prod, w_qty, w_rev = _COL_PRODUTO, _COL_QTD, _COL_RECEITA
    total_width = w_prod + w_qty + w_rev + 4

    header_sep = _HEADER_CHAR * total_width
    row_sep = _SEP_CHAR * total_width

    def _row(produto: str, qty: str, receita: str) -> str:
        return (
            f"│ {produto:<{w_prod - 1}}"
            f"│ {qty:>{w_qty - 1}} "
            f"│ {receita:>{w_rev - 1}} │"
        )

    lines: list[str] = []
    lines.append(header_sep)
    lines.append(f"{'RELATÓRIO DE VENDAS':^{total_width}}")
    lines.append(header_sep)

    if report.total_records == 0:
        lines.append(f"{'  Nenhum registro encontrado para os filtros informados.':<{total_width}}")
        lines.append(header_sep)
        stream.write("\n".join(lines) + "\n")
        return

    lines.append(_row("PRODUTO", "QUANTIDADE", "RECEITA (R$)"))
    lines.append(row_sep)

    for ps in report.sorted_products:
        lines.append(_row(
            ps.produto[:w_prod - 1],
            str(ps.total_quantidade),
            f"{ps.total_receita:,.2f}",
        ))

    lines.append(header_sep)
    lines.append(_row(
        "TOTAL GERAL",
        str(sum(p.total_quantidade for p in report.products.values())),
        f"{report.grand_total:,.2f}",
    ))
    lines.append(header_sep)

    top_qty = report.top_by_quantity
    top_rev = report.top_by_revenue

    lines.append("")
    lines.append("  DESTAQUES")
    if top_qty:
        lines.append(f"  • Mais vendido (qtd)  : {top_qty.produto} ({top_qty.total_quantidade} unidades)")
    if top_rev:
        lines.append(f"  • Maior receita       : {top_rev.produto} (R$ {top_rev.total_receita:,.2f})")
    lines.append(f"  • Total de registros  : {report.total_records}")
    lines.append("")

    stream.write("\n".join(lines) + "\n")
