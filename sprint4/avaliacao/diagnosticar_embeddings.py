"""
Diagnóstico do modelo de embeddings — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Hipótese a testar: as similaridades da recuperação ficam comprimidas numa
faixa estreita porque all-MiniLM-L6-v2 (card no Hugging Face: "language: en")
é aplicado a perguntas e documentos em português.

Só usa dados que já existem localmente — nenhum modelo novo é baixado:
  A. Distribuição das 400 similaridades pergunta × chunk gravadas em
     execucoes/recuperacao_*.json (16 perguntas × 25 chunks).
  B. Similaridade chunk × chunk a partir dos vetores JÁ GRAVADOS no ChromaDB
     (300 pares): o "piso" entre textos sem relação temática.
  C. Fragmentação do português pelo tokenizador do próprio modelo (vocabulário
     WordPiece em inglês): tokens por palavra e palavras quebradas em ≥3 peças.
  D. Sobreposição lexical × similaridade: se o modelo entendesse o conteúdo,
     pergunta que repete as palavras do chunk certo deveria pontuar alto.

Limite declarado: sem um segundo modelo sobre os mesmos dados não há
referência para chamar a faixa de "anormal" — este script mostra se os dados
são CONSISTENTES com a hipótese, não a prova. A prova é o experimento
comparativo descrito no relatório.

Uso:
    python sprint4/avaliacao/diagnosticar_embeddings.py execucoes/recuperacao_<ts>.json
"""

import json
import re
import statistics
import sys
import unicodedata
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]

STOP = {"a", "o", "as", "os", "de", "do", "da", "dos", "das", "e", "é", "em", "no", "na",
        "nos", "nas", "um", "uma", "para", "por", "com", "que", "qual", "quais", "meu",
        "minha", "seu", "sua", "se", "ao", "à", "eu", "me", "segundo", "sobre", "isso"}


def _q(valores, p):
    v = sorted(valores)
    k = (len(v) - 1) * p
    i = int(k)
    return round(v[i] + (v[min(i + 1, len(v) - 1)] - v[i]) * (k - i), 4)


def resumo(valores) -> dict:
    return {"n": len(valores), "min": round(min(valores), 4), "p05": _q(valores, 0.05),
            "mediana": _q(valores, 0.5), "p95": _q(valores, 0.95), "max": round(max(valores), 4),
            "media": round(statistics.mean(valores), 4), "desvio": round(statistics.pstdev(valores), 4)}


def palavras(texto: str) -> set:
    base = unicodedata.normalize("NFD", texto.lower())
    base = "".join(c for c in base if unicodedata.category(c) != "Mn")
    return {w for w in re.findall(r"[a-z0-9]+", base) if w not in STOP and len(w) > 2}


def condicao(secao: str):
    m = re.search(r"_(2\.\d)$", secao)
    return m.group(1) if m else None


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    caminho = Path(argv[0])
    if not caminho.is_absolute():
        caminho = DIR / caminho
    bruto = json.loads(caminho.read_text(encoding="utf-8"))
    perguntas = {p["id"]: p for p in
                 json.loads((DIR / "perguntas.json").read_text(encoding="utf-8"))["perguntas"]}

    # ── A. pergunta × chunk ──────────────────────────────────────────────────
    todas = [sim for r in bruto["resultados"] for _, sim in r["ranking_completo"]]
    por_pergunta = []
    for r in bruto["resultados"]:
        sims = [s for _, s in r["ranking_completo"]]
        por_pergunta.append({
            "id": r["id"], "max": max(sims), "min": min(sims),
            "amplitude": round(max(sims) - min(sims), 4),
            "margem_top1_top2": round(sims[0] - sims[1], 4),
            "margem_top1_mediana": round(sims[0] - statistics.median(sims), 4),
        })

    # ── B. chunk × chunk (vetores gravados) ──────────────────────────────────
    import chromadb
    import numpy as np

    col = chromadb.PersistentClient(
        path=str(RAIZ / "sprint2" / "vetorial" / "base_vetorial")
    ).get_collection("genera_relatorio")
    dados = col.get(include=["embeddings", "metadatas", "documents"])
    secoes = [m["secao"] for m in dados["metadatas"]]
    vet = np.array(dados["embeddings"], dtype=float)
    vet = vet / np.linalg.norm(vet, axis=1, keepdims=True)
    dimensao = int(vet.shape[1])

    mesma, diferente = [], []
    for i, j in combinations(range(len(secoes)), 2):
        s = float(vet[i] @ vet[j])
        ci, cj = condicao(secoes[i]), condicao(secoes[j])
        if ci and cj:
            (mesma if ci == cj else diferente).append(s)

    # ── C. fragmentação do tokenizador ───────────────────────────────────────
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2",
                                        local_files_only=True)
    total_palavras, total_tokens, quebradas = 0, 0, 0
    exemplos = {}
    for doc in dados["documents"]:
        for w in re.findall(r"[A-Za-zÀ-ÿ]{4,}", doc):
            pecas = tok.tokenize(w)
            total_palavras += 1
            total_tokens += len(pecas)
            if len(pecas) >= 3:
                quebradas += 1
                exemplos.setdefault(w.lower(), pecas)
    alvo = ["predisposição", "hipertensão", "ancestralidade", "recomendação", "composição",
            "condição", "genético", "risco", "doença", "percentil"]
    fragmentacao_alvo = {w: tok.tokenize(w) for w in alvo}

    # ── D. sobreposição lexical × similaridade ───────────────────────────────
    conteudo = dict(zip(secoes, dados["documents"]))
    lexical = []
    for r in bruto["resultados"]:
        p = perguntas[r["id"]]
        alvo_secoes = p["chunks_essenciais"] or [r["ranking_completo"][0][0]]
        for s in alvo_secoes:
            pq, pc = palavras(p["pergunta"]), palavras(conteudo[s])
            lexical.append({
                "id": r["id"], "chunk": s,
                "tipo": "essencial" if p["chunks_essenciais"] else "top1_de_pergunta_sem_resposta",
                "palavras_da_pergunta_no_chunk": round(len(pq & pc) / len(pq), 2) if pq else None,
                "palavras_em_comum": sorted(pq & pc),
                "similaridade": dict(r["ranking_completo"]).get(s),
            })

    saida = {
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fonte_bruta": str(caminho.relative_to(RAIZ)).replace("\\", "/"),
        "modelo": "sentence-transformers/all-MiniLM-L6-v2",
        "dimensao_vetores_gravados": dimensao,
        "A_pergunta_x_chunk": {"todas": resumo(todas), "por_pergunta": por_pergunta,
                               "amplitude_media": round(statistics.mean(p["amplitude"] for p in por_pergunta), 4),
                               "margem_top1_top2_media": round(statistics.mean(p["margem_top1_top2"] for p in por_pergunta), 4)},
        "B_chunk_x_chunk": {"mesma_condicao": resumo(mesma), "condicoes_diferentes": resumo(diferente)},
        "C_tokenizador": {
            "palavras_analisadas": total_palavras,
            "tokens_por_palavra": round(total_tokens / total_palavras, 3),
            "palavras_em_3_ou_mais_pecas": quebradas,
            "fracao_em_3_ou_mais_pecas": round(quebradas / total_palavras, 4),
            "remove_acentos": tok.tokenize("ç ã é") == tok.tokenize("c a e"),
            "exemplos_alvo": fragmentacao_alvo,
        },
        "D_lexical_x_similaridade": lexical,
        "limite": ("Sem segundo modelo sobre os mesmos dados não há referência de 'normal'; "
                   "os números mostram consistência com a hipótese, não a prova."),
    }
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = DIR / "execucoes" / f"diagnostico_embeddings_{carimbo}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")

    print("dimensão:", dimensao)
    print("A todas:", saida["A_pergunta_x_chunk"]["todas"])
    print("A amplitude média por pergunta:", saida["A_pergunta_x_chunk"]["amplitude_media"],
          "| margem top1-top2 média:", saida["A_pergunta_x_chunk"]["margem_top1_top2_media"])
    print("B mesma condição:", saida["B_chunk_x_chunk"]["mesma_condicao"])
    print("B condições diferentes:", saida["B_chunk_x_chunk"]["condicoes_diferentes"])
    c = saida["C_tokenizador"]
    print("C tokens/palavra:", c["tokens_por_palavra"], "| ≥3 peças:", c["fracao_em_3_ou_mais_pecas"],
          "| remove acentos:", c["remove_acentos"])
    for w, pecas in c["exemplos_alvo"].items():
        print("   ", w, pecas)
    for l in lexical:
        print("D", l["id"], l["chunk"], l["tipo"], "lex=", l["palavras_da_pergunta_no_chunk"],
              "sim=", l["similaridade"], l["palavras_em_comum"])
    print(f"[diagnostico] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
