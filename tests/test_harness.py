"""Test Harness do TaskAnalyzer.

Traduz os cenários de aceite da spec. Os nomes dos testes são os previstos
no contrato e não podem ser apagados nem enfraquecidos.
"""

from __future__ import annotations

import inspect
from datetime import datetime

import pytest

from src.task_analyzer import (
    DataInconsistenteError,
    EntradaInvalidaError,
    NenhumaTarefaConcluidaError,
    analisar_tarefas,
)


def _dt(texto: str) -> datetime:
    """Converte o texto do exemplo da spec em datetime ingênuo (UTC)."""
    return datetime.fromisoformat(texto)


def _tarefa(**alteracoes: object) -> dict:
    """Monta uma tarefa válida e aplica os campos informados."""
    tarefa = {
        "id_tarefa": 1,
        "data_criacao": _dt("2026-01-01 08:00"),
        "data_inicio": _dt("2026-01-01 09:00"),
        "data_conclusao": _dt("2026-01-01 10:00"),
        "prazo": _dt("2026-01-01 11:00"),
        "prioridade": "alta",
        "status": "concluída",
    }
    tarefa.update(alteracoes)
    return tarefa


def _exemplo_cenario_1() -> list[dict]:
    """Reproduz a tabela numérica do Cenário 1 da spec."""
    return [
        _tarefa(
            id_tarefa=1,
            data_conclusao=_dt("2026-01-01 10:00"),
            prazo=_dt("2026-01-01 11:00"),
            prioridade="alta",
            status="concluída",
        ),
        _tarefa(
            id_tarefa=2,
            data_conclusao=_dt("2026-01-01 12:00"),
            prazo=_dt("2026-01-01 11:00"),
            prioridade="alta",
            status="concluída",
        ),
        _tarefa(
            id_tarefa=3,
            data_conclusao=_dt("2026-01-01 10:30"),
            prazo=_dt("2026-01-01 12:00"),
            prioridade="média",
            status="concluída",
        ),
        _tarefa(
            id_tarefa=4,
            data_conclusao=_dt("2026-01-01 09:30"),
            prazo=_dt("2026-01-01 10:00"),
            prioridade="baixa",
            status="pendente",
        ),
        _tarefa(
            id_tarefa=5,
            data_conclusao=_dt("2026-01-01 11:00"),
            prazo=_dt("2026-01-01 10:00"),
            prioridade="baixa",
            status="cancelada",
        ),
    ]


def test_assinatura_publica_existe_e_nao_foi_alterada() -> None:
    """A função pública congelada no contrato deve existir com 1 parâmetro."""
    assert callable(analisar_tarefas)
    parametros = list(inspect.signature(analisar_tarefas).parameters)
    assert parametros == ["tarefas"]


def test_cenario_sucesso_metricas_corretas() -> None:
    """Cenário 1 — métricas gerais e por prioridade do exemplo numérico."""
    relatorio = analisar_tarefas(_exemplo_cenario_1())

    assert relatorio["quantidade_tarefas"] == 3
    assert relatorio["tempo_medio_conclusao_min"] == 110.0
    assert relatorio["taxa_atraso_percentual"] == 33.33

    indicadores = relatorio["indicadores_por_prioridade"]
    assert list(indicadores) == ["baixa", "média", "alta"]
    assert indicadores["alta"] == {
        "quantidade_tarefas": 2,
        "tempo_medio_conclusao_min": 120.0,
        "taxa_atraso_percentual": 50.0,
    }
    assert indicadores["média"] == {
        "quantidade_tarefas": 1,
        "tempo_medio_conclusao_min": 90.0,
        "taxa_atraso_percentual": 0.0,
    }
    assert indicadores["baixa"]["quantidade_tarefas"] == 0


def test_ignora_pendente_e_cancelada() -> None:
    """Pendentes e canceladas não entram em quantidade, tempo nem atraso."""
    relatorio = analisar_tarefas(_exemplo_cenario_1())
    assert relatorio["quantidade_tarefas"] == 3
    soma = sum(
        bloco["quantidade_tarefas"]
        for bloco in relatorio["indicadores_por_prioridade"].values()
    )
    assert soma == 3


def test_prioridade_sem_concluidas_retorna_zero() -> None:
    """Prioridade sem concluídas devolve 0 / 0.00 / 0.00."""
    relatorio = analisar_tarefas(_exemplo_cenario_1())
    assert relatorio["indicadores_por_prioridade"]["baixa"] == {
        "quantidade_tarefas": 0,
        "tempo_medio_conclusao_min": 0.0,
        "taxa_atraso_percentual": 0.0,
    }


def test_data_conclusao_antes_do_inicio_lanca_data_inconsistente() -> None:
    """Cenário 2 — data_conclusao < data_inicio."""
    tarefas = [_tarefa(id_tarefa=7, data_conclusao=_dt("2026-01-01 08:30"))]
    with pytest.raises(DataInconsistenteError, match=r"id_tarefa=7"):
        analisar_tarefas(tarefas)


def test_data_inicio_antes_da_criacao_lanca_data_inconsistente() -> None:
    """Cenário 2 — data_inicio < data_criacao."""
    tarefas = [_tarefa(id_tarefa=8, data_inicio=_dt("2026-01-01 07:00"))]
    with pytest.raises(DataInconsistenteError, match=r"id_tarefa=8"):
        analisar_tarefas(tarefas)


def test_lista_sem_concluidas_lanca_nenhuma_tarefa_concluida() -> None:
    """Cenário 3 — só pendente/cancelada."""
    tarefas = [
        _tarefa(id_tarefa=1, status="pendente"),
        _tarefa(id_tarefa=2, status="cancelada"),
    ]
    with pytest.raises(NenhumaTarefaConcluidaError, match="quantidade_concluida=0"):
        analisar_tarefas(tarefas)


def test_lista_vazia_lanca_nenhuma_tarefa_concluida() -> None:
    """Cenário 3 — lista vazia."""
    with pytest.raises(NenhumaTarefaConcluidaError, match="quantidade_recebida=0"):
        analisar_tarefas([])


def test_prioridade_invalida_lanca_entrada_invalida() -> None:
    """Cenário 4 — prioridade fora do enumerador."""
    tarefas = [_tarefa(id_tarefa=3, prioridade="urgente")]
    with pytest.raises(EntradaInvalidaError, match="id_tarefa=3"):
        analisar_tarefas(tarefas)


def test_id_duplicado_lanca_entrada_invalida() -> None:
    """Cenário 4 — id_tarefa repetido no lote."""
    tarefas = [_tarefa(id_tarefa=4), _tarefa(id_tarefa=4, prioridade="média")]
    with pytest.raises(EntradaInvalidaError, match="id_tarefa=4"):
        analisar_tarefas(tarefas)
