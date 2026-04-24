"""
test_cli.py — Testes de integração para vendas_cli.cli.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from vendas_cli.cli import main


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _csv(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "vendas.csv"
    p.write_text(content, encoding="utf-8")
    return p


CONTENT_SEM_DATA = (
    "produto,quantidade,preco_unitario\n"
    "Camiseta,3,49.9\n"
    "Calça,2,99.9\n"
    "Tênis,1,199.9\n"
)

CONTENT_COM_DATA = (
    "produto,quantidade,preco_unitario,data_venda\n"
    "Camiseta,3,49.9,2025-01-15\n"
    "Calça,2,99.9,2025-02-10\n"
    "Tênis,1,199.9,2025-03-05\n"
)


# ─── Casos de sucesso ─────────────────────────────────────────────────────────

class TestCliSuccess:
    def test_saida_texto_padrao(self, tmp_path, capsys):
        p = _csv(tmp_path, CONTENT_SEM_DATA)
        code = main([str(p)])
        out = capsys.readouterr().out
        assert code == 0
        assert "Camiseta" in out

    def test_saida_json(self, tmp_path, capsys):
        p = _csv(tmp_path, CONTENT_SEM_DATA)
        code = main([str(p), "--format", "json"])
        out = capsys.readouterr().out
        assert code == 0
        data = json.loads(out)
        assert "resumo" in data
        assert "produtos" in data

    def test_flag_format_text(self, tmp_path, capsys):
        p = _csv(tmp_path, CONTENT_SEM_DATA)
        code = main([str(p), "--format", "text"])
        out = capsys.readouterr().out
        assert code == 0
        assert "RELATÓRIO DE VENDAS" in out

    def test_filtro_start_end(self, tmp_path, capsys):
        p = _csv(tmp_path, CONTENT_COM_DATA)
        code = main([str(p), "--start", "2025-02-01", "--end", "2025-02-28"])
        out = capsys.readouterr().out
        assert code == 0
        assert "Cal" in out
        assert "Camiseta" not in out
        assert "nis" not in out

    def test_filtro_start_apenas(self, tmp_path, capsys):
        p = _csv(tmp_path, CONTENT_COM_DATA)
        code = main([str(p), "--start", "2025-03-01"])
        out = capsys.readouterr().out
        assert code == 0
        assert "nis" in out

    def test_json_com_filtro(self, tmp_path, capsys):
        p = _csv(tmp_path, CONTENT_COM_DATA)
        code = main([str(p), "--format", "json", "--start", "2025-01-01", "--end", "2025-01-31"])
        out = capsys.readouterr().out
        assert code == 0
        data = json.loads(out)
        assert len(data["produtos"]) == 1
        assert data["produtos"][0]["produto"] == "Camiseta"

    def test_verbose_nao_quebra(self, tmp_path, capsys):
        p = _csv(tmp_path, CONTENT_SEM_DATA)
        code = main([str(p), "--verbose"])
        assert code == 0


# ─── Casos de erro ────────────────────────────────────────────────────────────

class TestCliErrors:
    def test_arquivo_inexistente_retorna_1(self, tmp_path, capsys):
        code = main([str(tmp_path / "nao_existe.csv")])
        assert code == 1
        assert "não encontrado" in capsys.readouterr().err

    def test_data_invalida_start(self, tmp_path):
        p = _csv(tmp_path, CONTENT_SEM_DATA)
        with pytest.raises(SystemExit) as exc_info:
            main([str(p), "--start", "15-01-2025"])
        assert exc_info.value.code != 0

    def test_data_invalida_end(self, tmp_path):
        p = _csv(tmp_path, CONTENT_SEM_DATA)
        with pytest.raises(SystemExit):
            main([str(p), "--end", "nao-e-data"])

    def test_start_posterior_a_end(self, tmp_path):
        p = _csv(tmp_path, CONTENT_SEM_DATA)
        with pytest.raises(SystemExit):
            main([str(p), "--start", "2025-12-31", "--end", "2025-01-01"])

    def test_csv_sem_coluna_obrigatoria(self, tmp_path, capsys):
        p = _csv(tmp_path, "produto,quantidade\nX,1\n")
        code = main([str(p)])
        assert code == 1
        assert "preco_unitario" in capsys.readouterr().err



    def test_encoding_latin1_detectado_automaticamente(self, tmp_path, capsys):
        p = tmp_path / "vendas_latin1.csv"
        content = "produto,quantidade,preco_unitario\nCamiseta,3,49.9\nCalça,2,99.9\n"
        p.write_bytes(content.encode("latin-1"))
        code = main([str(p)])
        assert code == 0
        assert "Cal" in capsys.readouterr().out
