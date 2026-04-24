"""
cli.py — Ponto de entrada da CLI vendas-cli.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Optional

from vendas_cli import __version__
from vendas_cli.core.aggregator import build_report
from vendas_cli.output.output import OutputFormat, render
from vendas_cli.parser.reader import read_csv

logger = logging.getLogger(__name__)


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stderr,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vendas-cli",
        description=(
            "Processa um CSV de vendas e gera relatórios ricos.\n\n"
            "Exemplo de uso:\n"
            "  vendas-cli vendas.csv\n"
            "  vendas-cli vendas.csv --format json\n"
            "  vendas-cli vendas.csv --format text --start 2025-01-01 --end 2025-03-31\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("file", metavar="file", type=Path,
                        help="Caminho para o arquivo CSV de vendas.")
    parser.add_argument("--format", dest="fmt", choices=["text", "json"], default="text",
                        metavar="FORMAT", help="Formato de saída: 'text' ou 'json'. Padrão: text.")
    parser.add_argument("--start", dest="start_date", metavar="AAAA-MM-DD",
                        help="Data inicial do filtro (inclusiva).")
    parser.add_argument("--end", dest="end_date", metavar="AAAA-MM-DD",
                        help="Data final do filtro (inclusiva).")
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="Habilita logs detalhados no stderr.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _parse_date_arg(value: Optional[str], param_name: str) -> Optional[date]:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"'{param_name}' inválido: {value!r}. Use o formato AAAA-MM-DD."
        )


def main(argv: Optional[list[str]] = None) -> int:
    arg_parser = _build_parser()
    args = arg_parser.parse_args(argv)
    _configure_logging(args.verbose)

    try:
        start_date = _parse_date_arg(args.start_date, "--start")
        end_date = _parse_date_arg(args.end_date, "--end")
    except argparse.ArgumentTypeError as exc:
        arg_parser.error(str(exc))
        return 1

    if start_date and end_date and start_date > end_date:
        arg_parser.error(f"--start ({start_date}) não pode ser posterior a --end ({end_date}).")

    try:
        records = read_csv(args.file, start_date=start_date, end_date=end_date)
        report = build_report(records)
        render(report, fmt=args.fmt)  # type: ignore[arg-type]
    except FileNotFoundError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Erro de formato no CSV: {exc}", file=sys.stderr)
        return 1
    except PermissionError as exc:
        print(f"Sem permissão para ler o arquivo: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        logger.exception("Erro inesperado")
        print(f"Erro interno inesperado: {exc}", file=sys.stderr)
        return 2

    return 0


def entrypoint() -> None:
    sys.exit(main())


if __name__ == "__main__":
    entrypoint()
