"""Test Harness do TaskAnalyzer.

Os casos abaixo materializam os cenários de aceite da spec. Na Fase 1 eles
ficam marcados como skip; na Fase 2 a implementação deve fazê-los passar.
É proibido apagar, renomear ou enfraquecer estes testes.
"""

from __future__ import annotations

import inspect

import pytest

from src.task_analyzer import analisar_tarefas


def test_assinatura_publica_existe_e_nao_foi_alterada() -> None:
    """A função pública congelada no contrato deve existir com 1 parâmetro."""
    assert callable(analisar_tarefas)
    parametros = list(inspect.signature(analisar_tarefas).parameters)
    assert parametros == ["tarefas"]


@pytest.mark.skip(reason="Implementação na Fase 2")
def test_cenario_sucesso_metricas_corretas() -> None:
    """Cenário 1 - métricas gerais e por prioridade do exemplo numérico."""


@pytest.mark.skip(reason="Implementação na Fase 2")
def test_ignora_pendente_e_cancelada() -> None:
    """Pendentes e canceladas não entram em quantidade, tempo nem atraso."""


@pytest.mark.skip(reason="Implementação na Fase 2")
def test_prioridade_sem_concluidas_retorna_zero() -> None:
    """Prioridade sem concluídas devolve 0 / 0.00 / 0.00."""


@pytest.mark.skip(reason="Implementação na Fase 2")
def test_data_conclusao_antes_do_inicio_lanca_data_inconsistente() -> None:
    """Cenário 2 - data_conclusao < data_inicio."""


@pytest.mark.skip(reason="Implementação na Fase 2")
def test_data_inicio_antes_da_criacao_lanca_data_inconsistente() -> None:
    """Cenário 2 - data_inicio < data_criacao."""


@pytest.mark.skip(reason="Implementação na Fase 2")
def test_lista_sem_concluidas_lanca_nenhuma_tarefa_concluida() -> None:
    """Cenário 3 - só pendente/cancelada."""


@pytest.mark.skip(reason="Implementação na Fase 2")
def test_lista_vazia_lanca_nenhuma_tarefa_concluida() -> None:
    """Cenário 3 - lista vazia."""


@pytest.mark.skip(reason="Implementação na Fase 2")
def test_prioridade_invalida_lanca_entrada_invalida() -> None:
    """Cenário 4 - prioridade fora do enumerador."""


@pytest.mark.skip(reason="Implementação na Fase 2")
def test_id_duplicado_lanca_entrada_invalida() -> None:
    """Cenário 4 - id_tarefa repetido no lote."""
