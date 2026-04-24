"""
json_renderer.py — Renderização do relatório como JSON estruturado.
"""

from __future__ import annotations

import json
from typing import TextIO

from vendas_cli.core.models import SalesReport


def render_json(report: SalesReport, stream: TextIO) -> None:
    top_qty = report.top_by_quantity
    top_rev = report.top_by_revenue

    payload: dict = {
        "resumo": {
            "total_registros": report.total_records,
            "receita_total": report.grand_total,
            "produto_mais_vendido_quantidade": (
                {"produto": top_qty.produto, "total_quantidade": top_qty.total_quantidade, "total_receita": top_qty.total_receita}
                if top_qty else None
            ),
            "produto_maior_receita": (
                {"produto": top_rev.produto, "total_quantidade": top_rev.total_quantidade, "total_receita": top_rev.total_receita}
                if top_rev else None
            ),
        },
        "produtos": [
            {"produto": ps.produto, "total_quantidade": ps.total_quantidade, "total_receita": ps.total_receita}
            for ps in report.sorted_products
        ],
    }

    json.dump(payload, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
