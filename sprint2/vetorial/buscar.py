"""
Busca Semântica — Sprint 2 / Genera / Dasa

Responsável por:
1. Receber uma pergunta do usuário
2. Gerar embedding da pergunta
3. Consultar a base vetorial ChromaDB
4. Retornar os trechos mais relevantes do relatório
5. Exibir fonte, seção e similaridade

Uso no terminal:
    python sprint2/vetorial/buscar.py
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from sentence_transformers import SentenceTransformer


# ── Configurações ─────────────────────────────────────────────────────────────

RAIZ = Path(__file__).resolve().parents[2]

BASE_VETORIAL = RAIZ / "sprint2" / "vetorial" / "base_vetorial"

COLECAO_NOME = "genera_relatorio"

MODELO_NOME = "all-MiniLM-L6-v2"

TOP_K_PADRAO = 3

SIMILARIDADE_MINIMA = 0.50


# ── Carregamento ──────────────────────────────────────────────────────────────

def carregar_modelo() -> SentenceTransformer:
    """
    Carrega o mesmo modelo usado na geração dos embeddings dos chunks.
    """
    return SentenceTransformer(MODELO_NOME)


def carregar_colecao():
    """
    Conecta à base vetorial persistida no ChromaDB.
    """
    if not BASE_VETORIAL.exists():
        raise FileNotFoundError(
            f"Base vetorial não encontrada em: {BASE_VETORIAL}\n"
            "Execute primeiro:\n"
            "  python sprint2/embeddings/gerar_embeddings.py\n"
            "  python sprint2/vetorial/indexar.py"
        )

    cliente = chromadb.PersistentClient(path=str(BASE_VETORIAL))
    return cliente.get_collection(COLECAO_NOME)


# ── Busca Semântica ───────────────────────────────────────────────────────────

def buscar_trechos(
    pergunta: str,
    top_k: int = TOP_K_PADRAO,
    similaridade_minima: float = SIMILARIDADE_MINIMA
) -> List[Dict[str, Any]]:
    """
    Recebe uma pergunta em linguagem natural e retorna os trechos mais relevantes
    do relatório genético.

    Retorno:
        [
            {
                "conteudo": "...",
                "secao": "...",
                "fonte": "...",
                "similaridade": 0.82
            }
        ]
    """

    if not pergunta or not pergunta.strip():
        raise ValueError("A pergunta não pode estar vazia.")

    modelo = carregar_modelo()
    colecao = carregar_colecao()

    embedding_pergunta = modelo.encode(pergunta).tolist()

    resultados = colecao.query(
        query_embeddings=[embedding_pergunta],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    trechos = []

    documentos = resultados.get("documents", [[]])[0]
    metadados = resultados.get("metadatas", [[]])[0]
    distancias = resultados.get("distances", [[]])[0]

    for documento, metadata, distancia in zip(documentos, metadados, distancias):
        similaridade = round(1 - distancia, 4)

        if similaridade < similaridade_minima:
            continue

        trechos.append({
            "conteudo": documento,
            "secao": metadata.get("secao", ""),
            "fonte": metadata.get("fonte", ""),
            "similaridade": similaridade
        })

    return trechos


def montar_contexto(trechos: List[Dict[str, Any]]) -> str:
    """
    Monta o contexto que será enviado ao agente/LLM.
    """

    if not trechos:
        return ""

    contexto = "TRECHOS RECUPERADOS DO RELATÓRIO GENÉTICO:\n\n"

    for i, trecho in enumerate(trechos, start=1):
        contexto += f"[Fonte {i}]\n"
        contexto += f"Seção: {trecho['secao']}\n"
        contexto += f"Origem: {trecho['fonte']}\n"
        contexto += f"Similaridade: {trecho['similaridade']}\n"
        contexto += f"Conteúdo: {trecho['conteudo']}\n\n"

    return contexto.strip()


def buscar_contexto(
    pergunta: str,
    top_k: int = TOP_K_PADRAO,
    similaridade_minima: float = SIMILARIDADE_MINIMA
) -> Dict[str, Any]:
    """
    Função principal para integração com o agente.

    Retorna:
        {
            "pergunta": "...",
            "encontrou_contexto": True,
            "trechos": [...],
            "contexto": "..."
        }
    """

    trechos = buscar_trechos(
        pergunta=pergunta,
        top_k=top_k,
        similaridade_minima=similaridade_minima
    )

    contexto = montar_contexto(trechos)

    return {
        "pergunta": pergunta,
        "encontrou_contexto": len(trechos) > 0,
        "trechos": trechos,
        "contexto": contexto
    }


# ── Execução via terminal ─────────────────────────────────────────────────────

def imprimir_resultados(pergunta: str, trechos: List[Dict[str, Any]]) -> None:
    """
    Exibe os resultados da busca no terminal.
    """

    print("\n" + "=" * 70)
    print("BUSCA SEMÂNTICA — RESULTADO")
    print("=" * 70)
    print(f"Pergunta: {pergunta}")

    if not trechos:
        print("\nNenhum trecho com similaridade suficiente foi encontrado.")
        print("O agente deve responder que não encontrou informação no relatório.")
        return

    for i, trecho in enumerate(trechos, start=1):
        print("\n" + "-" * 70)
        print(f"Fonte {i}")
        print("-" * 70)
        print(f"Similaridade: {trecho['similaridade']}")
        print(f"Seção: {trecho['secao']}")
        print(f"Fonte: {trecho['fonte']}")
        print(f"Trecho: {trecho['conteudo']}")


def main() -> None:
    print("=" * 70)
    print("BUSCA SEMÂNTICA — Sprint 2 / Genera / Dasa")
    print("=" * 70)

    try:
        pergunta = input("\nDigite sua pergunta sobre o relatório genético: ").strip()

        resultado = buscar_contexto(pergunta)

        imprimir_resultados(
            pergunta=resultado["pergunta"],
            trechos=resultado["trechos"]
        )

    except Exception as erro:
        print("\n[ERRO] Falha ao executar busca semântica.")
        print(str(erro))
        sys.exit(1)


if __name__ == "__main__":
    main()
