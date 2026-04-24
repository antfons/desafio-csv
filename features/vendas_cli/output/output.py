"""
output.py — Mantido para compatibilidade. A lógica foi distribuída em:
    - text.py          : render_text
    - json_renderer.py : render_json
"""

from __future__ import annotations

import logging
import sys
from typing import Literal, Optional, TextIO

from vendas_cli.core.models import SalesReport
from vendas_cli.output.text import render_text
from vendas_cli.output.json_renderer import render_json

logger = logging.getLogger(__name__)

OutputFormat = Literal["text", "json"]


def render(
    report: SalesReport,
    fmt: OutputFormat = "text",
    stream: Optional[TextIO] = None,
) -> None:
    if stream is None:
        stream = sys.stdout
    if fmt == "json":
        render_json(report, stream)
    else:
        render_text(report, stream)
