# TaskAnalyzer

Módulo Python de análise de produtividade de tarefas. Projeto da disciplina **Bootcamp III** (UniCEUB), desenvolvido com **Spec-Driven Development (SDD)** e governança de contexto para agentes de IA.

Autor: **Lucas Fernando Macedo Pereira**  
Curso: Ciência da Computação - Campus Asa Norte, turma 2024-2  
Especificação: versão 1.0 (8 de setembro de 2026)

## O que este repositório é nesta fase

Esta é a **Fase 1**: planejamento e especificação. O contrato executável já está fechado; a implementação e os testes automatizados entram na **Fase 2**.

O TaskAnalyzer recebe uma lista de tarefas em memória e devolve métricas:

- tempo médio de conclusão (minutos);
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
def analisar_tarefas(tarefas: list[dict]) -> dict:
```

Exceções de domínio:

- `EntradaInvalidaError`
- `DataInconsistenteError`
- `NenhumaTarefaConcluidaError`

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
| 1 | Especificação SDD, `CONTEXT_RULES`, estrutura do repositório, vídeo | em andamento |
| 2 | Código gerado com IA, pytest, Git Flow e Pull Requests | próxima |
| 3 | GitHub Actions, Docker, relatório de governança e ética | depois |

## Bibliotecas autorizadas

- biblioteca padrão do Python 3.11+;
- `pytest` (obrigatório nos testes);
- `pandas` e `numpy` (opcionais; confirmados pelo professor).

Qualquer outra biblioteca exige autorização prévia. Flask e frameworks web estão fora do escopo.
