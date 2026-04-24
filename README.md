# Gerador de relatório de vendas de produtos

Client em Python para processar arquivos CSV de vendas e gerar relatórios.

---

## Funcionalidades

- Leitura de CSV usando apenas bibliotecas padrão (`csv`, `argparse`, `logging`)
- Total de vendas **por produto** e **geral**
- Identificação do **produto mais vendido** (quantidade e receita)
- Filtro por intervalo de datas (`--start` / `--end`)
- Saída em **tabela formatada** ou **JSON estruturado**
- Suporte automático a encodings UTF-8 e Latin-1
- Coluna `data_venda` **opcional** — funciona com e sem ela
- Logs detalhados via `--verbose`

---

## Estrutura do CSV

Colunas **obrigatórias**:

| Coluna           | Tipo    | Exemplo   |
|------------------|---------|-----------|
| `produto`        | string  | Camiseta  |
| `quantidade`     | inteiro | 3         |
| `preco_unitario` | decimal | 49.90     |

Coluna **opcional**:

| Coluna       | Tipo | Formato aceito                    |
|--------------|------|-----------------------------------|
| `data_venda` | data | `AAAA-MM-DD`, `DD/MM/AAAA`, `DD-MM-AAAA` |

### Exemplo de arquivo

```csv
produto,quantidade,preco_unitario,data_venda
Camiseta,3,49.9,2025-01-10
Calça,2,99.9,2025-01-22
Tênis,1,199.9,2025-02-18
```

---

## Instalação

### Pré-requisitos

- Python 3.10 ou superior
- pip

---

### Instalar para uso direto

```bash
git clone <repo-url>
cd vendas-cli

pip install -r requirements.txt
pip install .
```

### Instalar em modo desenvolvimento

```bash
git clone <repo-url>
cd vendas-cli

pip install -r requirements-dev.txt
pip install -e .
```

Após a instalação, o comando `vendas-cli` estará disponível no PATH.

> **⚠️ Importante:** O comando `vendas-cli` só fica disponível no PATH **após rodar `pip install .`** (ou `pip install -e .`). Sem isso, o terminal não reconhece o comando.

---

### Solução de problemas por sistema operacional

#### Windows (PowerShell ou CMD)

Se o terminal exibir um erro como `'vendas-cli' is not recognized`, execute:

```powershell
pip install -e .
```



Como alternativa, use sempre o módulo diretamente — **sem necessidade de instalação**:

```powershell
python -m vendas_cli.cli.cli vendas_exemplo.csv
python -m vendas_cli.cli.cli vendas_exemplo.csv --format json
```

#### Linux / macOS

```bash
pip install -e .
vendas-cli vendas_exemplo.csv
```

Se `vendas-cli` não for encontrado após instalar, adicione o diretório de scripts ao PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## Uso

### Sintaxe

```
vendas-cli file [--format text|json] [--start AAAA-MM-DD] [--end AAAA-MM-DD] [-v]
```

### Opções

| Opção                | Descrição                                              | Padrão |
|----------------------|--------------------------------------------------------|--------|
| `file`               | Caminho para o CSV de vendas                           | —      |
| `--format text`      | Saída em tabela ASCII formatada                        | `text` |
| `--format json`      | Saída em JSON estruturado                              | —      |
| `--start AAAA-MM-DD` | Data inicial do filtro (inclusiva)                   | —      |
| `--end AAAA-MM-DD`   | Data final do filtro (inclusiva)                     | —      |
| `-v / --verbose`     | Habilita logs detalhados no stderr                     | `false`|
| `--version`          | Exibe a versão e sai                                   | —      |

### Exemplos

```bash
# Relatório completo em tabela
vendas-cli vendas_exemplo.csv

# Saída JSON
vendas-cli vendas_exemplo.csv --format json

# Filtrar por período (requer coluna data_venda no CSV)
vendas-cli vendas_com_data.csv --format text --start 2025-01-01 --end 2025-03-31

# Formato JSON com filtro de data
vendas-cli vendas_com_data.csv --format json --start 2025-02-01 --end 2025-02-28

# Logs detalhados
vendas-cli vendas_exemplo.csv --verbose
```

### Saída texto (exemplo)

```
════════════════════════════════════════════════════════
              RELATÓRIO DE VENDAS
════════════════════════════════════════════════════════
│ PRODUTO                       │   QUANTIDADE │  RECEITA (R$) │
────────────────────────────────────────────────────────
│ Camiseta                      │            9 │        449,10 │
│ Tênis                         │            3 │        599,70 │
│ Calça                         │            3 │        299,70 │
════════════════════════════════════════════════════════
│ TOTAL GERAL                   │           15 │      1.348,50 │
════════════════════════════════════════════════════════

  DESTAQUES
  • Mais vendido (qtd)  : Camiseta (9 unidades)
  • Maior receita       : Tênis (R$ 599,70)
  • Total de registros  : 8
```

### Saída JSON (exemplo)

```json
{
  "resumo": {
    "total_registros": 8,
    "receita_total": 1348.5,
    "produto_mais_vendido_quantidade": {
      "produto": "Camiseta",
      "total_quantidade": 9,
      "total_receita": 449.1
    },
    "produto_maior_receita": {
      "produto": "Tênis",
      "total_quantidade": 3,
      "total_receita": 599.7
    }
  },
  "produtos": [
    { "produto": "Tênis",    "total_quantidade": 3, "total_receita": 599.7  },
    { "produto": "Camiseta", "total_quantidade": 9, "total_receita": 449.1  },
    { "produto": "Calça",    "total_quantidade": 3, "total_receita": 299.7  }
  ]
}
```

---

## Testes

### Executar todos os testes com cobertura

```bash
pytest
```



### Executar sem verificação de cobertura

```bash
pytest --no-cov
```

---

## Estrutura do Projeto

```
vendas-cli/
├── vendas_cli/
│   ├── __init__.py     # versão do pacote
│   ├── parser.py       # leitura e validação do CSV
│   ├── core.py         # agregações e cálculos de negócio
│   ├── output.py       # formatação text/JSON
│   └── cli.py          # ponto de entrada CLI (argparse)
├── tests/
│   ├── conftest.py     # fixtures compartilhadas
│   ├── test_parser.py  # testes do módulo parser
│   ├── test_core.py    # testes do módulo core
│   ├── test_output.py  # testes do módulo output
│   └── test_cli.py     # testes de integração da CLI
├── pyproject.toml          # configuração do pacote e pytest
└── README.md
```

---

## Motivações técnicas

**Sem dependências externas** — o projeto usa apenas a stdlib do Python (`csv`, `argparse`, `logging`, `dataclasses`, `json`, `pathlib`), facilitando instalação em qualquer ambiente.

**Coluna `data_venda` opcional** — o código detecta automaticamente se a coluna existe e emite aviso no log caso filtros de data sejam passados sem ela.

**Encoding automático** — tenta UTF-8, UTF-8 BOM, Latin-1 e CP1252 em sequência, cobrindo arquivos gerados por Excel brasileiro.

**Gerador em vez de lista** — `read_csv` é um `Iterator[SaleRecord]`, permitindo processar arquivos grandes sem carregar tudo na memória.

**Módulos desacoplados** — `parser` não conhece `core`; `core` não conhece `output`; `cli` orquestra todos. Fácil de testar isoladamente.
