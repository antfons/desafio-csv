"""
reader.py — Abertura e iteração do arquivo CSV de vendas.
"""

from __future__ import annotations

import csv
import logging
from datetime import date
from pathlib import Path
from typing import Iterator, Optional

from vendas_cli.parser.models import SaleRecord
from vendas_cli.parser.validators import build_record

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {"produto", "quantidade", "preco_unitario"}
_ENCODINGS = ("utf-8-sig", "utf-8", "latin-1", "cp1252")


def _detect_encoding(path: Path) -> str:
    """Detecta o encoding do arquivo tentando abrir com cada candidato."""
    for enc in _ENCODINGS:
        try:
            with path.open(encoding=enc) as fh:
                fh.read()
            logger.debug("Encoding detectado: '%s'", enc)
            return enc
        except UnicodeDecodeError:
            continue
    raise ValueError(
        f"Não foi possível decodificar '{path.name}'. "
        f"Tente converter o arquivo para UTF-8."
    )


def read_csv(
    path: Path,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Iterator[SaleRecord]:
    """
    Lê um CSV de vendas e produz SaleRecords válidos.

    A coluna 'data_venda' é opcional. Linhas inválidas são ignoradas com WARNING.
    O encoding é detectado automaticamente (UTF-8, Latin-1, CP1252).
    """
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    if not path.is_file():
        raise ValueError(f"Caminho não é um arquivo: {path}")

    encoding = _detect_encoding(path)
    logger.info("Abrindo arquivo CSV: %s (encoding=%s)", path, encoding)

    with path.open(newline="", encoding=encoding) as fh:
        reader = csv.DictReader(fh)

        if reader.fieldnames is None:
            raise ValueError("CSV vazio ou sem cabeçalho")

        normalized_fields = [f.strip().lower() for f in reader.fieldnames]
        reader.fieldnames = normalized_fields
        column_set = set(normalized_fields)

        missing = REQUIRED_COLUMNS - column_set
        if missing:
            raise ValueError(
                f"Colunas obrigatórias ausentes no CSV: {', '.join(sorted(missing))}"
            )

        has_date_column = "data_venda" in column_set
        if not has_date_column and (start_date or end_date):
            logger.warning(
                "Filtros de data informados mas 'data_venda' não existe no CSV. "
                "Os filtros serão ignorados."
            )

        logger.info("Colunas detectadas: %s", ", ".join(normalized_fields))

        valid_count = skipped_count = 0

        for line_number, row in enumerate(reader, start=2):
            try:
                record = build_record(row, line_number, has_date_column)
            except ValueError as exc:
                logger.warning("Linha ignorada — %s", exc)
                skipped_count += 1
                continue

            if has_date_column and record.data_venda is not None:
                if start_date and record.data_venda < start_date:
                    continue
                if end_date and record.data_venda > end_date:
                    continue

            valid_count += 1
            yield record

        logger.info(
            "Leitura concluída: %d registros válidos, %d ignorados",
            valid_count,
            skipped_count,
        )
