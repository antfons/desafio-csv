"""
Subpacote cli — ponto de entrada da CLI vendas-cli.

API pública:
    main       : função principal (retorna exit code).
    entrypoint : wrapper para console_scripts.
"""

from vendas_cli.cli.cli import entrypoint, main

__all__ = ["main", "entrypoint"]
