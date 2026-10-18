"""Test Harness do TaskAnalyzer.

Cobre o cenário de sucesso, a data inconsistente e os casos de borda
definidos no enunciado da Fase 2.
"""

from __future__ import annotations

import inspect
from datetime import datetime

import pytest

from src.task_analyzer import TaskValidationError, analyze_tasks

CASOS: list[tuple[str, str, str]] = []


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


def anotar(titulo: str, entrada: str, saida: str) -> None:
    """Guarda um cenário para o resumo impresso no fim do pytest."""
    CASOS.append((titulo, entrada, saida))


def _hora(valor: datetime) -> str:
    """Formata um datetime do exemplo como hora."""
    return valor.strftime("%H:%M")


def _descrever_entrada(tarefas: list[dict]) -> str:
    """Resume a lista enviada para o relatório do terminal."""
    if not tarefas:
        return "(lista vazia)"
    linhas = []
    for tarefa in tarefas:
        linhas.append(
            "id={id_tarefa} {prioridade} {status} | "
            "criacao={criacao} inicio={inicio} conclusao={conclusao} prazo={prazo}".format(
                criacao=_hora(tarefa["data_criacao"]),
                inicio=_hora(tarefa["data_inicio"]),
                conclusao=_hora(tarefa["data_conclusao"]),
                prazo=_hora(tarefa["prazo"]),
                **{chave: tarefa[chave] for chave in ("id_tarefa", "prioridade", "status")},
            )
        )
    return "\n".join(linhas)


def _descrever_saida(relatorio: dict) -> str:
    """Resume o relatório devolvido por analyze_tasks."""
    linhas = [
        f"total_tarefas={relatorio['total_tarefas']}",
        f"total_concluidas={relatorio['total_concluidas']}",
        f"total_pendentes={relatorio['total_pendentes']}",
        f"tempo_medio_conclusao_horas={relatorio['tempo_medio_conclusao_horas']:.2f}",
        f"taxa_atraso_percentual={relatorio['taxa_atraso_percentual']:.2f}",
    ]
    for prioridade, bloco in relatorio["indicadores_por_prioridade"].items():
        linhas.append(
            f"{prioridade}: {bloco['tempo_medio_conclusao_horas']:.2f} h, "
            f"atraso {bloco['taxa_atraso_percentual']:.2f}%"
        )
    return "\n".join(linhas)


def _descrever_erro(erro: BaseException) -> str:
    """Resume a exceção esperada."""
    return f"{type(erro).__name__}: {erro}"


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
    anotar(
        "1. Sucesso — exemplo numerico",
        _descrever_entrada(_exemplo_cenario_1()),
        _descrever_saida(relatorio),
    )


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
    with pytest.raises(TaskValidationError, match=r"id_tarefa=7") as erro:
        analyze_tasks(tarefas)
    anotar(
        "2. Data inconsistente — conclusao antes da criacao",
        _descrever_entrada(tarefas),
        _descrever_erro(erro.value),
    )


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
    anotar(
        "3. Sem concluidas — so pendente e cancelada",
        _descrever_entrada(tarefas),
        _descrever_saida(relatorio),
    )


def test_lista_vazia_retorna_zero() -> None:
    """Caso de borda — lista vazia devolve 0.0, sem exceção."""
    relatorio = analyze_tasks([])
    assert relatorio["total_tarefas"] == 0
    assert relatorio["total_concluidas"] == 0
    assert relatorio["total_pendentes"] == 0
    assert relatorio["tempo_medio_conclusao_horas"] == 0.0
    assert relatorio["taxa_atraso_percentual"] == 0.0
    assert relatorio["indicadores_por_prioridade"] == _zeros_prioridade()
    anotar("4. Lista vazia", _descrever_entrada([]), _descrever_saida(relatorio))


def test_prioridade_invalida_lanca_task_validation_error() -> None:
    """Prioridade fora do enumerador."""
    tarefas = [_tarefa(id_tarefa=3, prioridade="urgente")]
    with pytest.raises(TaskValidationError, match="id_tarefa=3") as erro:
        analyze_tasks(tarefas)
    anotar(
        "5. Prioridade invalida",
        _descrever_entrada(tarefas),
        _descrever_erro(erro.value),
    )


def test_id_duplicado_lanca_task_validation_error() -> None:
    """id_tarefa repetido no lote."""
    tarefas = [_tarefa(id_tarefa=4), _tarefa(id_tarefa=4, prioridade="média")]
    with pytest.raises(TaskValidationError, match="id_tarefa=4") as erro:
        analyze_tasks(tarefas)
    anotar(
        "6. id duplicado",
        _descrever_entrada(tarefas),
        _descrever_erro(erro.value),
    )
