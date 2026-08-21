"""
Teste de Busca Semântica — Sprint 2 / Genera / Dasa

Este arquivo testa a camada oficial de busca semântica localizada em:
    sprint2/vetorial/buscar.py

Uso:
    python sprint2/testes/testar_busca.py
"""

import sys
from pathlib import Path

# Permite importar módulos a partir da raiz do projeto
RAIZ = Path(__file__).resolve().parents[2]
sys.path.append(str(RAIZ))

from sprint2.vetorial.buscar import buscar_trechos


PERGUNTAS_TESTE = [
    "Eu tenho risco de diabetes?",
    "Quais são minhas condições de risco alto?",
    "O que devo fazer para prevenir doenças?",
    "Qual é minha ancestralidade?",
    "Existe algum problema genético relacionado ao câncer?",
    "Qual remédio devo tomar?"
]


def imprimir_resultado(pergunta: str, trechos: list[dict]) -> None:
    print(f"\n{'─' * 60}")
    print(f"PERGUNTA: {pergunta}")
    print(f"{'─' * 60}")

    if not trechos:
        print("Nenhum trecho relevante encontrado.")
        print("O agente deve responder que não encontrou informação suficiente no relatório.")
        return

    for i, trecho in enumerate(trechos, 1):
        print(f"\n  [{i}] Similaridade: {trecho['similaridade']:.4f}")
        print(f"      Seção:  {trecho['secao']}")
        print(f"      Fonte:  {trecho['fonte']}")

        conteudo = trecho["conteudo"]
        trecho_curto = conteudo[:220] + "..." if len(conteudo) > 220 else conteudo

        print(f"      Trecho: {trecho_curto}")


def main() -> None:
    print("=" * 60)
    print("TESTE DE BUSCA SEMÂNTICA — Sprint 2 / Genera")
    print("=" * 60)

    for pergunta in PERGUNTAS_TESTE:
        trechos = buscar_trechos(
            pergunta=pergunta,
            top_k=3
        )
        imprimir_resultado(pergunta, trechos)

    print(f"\n{'=' * 60}")
    print("BUSCA CONCLUÍDA.")
    print("=" * 60)


if __name__ == "__main__":
    main()
