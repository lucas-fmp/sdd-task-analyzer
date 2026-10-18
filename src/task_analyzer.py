"""Analisa tarefas e devolve métricas de produtividade.

O contrato está em ``specs/task_analyzer_spec.md``. Este módulo valida a
entrada, calcula tempo médio e taxa de atraso e não persiste dados.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_CAMPOS_OBRIGATORIOS = (
    "id_tarefa",
    "data_criacao",
    "data_inicio",
    "data_conclusao",
    "prazo",
    "prioridade",
    "status",
)
_PRIORIDADES = ("baixa", "média", "alta")
_STATUS = ("concluída", "pendente", "cancelada")
_CAMPOS_DATA = ("data_criacao", "data_inicio", "data_conclusao", "prazo")


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
    recebidas = len(tarefas) if isinstance(tarefas, list) else "entrada_invalida"
    logger.info("analise_iniciada quantidade_recebida=%s", recebidas)
    try:
        validadas = _validar_entrada(tarefas)
        concluidas = _filtrar_concluidas(validadas)
        if not concluidas:
            raise NenhumaTarefaConcluidaError(
                f"quantidade_recebida={len(validadas)} quantidade_concluida=0"
            )
        relatorio = _montar_relatorio(concluidas)
    except TaskAnalyzerError:
        logger.error("analise_falhou quantidade_recebida=%s", recebidas)
        raise
    logger.info(
        "analise_concluida quantidade_recebida=%s quantidade_considerada=%s",
        recebidas,
        relatorio["quantidade_tarefas"],
    )
    return relatorio


def _validar_entrada(tarefas: list[dict]) -> list[dict]:
    """Valida a lista inteira e devolve as tarefas aceitas.

    Args:
        tarefas: Entrada bruta da função pública.

    Returns:
        A mesma lista, depois das validações estrutural, de tipo e de data.

    Raises:
        EntradaInvalidaError: A lista ou algum item não cumpre o contrato.
        DataInconsistenteError: Alguma tarefa quebra a ordem das datas.
    """
    if not isinstance(tarefas, list):
        raise EntradaInvalidaError("a entrada deve ser uma lista de dicionários")
    validadas: list[dict] = []
    ids_vistos: set[int] = set()
    for indice, tarefa in enumerate(tarefas):
        _validar_tarefa(tarefa, indice)
        _validar_datas(tarefa)
        identificador = tarefa["id_tarefa"]
        if identificador in ids_vistos:
            raise EntradaInvalidaError(f"id_tarefa={identificador} duplicado no lote")
        ids_vistos.add(identificador)
        validadas.append(tarefa)
    return validadas


def _validar_tarefa(tarefa: object, indice: int) -> None:
    """Confere campos, tipos e enumeradores de uma tarefa.

    Args:
        tarefa: Item da lista recebida.
        indice: Posição do item, usada na mensagem quando ainda não há id.

    Raises:
        EntradaInvalidaError: Campo, tipo ou enumerador fora do contrato.
    """
    if not isinstance(tarefa, dict):
        raise EntradaInvalidaError(f"item {indice} não é um dicionário")
    faltando = [campo for campo in _CAMPOS_OBRIGATORIOS if campo not in tarefa]
    extras = [campo for campo in tarefa if campo not in _CAMPOS_OBRIGATORIOS]
    if faltando or extras:
        raise EntradaInvalidaError(
            f"item {indice} campos_faltando={faltando} campos_extras={extras}"
        )
    _validar_id(tarefa)
    _validar_datetimes(tarefa)
    if tarefa["prioridade"] not in _PRIORIDADES:
        raise EntradaInvalidaError(
            f"id_tarefa={tarefa['id_tarefa']} prioridade inválida: {tarefa['prioridade']!r}"
        )
    if tarefa["status"] not in _STATUS:
        raise EntradaInvalidaError(
            f"id_tarefa={tarefa['id_tarefa']} status inválido: {tarefa['status']!r}"
        )


def _validar_id(tarefa: dict) -> None:
    """Garante id inteiro, positivo e único no formato.

    Args:
        tarefa: Tarefa já com a chave ``id_tarefa``.

    Raises:
        EntradaInvalidaError: Id ausente no tipo certo ou menor ou igual a zero.
    """
    identificador = tarefa["id_tarefa"]
    if isinstance(identificador, bool) or not isinstance(identificador, int):
        raise EntradaInvalidaError(f"id_tarefa inválido: {identificador!r}")
    if identificador <= 0:
        raise EntradaInvalidaError(f"id_tarefa={identificador} deve ser > 0")


def _validar_datetimes(tarefa: dict) -> None:
    """Garante que os quatro campos de data são datetime em UTC.

    Args:
        tarefa: Tarefa com as chaves de data presentes.

    Raises:
        EntradaInvalidaError: Valor que não é datetime ou que não está em UTC.
    """
    for campo in _CAMPOS_DATA:
        valor = tarefa[campo]
        if not isinstance(valor, datetime):
            raise EntradaInvalidaError(
                f"id_tarefa={tarefa['id_tarefa']} {campo} deve ser datetime"
            )
        if valor.tzinfo is not None and valor.utcoffset() != timezone.utc.utcoffset(valor):
            raise EntradaInvalidaError(
                f"id_tarefa={tarefa['id_tarefa']} {campo} deve estar em UTC"
            )


def _validar_datas(tarefa: dict) -> None:
    """Exige data_criacao <= data_inicio <= data_conclusao.

    Args:
        tarefa: Tarefa com datetimes já validados.

    Raises:
        DataInconsistenteError: A ordem temporal foi violada.
    """
    criacao = tarefa["data_criacao"]
    inicio = tarefa["data_inicio"]
    conclusao = tarefa["data_conclusao"]
    identificador = tarefa["id_tarefa"]
    if criacao > inicio:
        raise DataInconsistenteError(
            f"id_tarefa={identificador} data_criacao={criacao.isoformat()} "
            f"data_inicio={inicio.isoformat()}"
        )
    if inicio > conclusao:
        raise DataInconsistenteError(
            f"id_tarefa={identificador} data_inicio={inicio.isoformat()} "
            f"data_conclusao={conclusao.isoformat()}"
        )


def _filtrar_concluidas(tarefas: list[dict]) -> list[dict]:
    """Mantém só as tarefas com status concluída.

    Args:
        tarefas: Lote já validado.

    Returns:
        Sublista das tarefas concluídas, na ordem original.
    """
    return [tarefa for tarefa in tarefas if tarefa["status"] == "concluída"]


def _tempo_minutos(tarefa: dict) -> float:
    """Calcula a duração da tarefa em minutos.

    Args:
        tarefa: Tarefa concluída com datas consistentes.

    Returns:
        Minutos entre o início e a conclusão.
    """
    delta = tarefa["data_conclusao"] - tarefa["data_inicio"]
    return delta.total_seconds() / 60


def _esta_atrasada(tarefa: dict) -> bool:
    """Indica se a conclusão passou do prazo.

    Args:
        tarefa: Tarefa concluída.

    Returns:
        True quando data_conclusao é estritamente maior que prazo.
    """
    return tarefa["data_conclusao"] > tarefa["prazo"]


def _indicadores(tarefas: list[dict]) -> dict[str, int | float]:
    """Monta quantidade, tempo médio e taxa de atraso de um grupo.

    Args:
        tarefas: Tarefas concluídas do grupo. Pode ser vazia.

    Returns:
        Indicadores do grupo. Grupo vazio devolve zeros, sem divisão.
    """
    if not tarefas:
        return {
            "quantidade_tarefas": 0,
            "tempo_medio_conclusao_min": 0.0,
            "taxa_atraso_percentual": 0.0,
        }
    tempos = [_tempo_minutos(tarefa) for tarefa in tarefas]
    atrasadas = sum(1 for tarefa in tarefas if _esta_atrasada(tarefa))
    return {
        "quantidade_tarefas": len(tarefas),
        "tempo_medio_conclusao_min": round(sum(tempos) / len(tempos), 2),
        "taxa_atraso_percentual": round(atrasadas / len(tarefas) * 100, 2),
    }


def _montar_relatorio(concluidas: list[dict]) -> dict:
    """Agrega o relatório geral e o recorte por prioridade.

    Args:
        concluidas: Tarefas concluídas. A lista não pode ser vazia.

    Returns:
        RelatorioMetricas no formato do contrato.
    """
    geral = _indicadores(concluidas)
    por_prioridade = {
        prioridade: _indicadores(
            [tarefa for tarefa in concluidas if tarefa["prioridade"] == prioridade]
        )
        for prioridade in _PRIORIDADES
    }
    return {
        "tempo_medio_conclusao_min": geral["tempo_medio_conclusao_min"],
        "taxa_atraso_percentual": geral["taxa_atraso_percentual"],
        "quantidade_tarefas": geral["quantidade_tarefas"],
        "indicadores_por_prioridade": por_prioridade,
    }
