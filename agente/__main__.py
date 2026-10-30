"""Linha de comando: python -m agente "Qual foi o % de aéreas em setembro?" """

import sys

from .agent import ask


def main() -> None:
    if len(sys.argv) < 2:
        print('Uso: python -m agente "sua pergunta"')
        sys.exit(1)
    answer = ask(" ".join(sys.argv[1:]))
    print(answer.text)
    for q in answer.queries:
        print(f"\n-- SQL ({'ok' if q.ok else 'erro'}):\n{q.sql}")
    if answer.error:
        sys.exit(2)


if __name__ == "__main__":
    main()
