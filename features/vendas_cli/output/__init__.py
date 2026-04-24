"""
Subpacote output — formatação e renderização dos relatórios.

API pública:
    OutputFormat : tipo literal 'text' | 'json'.
    render       : escreve um SalesReport formatado em um stream de saída.
"""

from vendas_cli.output.output import OutputFormat, render

__all__ = ["OutputFormat", "render"]
