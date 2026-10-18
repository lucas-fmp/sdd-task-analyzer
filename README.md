# TaskAnalyzer

Módulo Python de análise de produtividade de tarefas. Projeto da disciplina **Bootcamp III** (UniCEUB), desenvolvido com **Spec-Driven Development (SDD)** e governança de contexto para agentes de IA.

Autor: **Lucas Fernando Macedo Pereira**  
Curso: Ciência da Computação - Campus Asa Norte, turma 2024-2  
Especificação: versão 2.0 (17 de outubro de 2026)

## O que este repositório é nesta fase

A **Fase 2** implementa `analyze_tasks` e o Test Harness em `pytest`. O enunciado desta fase fechou a função, a unidade (horas) e o caso sem concluídas (`0.0`). A spec vigente é a versão 2.0.

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
├── requirements.txt
├── specs/
│   └── task_analyzer_spec.md # contrato SDD (fonte da verdade)
├── tests/
│   └── test_harness.py       # Test Harness (pytest) - Fase 2
└── src/
    └── task_analyzer.py      # implementação - Fase 2
```

## Contrato público (congelado)

```python
def analyze_tasks(tarefas: list[dict]) -> dict:
```

Exceção de validação:

- `TaskValidationError`

Sem tarefas concluídas, médias e taxa voltam `0.0`.

Detalhes de campos, regras e exemplos numéricos: [`specs/task_analyzer_spec.md`](specs/task_analyzer_spec.md).  
Regras para geração de código: [`CONTEXT_RULES.md`](CONTEXT_RULES.md).

## Como rodar (a partir da Fase 2)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/test_harness.py -v
```

Python mínimo: **3.11+**.

## Fases do projeto

| Fase | Conteúdo | Status |
| --- | --- | --- |
| 1 | Especificação SDD, `CONTEXT_RULES`, estrutura do repositório, vídeo | concluída |
| 2 | Código gerado com IA, pytest, Git Flow e Pull Requests | esta entrega |
| 3 | GitHub Actions, Docker, relatório de governança e ética | depois |

## Bibliotecas autorizadas

- biblioteca padrão do Python 3.11+;
- `pytest` (obrigatório nos testes);
- `pandas` e `numpy` (opcionais; confirmados pelo professor).

Qualquer outra biblioteca exige autorização prévia. Flask e frameworks web estão fora do escopo.
