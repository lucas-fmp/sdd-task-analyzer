# Especificação SDD - TaskAnalyzer

**Versão:** 1.0  
**Data:** 8 de setembro de 2026  
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
- **Fluxo:** o cliente chama `analisar_tarefas`; o módulo valida, filtra, calcula e devolve `RelatorioMetricas`.
- **Pós-condição:** tempo médio, taxa de atraso, quantidade e indicadores por prioridade corretos.

### UC02 - Rejeitar datas inconsistentes

- **Pré-condição:** ao menos uma tarefa viola a ordem temporal das datas.
- **Pós-condição:** `DataInconsistenteError`; nenhuma métrica parcial.

### UC03 - Rejeitar conjunto sem tarefas concluídas

- **Pré-condição:** entrada estruturalmente válida, porém zero tarefas `concluída`.
- **Pós-condição:** `NenhumaTarefaConcluidaError`. Não se retorna zero.

### UC04 - Rejeitar entrada malformada

- **Pré-condição:** campo faltando, tipo errado, enumerador inválido ou entrada que não é lista de dicionários.
- **Pós-condição:** `EntradaInvalidaError`.

## 5. Requisitos

### Funcionais

| ID | Requisito |
| --- | --- |
| RF01 | Expor a função pública `analisar_tarefas(tarefas)`. |
| RF02 | Validar todos os campos obrigatórios antes de calcular. |
| RF03 | Aceitar apenas `prioridade` em `{baixa, média, alta}` e `status` em `{concluída, pendente, cancelada}`. |
| RF04 | Validar datas e lançar `DataInconsistenteError` em caso de violação. |
| RF05 | Considerar somente `status == "concluída"` nos cálculos. |
| RF06 | Tempo de uma tarefa = `data_conclusao − data_inicio` em minutos, 2 casas. |
| RF07 | Atrasada quando `data_conclusao > prazo`. Empate no prazo não é atraso. |
| RF08 | Taxa de atraso = `(atrasadas / concluídas) * 100`, 2 casas. |
| RF09 | Devolver `indicadores_por_prioridade` com chaves `baixa`, `média` e `alta`. |
| RF10 | Prioridade sem concluídas: `0`, `0.00`, `0.00`. Sem exceção. |
| RF11 | Zero concluídas no lote: `NenhumaTarefaConcluidaError`. Proibido mascarar com `0.00`. |
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

1. O cliente chama `analisar_tarefas(tarefas)`.
2. Validação estrutural: `list[dict]` com exatamente os campos do contrato.
3. Validação de enumeradores.
4. Validação temporal: `data_criacao <= data_inicio <= data_conclusao`.
5. Filtro: permanece só `concluída`.
6. Se o filtro resultar em zero, `NenhumaTarefaConcluidaError`.
7. Cálculo geral.
8. Cálculo por prioridade.
9. Montagem e retorno de `RelatorioMetricas`.
10. Falha nas etapas 2 a 6 não produz relatório parcial.

## 7. Contrato de interface

### 7.1 Entrada

```text
analisar_tarefas(tarefas: list[TarefaEntrada]) -> RelatorioMetricas
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

Não existe campo `title`. Campo extra ou ausente → `EntradaInvalidaError`.

Datas inconsistentes → `DataInconsistenteError`. Não se ignora a tarefa.

### 7.2 Saída (`RelatorioMetricas`)

| Campo | Tipo | Significado |
| --- | --- | --- |
| `tempo_medio_conclusao_min` | `float` | média em minutos, 2 casas |
| `taxa_atraso_percentual` | `float` | 0.00 a 100.00, 2 casas |
| `quantidade_tarefas` | `int` | só concluídas |
| `indicadores_por_prioridade` | `dict` | sempre as três chaves abaixo |

```text
{
  "baixa": {
    "quantidade_tarefas": int,
    "tempo_medio_conclusao_min": float,
    "taxa_atraso_percentual": float
  },
  "média": { ... },
  "alta": { ... }
}
```

A soma das três `quantidade_tarefas` é igual à `quantidade_tarefas` geral.

### 7.3 Assinatura pública (congelada)

```python
def analisar_tarefas(tarefas: list[dict]) -> dict:
```

Módulo: `src/task_analyzer.py`.

### 7.4 Exceções

Todas herdam de `TaskAnalyzerError`.

| Exceção | Quando | Mensagem deve conter |
| --- | --- | --- |
| `EntradaInvalidaError` | tipo errado, campo faltando/extra, enumerador inválido, `id_tarefa <= 0`, id duplicado | o que falhou e, se possível, o `id_tarefa` |
| `DataInconsistenteError` | quebra de `data_criacao <= data_inicio <= data_conclusao` | `id_tarefa` e as duas datas |
| `NenhumaTarefaConcluidaError` | zero concluídas após validação | quantidade recebida e quantidade concluída (0) |

### 7.5 Regras de negócio

- RN01. Só `concluída` entra nos cálculos.
- RN02. Tempo = `(data_conclusao − data_inicio)` em minutos, 2 casas.
- RN03. Atrasada ⇔ `data_conclusao > prazo`.
- RN04. Taxa = `(atrasadas / concluídas) * 100`.
- RN05. Data inconsistente → exceção. Não se ignora.
- RN06. Zero concluídas → exceção. Não se retorna `0.00`.
- RN07. Prioridade vazia → `0` / `0.00` / `0.00`.
- RN08. UTC.
- RN09. 2 casas decimais.
- RN10. Sem persistência.
- RN11. Sem campos fora da tabela.
- RN12. ids únicos no lote.

## 8. Cenários de aceite

### Cenário 1 - Sucesso (métricas corretas)

**Dado** um conjunto válido com prioridades e status misturados  
**Quando** `analisar_tarefas` for executada  
**Então** considera só as concluídas e devolve métricas gerais e por prioridade corretas.

Exemplo numérico (UTC):

| id_tarefa | data_criacao | data_inicio | data_conclusao | prazo | prioridade | status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-01-01 08:00 | 2026-01-01 09:00 | 2026-01-01 10:00 | 2026-01-01 11:00 | alta | concluída |
| 2 | 2026-01-01 08:00 | 2026-01-01 09:00 | 2026-01-01 12:00 | 2026-01-01 11:00 | alta | concluída |
| 3 | 2026-01-01 08:00 | 2026-01-01 09:00 | 2026-01-01 10:30 | 2026-01-01 12:00 | média | concluída |
| 4 | 2026-01-01 08:00 | 2026-01-01 09:00 | 2026-01-01 09:30 | 2026-01-01 10:00 | baixa | pendente |
| 5 | 2026-01-01 08:00 | 2026-01-01 09:00 | 2026-01-01 11:00 | 2026-01-01 10:00 | baixa | cancelada |

Resultado esperado:

- concluídas: ids 1, 2 e 3 → `quantidade_tarefas = 3`
- tempos: 60.00, 180.00, 90.00 → média geral `110.00`
- atrasada: só id 2 → taxa geral `33.33`
- `alta`: qtd 2, tempo `120.00`, taxa `50.00`
- `média`: qtd 1, tempo `90.00`, taxa `0.00`
- `baixa`: qtd 0, tempo `0.00`, taxa `0.00`

### Cenário 2 - Data inconsistente

**Dado** `data_conclusao` anterior a `data_inicio` (ou `data_inicio` anterior a `data_criacao`)  
**Quando** a função for executada  
**Então** lança `DataInconsistenteError` identificando o `id_tarefa`.

### Cenário 3 - Zero tarefas concluídas

**Dado** lista vazia ou só `pendente`/`cancelada`  
**Quando** a função for executada  
**Então** lança `NenhumaTarefaConcluidaError`.

### Cenário 4 - Entrada malformada

**Dado** campo ausente, `prioridade="urgente"`, `status="done"` ou `id_tarefa` duplicado  
**Quando** a função for executada  
**Então** lança `EntradaInvalidaError`.

Os Cenários 2 e 3 decompõem o “Cenário 2 - Exceção/Erro” do enunciado da disciplina para ficar testável.

## 9. Test Harness previsto (Fase 2)

Arquivo obrigatório: `tests/test_harness.py`.

- `test_cenario_sucesso_metricas_corretas`
- `test_ignora_pendente_e_cancelada`
- `test_prioridade_sem_concluidas_retorna_zero`
- `test_data_conclusao_antes_do_inicio_lanca_data_inconsistente`
- `test_data_inicio_antes_da_criacao_lanca_data_inconsistente`
- `test_lista_sem_concluidas_lanca_nenhuma_tarefa_concluida`
- `test_lista_vazia_lanca_nenhuma_tarefa_concluida`
- `test_prioridade_invalida_lanca_entrada_invalida`
- `test_id_duplicado_lanca_entrada_invalida`
- `test_assinatura_publica_existe_e_nao_foi_alterada`

É proibido apagar, renomear ou enfraquecer esses cenários na Fase 2.

## 10. Decisões da versão 1.0

- Campos: contrato formal (`id_tarefa`, `data_criacao`, `data_inicio`, `data_conclusao`, `prazo`, `prioridade`, `status`). Sem `title`.
- Datas inconsistentes: `DataInconsistenteError`.
- Zero concluídas: `NenhumaTarefaConcluidaError`.
- `indicadores_por_prioridade`: dict fixo com `baixa` / `média` / `alta`.
- Função pública: `analisar_tarefas(tarefas: list[dict]) -> dict`.
- Bibliotecas: stdlib + `pytest` + pandas/numpy opcionais. Sem Flask.
