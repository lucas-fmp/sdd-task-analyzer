"""Analisa tarefas e devolve métricas de produtividade.

O contrato vigente é a versão 2.0 de ``specs/task_analyzer_spec.md``.
O tempo sai em horas. Lote sem tarefas concluídas devolve 0.0.
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


class TaskValidationError(TaskAnalyzerError):
    """Entrada inválida ou datas inconsistentes."""


def analyze_tasks(tarefas: list[dict]) -> dict:
    """Analisa um conjunto de tarefas e devolve métricas de produtividade.

    Args:
        tarefas: Lista de dicionários no formato TarefaEntrada da spec.

    Returns:
        RelatorioMetricas com totais, tempo médio em horas, taxa de atraso
        e os mesmos indicadores por prioridade. Sem concluídas, as médias
        e a taxa são 0.0.

    Raises:
        TaskValidationError: Estrutura, tipo, enumerador ou data inválidos.
    """
    recebidas = len(tarefas) if isinstance(tarefas, list) else "entrada_invalida"
    logger.info("analise_iniciada quantidade_recebida=%s", recebidas)
    try:
        validadas = _validar_entrada(tarefas)
        relatorio = _montar_relatorio(validadas)
    except TaskAnalyzerError:
        logger.error("analise_falhou quantidade_recebida=%s", recebidas)
        raise
    logger.info(
        "analise_concluida quantidade_recebida=%s quantidade_considerada=%s",
        recebidas,
        relatorio["total_concluidas"],
    )
    return relatorio


def _validar_entrada(tarefas: list[dict]) -> list[dict]:
    """Valida a lista inteira e devolve as tarefas aceitas.

    Args:
        tarefas: Entrada bruta da função pública.

    Returns:
        A mesma lista, depois das validações estrutural, de tipo e de data.

    Raises:
        TaskValidationError: A lista, um item ou uma data não cumpre o contrato.
    """
    if not isinstance(tarefas, list):
        raise TaskValidationError("a entrada deve ser uma lista de dicionários")
    validadas: list[dict] = []
    ids_vistos: set[int] = set()
    for indice, tarefa in enumerate(tarefas):
        _validar_tarefa(tarefa, indice)
        _validar_datas(tarefa)
        identificador = tarefa["id_tarefa"]
        if identificador in ids_vistos:
            raise TaskValidationError(f"id_tarefa={identificador} duplicado no lote")
        ids_vistos.add(identificador)
        validadas.append(tarefa)
    return validadas


def _validar_tarefa(tarefa: object, indice: int) -> None:
    """Confere campos, tipos e enumeradores de uma tarefa.

    Args:
        tarefa: Item da lista recebida.
        indice: Posição do item, usada na mensagem quando ainda não há id.

    Raises:
        TaskValidationError: Campo, tipo ou enumerador fora do contrato.
    """
    if not isinstance(tarefa, dict):
        raise TaskValidationError(f"item {indice} não é um dicionário")
    faltando = [campo for campo in _CAMPOS_OBRIGATORIOS if campo not in tarefa]
    extras = [campo for campo in tarefa if campo not in _CAMPOS_OBRIGATORIOS]
    if faltando or extras:
        raise TaskValidationError(
            f"item {indice} campos_faltando={faltando} campos_extras={extras}"
        )
    _validar_id(tarefa)
    _validar_datetimes(tarefa)
    if tarefa["prioridade"] not in _PRIORIDADES:
        raise TaskValidationError(
            f"id_tarefa={tarefa['id_tarefa']} prioridade inválida: {tarefa['prioridade']!r}"
        )
    if tarefa["status"] not in _STATUS:
        raise TaskValidationError(
            f"id_tarefa={tarefa['id_tarefa']} status inválido: {tarefa['status']!r}"
        )


def _validar_id(tarefa: dict) -> None:
    """Garante id inteiro e positivo.

    Args:
        tarefa: Tarefa já com a chave ``id_tarefa``.

    Raises:
        TaskValidationError: Id fora do tipo ou menor ou igual a zero.
    """
    identificador = tarefa["id_tarefa"]
    if isinstance(identificador, bool) or not isinstance(identificador, int):
        raise TaskValidationError(f"id_tarefa inválido: {identificador!r}")
    if identificador <= 0:
        raise TaskValidationError(f"id_tarefa={identificador} deve ser > 0")


def _validar_datetimes(tarefa: dict) -> None:
    """Garante que os quatro campos de data são datetime em UTC.

    Args:
        tarefa: Tarefa com as chaves de data presentes.

    Raises:
        TaskValidationError: Valor que não é datetime ou que não está em UTC.
    """
    for campo in _CAMPOS_DATA:
        valor = tarefa[campo]
        if not isinstance(valor, datetime):
            raise TaskValidationError(
                f"id_tarefa={tarefa['id_tarefa']} {campo} deve ser datetime"
            )
        if valor.tzinfo is not None and valor.utcoffset() != timezone.utc.utcoffset(valor):
            raise TaskValidationError(
                f"id_tarefa={tarefa['id_tarefa']} {campo} deve estar em UTC"
            )


def _validar_datas(tarefa: dict) -> None:
    """Rejeita conclusão anterior à criação e as outras inversões.

    Args:
        tarefa: Tarefa com datetimes já validados.

    Raises:
        TaskValidationError: A ordem temporal foi violada.
    """
    criacao = tarefa["data_criacao"]
    inicio = tarefa["data_inicio"]
    conclusao = tarefa["data_conclusao"]
    identificador = tarefa["id_tarefa"]
    if conclusao < criacao:
        raise TaskValidationError(
            f"id_tarefa={identificador} data_conclusao={conclusao.isoformat()} "
            f"data_criacao={criacao.isoformat()}"
        )
    if criacao > inicio:
        raise TaskValidationError(
            f"id_tarefa={identificador} data_criacao={criacao.isoformat()} "
            f"data_inicio={inicio.isoformat()}"
        )
    if inicio > conclusao:
        raise TaskValidationError(
            f"id_tarefa={identificador} data_inicio={inicio.isoformat()} "
            f"data_conclusao={conclusao.isoformat()}"
        )


def _filtrar(tarefas: list[dict], status: str) -> list[dict]:
    """Mantém as tarefas de um status.

    Args:
        tarefas: Lote já validado.
        status: Status desejado.

    Returns:
        Sublista na ordem original.
    """
    return [tarefa for tarefa in tarefas if tarefa["status"] == status]


def _horas(tarefa: dict) -> float:
    """Calcula a duração da tarefa em horas.

    Args:
        tarefa: Tarefa concluída com datas consistentes.

    Returns:
        Horas entre o início e a conclusão.
    """
    delta = tarefa["data_conclusao"] - tarefa["data_inicio"]
    return delta.total_seconds() / 3600


def _esta_atrasada(tarefa: dict) -> bool:
    """Indica se a conclusão passou do prazo.

    Args:
        tarefa: Tarefa concluída.

    Returns:
        True quando data_conclusao é estritamente maior que prazo.
    """
    return tarefa["data_conclusao"] > tarefa["prazo"]


def _media_horas(tarefas: list[dict]) -> float:
    """Média de duração em horas, ou 0.0 se o grupo estiver vazio.

    Args:
        tarefas: Tarefas concluídas do grupo.

    Returns:
        Média arredondada em duas casas.
    """
    if not tarefas:
        return 0.0
    return round(sum(_horas(tarefa) for tarefa in tarefas) / len(tarefas), 2)


def _taxa_atraso(tarefas: list[dict]) -> float:
    """Taxa de atraso percentual, ou 0.0 se o grupo estiver vazio.

    Args:
        tarefas: Tarefas concluídas do grupo.

    Returns:
        Percentual arredondado em duas casas.
    """
    if not tarefas:
        return 0.0
    atrasadas = sum(1 for tarefa in tarefas if _esta_atrasada(tarefa))
    return round(atrasadas / len(tarefas) * 100, 2)


def _montar_relatorio(tarefas: list[dict]) -> dict:
    """Agrega totais, métricas gerais e o recorte por prioridade.

    Args:
        tarefas: Lote validado, com qualquer status.

    Returns:
        RelatorioMetricas no formato da versão 2.0.
    """
    concluidas = _filtrar(tarefas, "concluída")
    por_prioridade = {
        prioridade: {
            "tempo_medio_conclusao_horas": _media_horas(
                [tarefa for tarefa in concluidas if tarefa["prioridade"] == prioridade]
            ),
            "taxa_atraso_percentual": _taxa_atraso(
                [tarefa for tarefa in concluidas if tarefa["prioridade"] == prioridade]
            ),
        }
        for prioridade in _PRIORIDADES
    }
    return {
        "total_tarefas": len(tarefas),
        "total_concluidas": len(concluidas),
        "total_pendentes": len(_filtrar(tarefas, "pendente")),
        "tempo_medio_conclusao_horas": _media_horas(concluidas),
        "taxa_atraso_percentual": _taxa_atraso(concluidas),
        "indicadores_por_prioridade": por_prioridade,
    }
