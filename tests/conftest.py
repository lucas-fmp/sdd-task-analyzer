"""Imprime, no fim do pytest, a entrada e a saída de cada cenário anotado."""

from __future__ import annotations


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:
    """Escreve o resumo de entradas e saídas depois dos testes."""
    del exitstatus, config
    from test_harness import CASOS

    if not CASOS:
        return
    terminalreporter.write_sep("=", "Entradas e saidas")
    for titulo, entrada, saida in CASOS:
        terminalreporter.write_line("")
        terminalreporter.write_line(titulo)
        terminalreporter.write_line("Entrada:")
        for linha in entrada.splitlines():
            terminalreporter.write_line(f"  {linha}")
        terminalreporter.write_line("Saida:")
        for linha in saida.splitlines():
            terminalreporter.write_line(f"  {linha}")
    terminalreporter.write_line("")
