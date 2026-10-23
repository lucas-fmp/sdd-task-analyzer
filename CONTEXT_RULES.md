# CONTEXT_RULES - TaskAnalyzer

Regras persistentes para qualquer agente de IA que gerar, alterar ou revisar código neste repositório.

Antes de escrever código, leia também [`specs/task_analyzer_spec.md`](specs/task_analyzer_spec.md). Se houver conflito, a spec vence e este arquivo restringe o *como*.

## Diretrizes arquiteturais (obrigatórias)

- Linguagem mínima: Python 3.11+.
- Type hints em todas as funções e métodos.
- Seguir SRP e PEP 8.
- Docstrings no padrão Google para módulos, classes, funções e parâmetros.
- Funções pequenas, coesas, um único propósito.
- Exceções específicas, com mensagens descritivas. Sem `bare except`.
- Logs estruturados com o módulo padrão `logging`.
- Nomes descritivos. Código legível e manutenível.
- Separar validação, cálculo e montagem do relatório. Não colocar regra de negócio em script solto.

## Assinatura pública (congelada)

Único ponto de entrada público:

```python
def analyze_tasks(tarefas: list[dict]) -> dict:
```

Módulo: `src/task_analyzer.py`.

Exceção de validação, filha de `TaskAnalyzerError`:

- `TaskValidationError`

Lista vazia ou sem tarefas concluídas devolve médias e taxa `0.0`. Não é erro.

Não alterar nome, parâmetros nem tipo de retorno sem nova versão da spec. A versão 2.0 fez essa troca porque o enunciado da Fase 2 definiu o nome `analyze_tasks`.

## Proibições explícitas

- Não usar biblioteca fora da lista autorizada.
- Não alterar, remover ou adaptar os cenários de teste da spec.
- Não modificar a estrutura existente da aplicação sem autorização. A Fase 3
  autoriza explicitamente os artefatos de infraestrutura e documentação
  descritos no desafio: `.github/workflows/`, `Dockerfile`,
  `docker-compose.yml`, `.dockerignore` e os documentos adicionais em `specs/`.
- Não persistir dados em arquivo ou banco.
- Não alterar a assinatura pública de `analyze_tasks`.
- Não gerar funcionalidade nova sem teste correspondente.
- Não inserir código duplicado ou morto.
- Não assumir comportamento que a spec não descreve (campo `title`, API web, persistência, Flask).
- Não comentar o óbvio.
- Não devolver formato de saída diferente do `RelatorioMetricas`.
- Não lançar exceção quando não houver tarefas concluídas: médias e taxa ficam `0.0`.
- Não devolver tempo em minutos. A unidade do contrato é hora.

## Bibliotecas autorizadas

Obrigatória na Fase 2:

- `pytest`

Autorizadas e opcionais (a implementação pode ficar só na stdlib):

- `pandas`
- `numpy`

Sempre autorizada:

- biblioteca padrão do Python 3.11+ (`datetime`, `logging`, `statistics`, `math`, `typing`, `dataclasses`, etc.)

Não autorizadas enquanto o professor não responder o contrário:

- Flask e qualquer framework web
- ORMs, bancos, `requests`, FastAPI, Django, Streamlit, Gradio

`requirements.txt` lista somente o que for de fato usado.

## Regras de interação com IA

- Fornecer este arquivo e a spec completa antes de pedir código.
- Confirmar que a IA repetiu a assinatura, as exceções e as chaves de saída antes de gerar implementação.
- Pedir explicação quando a solução não estiver óbvia.
- Revisar criticamente todo código gerado.
- Rejeitar qualquer proposta que viole proibição, altere assinatura ou invente campo.

## Homologação humana

Nenhum código gerado por IA entra no repositório sem revisão humana. A decisão final é do autor.

1. Rodar `pytest` e cobrir os cenários da spec.
2. Conferir contrato: assinatura, campos, exceções, chaves de `indicadores_por_prioridade`.
3. Conferir qualidade: PEP 8, type hints, docstrings Google, logs, SRP.
4. Verificar que nenhuma proibição foi violada.
5. Validar o exemplo numérico do Cenário 1.
6. Só então commitar e abrir Pull Request.
