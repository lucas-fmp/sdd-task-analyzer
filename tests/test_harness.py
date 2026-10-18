"""Test Harness do TaskAnalyzer.

Cobre o cenário de sucesso, a data inconsistente e os casos de borda
definidos no enunciado da Fase 2.
"""

from __future__ import annotations

import inspect
from datetime import datetime

import pytest

from src.task_analyzer import TaskValidationError, analyze_tasks


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
        _tarefa(id_tarefa=1, prioridade="alta", status="concluída"),
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


def _zeros_prioridade() -> dict[str, dict[str, float]]:
    """Indicadores vazios, uma chave por prioridade."""
    return {
        nome: {"tempo_medio_conclusao_horas": 0.0, "taxa_atraso_percentual": 0.0}
        for nome in ("baixa", "média", "alta")
    }


def test_assinatura_publica_existe_e_nao_foi_alterada() -> None:
    """A função pública definida na Fase 2 deve existir com 1 parâmetro."""
    assert callable(analyze_tasks)
    parametros = list(inspect.signature(analyze_tasks).parameters)
    assert parametros == ["tarefas"]


def test_cenario_sucesso_metricas_corretas() -> None:
    """Cenário 1 — totais, média em horas e taxa do exemplo numérico."""
    relatorio = analyze_tasks(_exemplo_cenario_1())

    assert relatorio["total_tarefas"] == 5
    assert relatorio["total_concluidas"] == 3
    assert relatorio["total_pendentes"] == 1
    assert relatorio["tempo_medio_conclusao_horas"] == 1.83
    assert relatorio["taxa_atraso_percentual"] == 33.33

    indicadores = relatorio["indicadores_por_prioridade"]
    assert list(indicadores) == ["baixa", "média", "alta"]
    assert indicadores["alta"] == {
        "tempo_medio_conclusao_horas": 2.0,
        "taxa_atraso_percentual": 50.0,
    }
    assert indicadores["média"] == {
        "tempo_medio_conclusao_horas": 1.5,
        "taxa_atraso_percentual": 0.0,
    }


def test_ignora_pendente_e_cancelada() -> None:
    """Pendentes e canceladas não entram na média nem na taxa."""
    relatorio = analyze_tasks(_exemplo_cenario_1())
    assert relatorio["total_concluidas"] == 3
    assert relatorio["tempo_medio_conclusao_horas"] == 1.83


def test_prioridade_sem_concluidas_retorna_zero() -> None:
    """Prioridade sem concluídas devolve 0.0 no tempo e na taxa."""
    relatorio = analyze_tasks(_exemplo_cenario_1())
    assert relatorio["indicadores_por_prioridade"]["baixa"] == {
        "tempo_medio_conclusao_horas": 0.0,
        "taxa_atraso_percentual": 0.0,
    }


def test_data_conclusao_antes_da_criacao_lanca_task_validation_error() -> None:
    """Cenário 2 — data_conclusao < data_criacao."""
    tarefas = [
        _tarefa(
            id_tarefa=7,
            data_criacao=_dt("2026-01-01 12:00"),
            data_inicio=_dt("2026-01-01 12:30"),
            data_conclusao=_dt("2026-01-01 11:00"),
        )
    ]
    with pytest.raises(TaskValidationError, match=r"id_tarefa=7"):
        analyze_tasks(tarefas)


def test_lista_sem_concluidas_retorna_zero() -> None:
    """Caso de borda — só pendente/cancelada devolve 0.0, sem exceção."""
    tarefas = [
        _tarefa(id_tarefa=1, status="pendente"),
        _tarefa(id_tarefa=2, status="cancelada"),
    ]
    relatorio = analyze_tasks(tarefas)
    assert relatorio["total_tarefas"] == 2
    assert relatorio["total_concluidas"] == 0
    assert relatorio["total_pendentes"] == 1
    assert relatorio["tempo_medio_conclusao_horas"] == 0.0
    assert relatorio["taxa_atraso_percentual"] == 0.0


def test_lista_vazia_retorna_zero() -> None:
    """Caso de borda — lista vazia devolve 0.0, sem exceção."""
    relatorio = analyze_tasks([])
    assert relatorio["total_tarefas"] == 0
    assert relatorio["total_concluidas"] == 0
    assert relatorio["total_pendentes"] == 0
    assert relatorio["tempo_medio_conclusao_horas"] == 0.0
    assert relatorio["taxa_atraso_percentual"] == 0.0
    assert relatorio["indicadores_por_prioridade"] == _zeros_prioridade()


def test_prioridade_invalida_lanca_task_validation_error() -> None:
    """Prioridade fora do enumerador."""
    tarefas = [_tarefa(id_tarefa=3, prioridade="urgente")]
    with pytest.raises(TaskValidationError, match="id_tarefa=3"):
        analyze_tasks(tarefas)


def test_id_duplicado_lanca_task_validation_error() -> None:
    """id_tarefa repetido no lote."""
    tarefas = [_tarefa(id_tarefa=4), _tarefa(id_tarefa=4, prioridade="média")]
    with pytest.raises(TaskValidationError, match="id_tarefa=4"):
        analyze_tasks(tarefas)
