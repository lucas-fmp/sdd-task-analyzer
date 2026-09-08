"""Módulo TaskAnalyzer.

A implementação das métricas ocorre na Fase 2. Este arquivo congela a
assinatura pública e as exceções de domínio definidas na especificação SDD.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class TaskAnalyzerError(Exception):
    """Erro de domínio do TaskAnalyzer."""


class EntradaInvalidaError(TaskAnalyzerError):
    """Entrada malformada, tipo incorreto ou enumerador inválido."""


class DataInconsistenteError(TaskAnalyzerError):
    """Datas violam data_criacao <= data_inicio <= data_conclusao."""


class NenhumaTarefaConcluidaError(TaskAnalyzerError):
    """Não há tarefas concluídas; calcular métricas causaria divisão por zero."""


def analisar_tarefas(tarefas: list[dict]) -> dict:
    """Analisa um conjunto de tarefas e devolve métricas de produtividade.

    Args:
        tarefas: Lista de dicionários no formato TarefaEntrada da spec.

    Returns:
        RelatorioMetricas com tempo médio, taxa de atraso, quantidade e
        indicadores por prioridade.

    Raises:
        EntradaInvalidaError: Estrutura, tipo ou enumerador inválido.
        DataInconsistenteError: Ordem temporal das datas violada.
        NenhumaTarefaConcluidaError: Nenhuma tarefa com status concluída.
    """
    logger.info("analisar_tarefas chamado; implementação na Fase 2")
    raise NotImplementedError(
        "Implementação prevista para a Fase 2. "
        "Siga specs/task_analyzer_spec.md e CONTEXT_RULES.md."
    )
