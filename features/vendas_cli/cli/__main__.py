"""
__main__.py — Permite executar o pacote cli diretamente via:

    python -m vendas_cli.cli  [argumentos]

Útil no Windows quando o comando 'vendas-cli' não está no PATH.
"""

from vendas_cli.cli.cli import entrypoint

entrypoint()
