# TaskAnalyzer

Módulo Python de análise de produtividade de tarefas. Projeto da disciplina **Bootcamp III** (UniCEUB), desenvolvido com **Spec-Driven Development (SDD)** e governança de contexto para agentes de IA.

Autor: **Lucas Fernando Macedo Pereira**  
Curso: Ciência da Computação - Campus Asa Norte, turma 2024-2  
Especificação: versão 2.0 (17 de outubro de 2026)

## O que este repositório é nesta fase

A **Fase 3** preserva a implementação da Fase 2 e adiciona uma esteira reproduzível
de validação. O código pode ser testado localmente, no GitHub Actions e em um
contêiner Docker baseado em Python 3.11.

O TaskAnalyzer recebe uma lista de tarefas em memória e devolve métricas:

- tempo médio de conclusão (horas);
- taxa de atraso percentual;
- quantidade de tarefas concluídas;
- os mesmos indicadores quebrados por prioridade (`baixa`, `média`, `alta`).

Ele não gerencia tarefas, não tem interface web e não persiste dados.

## Estrutura

```text
sdd-task-analyzer/
├── README.md
├── CONTEXT_RULES.md          # regras persistentes para a IA
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .github/
│   └── workflows/
│       └── ci.yml            # testes Python e Docker no GitHub Actions
├── specs/
│   ├── task_analyzer_spec.md # contrato SDD (fonte da verdade)
│   ├── requirements.yaml     # requisitos e rastreabilidade
│   └── system_design_document.pdf
├── tests/
│   └── test_harness.py       # Test Harness (pytest)
└── src/
    └── task_analyzer.py      # implementação aprovada
```

## Contrato público (congelado)

```python
def analyze_tasks(tarefas: list[dict]) -> dict:
```

Exceção de validação:

- `TaskValidationError`

Sem tarefas concluídas, médias e taxa voltam `0.0`, sem exceção.

Detalhes de campos, regras e exemplos numéricos: [`specs/task_analyzer_spec.md`](specs/task_analyzer_spec.md).  
Regras para geração de código: [`CONTEXT_RULES.md`](CONTEXT_RULES.md).

## Como rodar localmente

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest tests/test_harness.py -v
```

Python mínimo: **3.11+**.

## Como rodar com Docker

O Compose constrói uma imagem isolada, sem bind mount do ambiente local, e executa
o mesmo Test Harness usado na CI:

```bash
docker compose config
docker compose build tests
docker compose run --rm tests
```

O `Dockerfile` usa `python:3.11-slim` e executa os testes com um usuário não-root.

## Integração contínua

O workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) é disparado em
pushes e Pull Requests para `main` e `develop`. Ele:

1. configura Ubuntu com Python 3.11;
2. instala `requirements.txt`;
3. executa `python -m pytest tests/test_harness.py -v`;
4. constrói a imagem Docker e executa a suíte no Compose.

O selo verde aparece no GitHub quando o workflow roda em um push ou Pull Request para `main` ou `develop`.

## Fases do projeto

| Fase | Conteúdo | Status |
| --- | --- | --- |
| 1 | Especificação SDD, `CONTEXT_RULES`, estrutura do repositório, vídeo | concluída |
| 2 | Código gerado com IA, pytest, Git Flow e Pull Requests | concluída |
| 3 | GitHub Actions, Docker, rastreabilidade e governança ética | esta entrega |

## Bibliotecas autorizadas

- biblioteca padrão do Python 3.11+;
- `pytest` (obrigatório nos testes e na CI);
- `pandas` e `numpy` (opcionais; confirmados pelo professor).

Qualquer outra biblioteca exige autorização prévia. Flask e frameworks web estão fora do escopo.

## Limites e segurança

- Os dados das tarefas permanecem em memória e não são enviados para serviços externos.
- O módulo não toma decisões automáticas sobre pessoas; ele apenas calcula métricas
  descritivas.
- A análise de produtividade deve ser interpretada com contexto humano, sem usar
  uma taxa ou média isolada como critério disciplinar.
