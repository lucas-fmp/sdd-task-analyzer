# Especificação SDD - TaskAnalyzer

**Versão:** 2.0  
**Data:** 17 de outubro de 2026  
**Autor:** Lucas Fernando Macedo Pereira  
**Curso:** Ciência da Computação - Campus Asa Norte, turma 2024-2  
**E-mail:** lucaspereira.lp@sempreceub.com

Este arquivo é o contrato executável do módulo. A implementação da Fase 2 deve segui-lo à risca.

---

## 1. Problema de negócio

Equipes que executam tarefas no dia a dia costumam saber o que foi feito, mas não conseguem medir com objetividade como o trabalho está performando. Sem métricas padronizadas, fica difícil responder:

- quanto tempo, em média, uma tarefa leva para ser concluída?
- qual percentual das tarefas concluídas estourou o prazo?
- a prioridade alta está realmente saindo mais rápido do que a baixa, ou só parece?

O TaskAnalyzer recebe um conjunto de tarefas já registradas e devolve um relatório numérico, determinístico e auditável. Ele não gerencia tarefas, não substitui um kanban e não persiste dados. Ele apenas analisa.

## 2. Escopo

**Dentro do escopo**

- receber uma lista de tarefas em memória;
- validar estrutura, tipos, enumeradores e consistência de datas;
- calcular tempo médio de conclusão, taxa de atraso e indicadores por prioridade;
- lançar exceções específicas quando a entrada for inválida ou quando não houver tarefas concluídas;
- registrar logs estruturados;
- disponibilizar testes automatizados (`pytest`) que proveem este contrato.

**Fora do escopo**

- interface gráfica ou site (Flask ou similar);
- banco de dados, arquivos persistidos ou API HTTP;
- autenticação, multi-usuário ou painel gerencial;
- campo título da tarefa;
- previsão, machine learning ou recomendação;
- edição, criação ou exclusão de tarefas.

## 3. Premissas

- Todas as datas e horários estão em UTC.
- Tempos e percentuais são arredondados com 2 casas decimais (half even, padrão do Python).
- A unidade de tempo é o minuto.
- O módulo é puro em relação a I/O: não lê nem grava arquivos ou banco.
- A responsabilidade técnica do código gerado por IA permanece humana.

## 4. Casos de uso

### UC01 - Analisar produtividade de um conjunto válido

- **Pré-condição:** ao menos uma tarefa `concluída`; todos os campos válidos; datas consistentes.
- **Fluxo:** o cliente chama `analyze_tasks`; o módulo valida, filtra, calcula e devolve `RelatorioMetricas`.
- **Pós-condição:** tempo médio, taxa de atraso, quantidade e indicadores por prioridade corretos.

### UC02 - Rejeitar datas inconsistentes

- **Pré-condição:** ao menos uma tarefa viola a ordem temporal das datas.
- **Pós-condição:** `TaskValidationError`; nenhuma métrica parcial.

### UC03 - Rejeitar conjunto sem tarefas concluídas

- **Pré-condição:** entrada estruturalmente válida, porém zero tarefas `concluída`.
- **Pós-condição:** o relatório volta com médias e taxa em `0.0`. Não há exceção.

### UC04 - Rejeitar entrada malformada

- **Pré-condição:** campo faltando, tipo errado, enumerador inválido ou entrada que não é lista de dicionários.
- **Pós-condição:** `TaskValidationError`.

## 5. Requisitos

### Funcionais

| ID | Requisito |
| --- | --- |
| RF01 | Expor a função pública `analyze_tasks(tarefas)`. |
| RF02 | Validar todos os campos obrigatórios antes de calcular. |
| RF03 | Aceitar apenas `prioridade` em `{baixa, média, alta}` e `status` em `{concluída, pendente, cancelada}`. |
| RF04 | Validar datas e lançar `TaskValidationError` quando `data_conclusao < data_criacao`. |
| RF05 | Considerar somente `status == "concluída"` nos cálculos. |
| RF06 | Tempo de uma tarefa = `data_conclusao − data_inicio` em horas, 2 casas. |
| RF07 | Atrasada quando `data_conclusao > prazo`. Empate no prazo não é atraso. |
| RF08 | Taxa de atraso = `(atrasadas / concluídas) * 100`, 2 casas. |
| RF09 | Devolver `indicadores_por_prioridade` com chaves `baixa`, `média` e `alta`. |
| RF10 | Prioridade sem concluídas: tempo e taxa `0.0` naquela chave. Sem exceção. |
| RF11 | Zero concluídas no lote (lista vazia ou só pendente/cancelada): médias e taxa voltam `0.0`, sem exceção. |
| RF12 | Logs estruturados (início, recebidas, consideradas, sucesso ou falha). |

### Não funcionais

| ID | Requisito |
| --- | --- |
| RNF01 | Python 3.11+. |
| RNF02 | Type hints em todas as funções e métodos. |
| RNF03 | PEP 8, SRP e clean code. |
| RNF04 | Docstrings no padrão Google. |
| RNF05 | Exceções específicas; nunca `bare except`. |
| RNF06 | Logs via `logging`. |
| RNF07 | Sem persistência. |
| RNF08 | Sem bibliotecas além das autorizadas em `CONTEXT_RULES.md`. |
| RNF09 | Determinismo: mesma entrada válida, mesma saída. |
| RNF10 | Cada cenário de aceite vira teste `pytest`. |
| RNF11 | UTC em todo o contrato. |
| RNF12 | Sem interface web. |

## 6. Fluxo do sistema

1. O cliente chama `analyze_tasks(tarefas)`.
2. Validação estrutural: `list[dict]` com exatamente os campos do contrato.
3. Validação de enumeradores.
4. Validação temporal: `data_conclusao < data_criacao` lança `TaskValidationError`. A mesma exceção cobre início anterior à criação ou conclusão anterior ao início.
5. Filtro: permanece só `concluída`.
6. Se o filtro resultar em zero, médias e taxa ficam `0.0` e o relatório ainda é devolvido.
7. Cálculo geral.
8. Cálculo por prioridade.
9. Montagem e retorno de `RelatorioMetricas`.
10. Falha nas etapas 2 a 4 não produz relatório parcial.

## 7. Contrato de interface

### 7.1 Entrada

```text
analyze_tasks(tarefas: list[TarefaEntrada]) -> RelatorioMetricas
```

| Campo | Tipo | Obrigatório | Domínio |
| --- | --- | --- | --- |
| `id_tarefa` | `int` | sim | único no lote, `> 0` |
| `data_criacao` | `datetime` | sim | UTC |
| `data_inicio` | `datetime` | sim | UTC |
| `data_conclusao` | `datetime` | sim | UTC (obrigatório também em pendente/cancelada; essas não entram no cálculo) |
| `prazo` | `datetime` | sim | UTC |
| `prioridade` | `str` | sim | `baixa` \| `média` \| `alta` |
| `status` | `str` | sim | `concluída` \| `pendente` \| `cancelada` |

Não existe campo `title`. Campo extra, ausente, tipo errado ou enumerador inválido → `TaskValidationError`.

`data_conclusao < data_criacao` → `TaskValidationError`. Não se ignora a tarefa.

### 7.2 Saída (`RelatorioMetricas`)

Definida pelo enunciado da Fase 2.

| Campo | Tipo | Significado |
| --- | --- | --- |
| `total_tarefas` | `int` | todas as tarefas do lote |
| `total_concluidas` | `int` | status `concluída` |
| `total_pendentes` | `int` | status `pendente` (cancelada não entra aqui) |
| `tempo_medio_conclusao_horas` | `float` | média em horas, 2 casas; `0.0` se não houver concluída |
| `taxa_atraso_percentual` | `float` | 0.00 a 100.00; `0.0` se não houver concluída |
| `indicadores_por_prioridade` | `dict` | sempre `baixa`, `média` e `alta` |

```text
{
  "baixa": {
    "tempo_medio_conclusao_horas": float,
    "taxa_atraso_percentual": float
  },
  "média": { ... },
  "alta": { ... }
}
```

### 7.3 Assinatura pública

```python
def analyze_tasks(tarefas: list[dict]) -> dict:
```

Módulo: `src/task_analyzer.py`.

### 7.4 Exceção

`TaskValidationError` herda de `TaskAnalyzerError`.

| Quando | Mensagem deve conter |
| --- | --- |
| tipo errado, campo faltando/extra, enumerador inválido, `id_tarefa <= 0`, id duplicado | o que falhou e, se possível, o `id_tarefa` |
| `data_conclusao < data_criacao` (e as outras inversões de data) | `id_tarefa` e as duas datas |

Lista vazia ou lote sem concluídas não é exceção.

### 7.5 Regras de negócio

- RN01. Só `concluída` entra no tempo médio e na taxa de atraso.
- RN02. Tempo = `(data_conclusao − data_inicio)` em horas, 2 casas.
- RN03. Atrasada ⇔ `data_conclusao > prazo`.
- RN04. Taxa = `(atrasadas / concluídas) * 100`. Sem concluídas, a taxa é `0.0`.
- RN05. `data_conclusao < data_criacao` → `TaskValidationError`. Não se ignora.
- RN06. Zero concluídas → médias e taxa `0.0`. Não se lança exceção.
- RN07. Prioridade sem concluídas → `0.0` / `0.0` naquela chave.
- RN08. UTC.
- RN09. 2 casas decimais.
- RN10. Sem persistência.
- RN11. Sem campos fora da tabela.
- RN12. ids únicos no lote.

## 8. Cenários de aceite

### Cenário 1 - Sucesso (métricas corretas)

**Dado** um conjunto válido com prioridades e status misturados  
**Quando** `analyze_tasks` for executada  
**Então** considera só as concluídas no tempo e no atraso, e devolve totais, média em horas e taxa, no geral e por prioridade.

Exemplo numérico (UTC):

| id_tarefa | data_criacao | data_inicio | data_conclusao | prazo | prioridade | status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-01-01 08:00 | 2026-01-01 09:00 | 2026-01-01 10:00 | 2026-01-01 11:00 | alta | concluída |
| 2 | 2026-01-01 08:00 | 2026-01-01 09:00 | 2026-01-01 12:00 | 2026-01-01 11:00 | alta | concluída |
| 3 | 2026-01-01 08:00 | 2026-01-01 09:00 | 2026-01-01 10:30 | 2026-01-01 12:00 | média | concluída |
| 4 | 2026-01-01 08:00 | 2026-01-01 09:00 | 2026-01-01 09:30 | 2026-01-01 10:00 | baixa | pendente |
| 5 | 2026-01-01 08:00 | 2026-01-01 09:00 | 2026-01-01 11:00 | 2026-01-01 10:00 | baixa | cancelada |

Resultado esperado:

- `total_tarefas = 5`, `total_concluidas = 3`, `total_pendentes = 1`
- durações: 1.00 h, 3.00 h e 1.50 h → média geral `1.83`
- atrasada: só id 2 → taxa geral `33.33`
- `alta`: tempo `2.00`, taxa `50.00`
- `média`: tempo `1.50`, taxa `0.00`
- `baixa`: tempo `0.00`, taxa `0.00`

### Cenário 2 - Data inconsistente

**Dado** `data_conclusao` anterior a `data_criacao`  
**Quando** a função for executada  
**Então** lança `TaskValidationError` identificando o `id_tarefa`.

### Cenário 3 - Zero tarefas concluídas

**Dado** lista vazia ou só `pendente`/`cancelada`  
**Quando** a função for executada  
**Então** devolve médias e taxa `0.0`, sem exceção.

### Cenário 4 - Entrada malformada

**Dado** campo ausente, `prioridade="urgente"`, `status="done"` ou `id_tarefa` duplicado  
**Quando** a função for executada  
**Então** lança `TaskValidationError`.

## 9. Test Harness

Arquivo obrigatório: `tests/test_harness.py`.

- `test_cenario_sucesso_metricas_corretas`
- `test_ignora_pendente_e_cancelada`
- `test_prioridade_sem_concluidas_retorna_zero`
- `test_data_conclusao_antes_da_criacao_lanca_task_validation_error`
- `test_lista_sem_concluidas_retorna_zero`
- `test_lista_vazia_retorna_zero`
- `test_prioridade_invalida_lanca_task_validation_error`
- `test_id_duplicado_lanca_task_validation_error`
- `test_assinatura_publica_existe_e_nao_foi_alterada`

## 10. Decisões

Versão 1.0 (Fase 1) usava `analisar_tarefas`, minutos e exceção quando não havia concluídas. O enunciado da Fase 2 fechou esses três pontos. A versão 2.0 adota o que ficou definido:

- Função pública: `analyze_tasks(tarefas: list[dict]) -> dict`.
- Exceção única de validação: `TaskValidationError`.
- Tempo em horas (`tempo_medio_conclusao_horas`), geral e por prioridade.
- Totais: `total_tarefas`, `total_concluidas`, `total_pendentes`.
- Lista vazia ou sem concluídas: médias e taxa `0.0`, sem exceção.
- Campos de entrada continuam os da Fase 1. Sem `title`.
- Bibliotecas: stdlib + `pytest`. Sem Flask.
