"""
Avaliação da camada de recuperação — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Roda 100% sem chave de API: usa a busca semântica real da Sprint 2
(sprint2/vetorial/buscar.py → all-MiniLM-L6-v2 + ChromaDB) e compara contra a
verdade-base anotada em perguntas.json.

Por pergunta (exceto guardrail, bloqueadas antes da busca no contrato v1.0):

  1. Ranking completo (top_k=25, limiar 0) repetido N vezes → determinismo.
     As N saídas são serializadas e comparadas byte a byte; qualquer diferença
     é registrada como bug, sem arredondamento.
  2. As três configurações de produção, uma vez cada, pelo mesmo caminho que
     o personalizador usa (buscar_contexto com limiar padrão 0,50):
         leigo_ansioso top_k=3 · leigo_curioso top_k=4 · medico top_k=5
     O perfil NÃO altera a query (personalizador.py passa a pergunta crua);
     só o top_k muda. O script verifica que cada configuração é igual ao
     prefixo do ranking completo filtrado pelo limiar.
  3. Métricas contra a verdade-base: precisão e recall de contexto, posição
     e similaridade de cada chunk essencial no ranking completo.

Uso:
    python sprint4/avaliacao/avaliar_recuperacao.py            # N=5
    python sprint4/avaliacao/avaliar_recuperacao.py --n 3
"""

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from sprint2.vetorial.buscar import (  # noqa: E402
    MODELO_NOME,
    SIMILARIDADE_MINIMA,
    buscar_contexto,
    buscar_trechos,
)

PERFIS_TOP_K = {"leigo_ansioso": 3, "leigo_curioso": 4, "medico": 5}
TOTAL_CHUNKS = 25


def _hash(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _div(a, b):
    return round(a / b, 4) if b else None


def metricas_contexto(secoes_recuperadas: list, pergunta: dict) -> dict:
    """Precisão e recall de contexto conforme criterios_anotacao."""
    essenciais = set(pergunta["chunks_essenciais"])
    relevantes = essenciais | set(pergunta["chunks_aceitaveis"])
    recuperadas = list(secoes_recuperadas)

    acertos_relevantes = [s for s in recuperadas if s in relevantes]
    acertos_essenciais = [s for s in essenciais if s in recuperadas]

    return {
        "recuperadas": recuperadas,
        "n_recuperadas": len(recuperadas),
        "precisao": _div(len(acertos_relevantes), len(recuperadas)),
        "recall": _div(len(acertos_essenciais), len(essenciais)),
        "essenciais_faltando": sorted(essenciais - set(recuperadas)),
        "irrelevantes_recuperadas": [s for s in recuperadas if s not in relevantes],
        "encontrou_contexto": len(recuperadas) > 0,
    }


def avaliar_pergunta(pergunta: dict, n: int) -> dict:
    # 1) Ranking completo, N vezes.
    execucoes = []
    for _ in range(n):
        inicio = time.perf_counter()
        ranking = buscar_trechos(pergunta["pergunta"], top_k=TOTAL_CHUNKS,
                                 similaridade_minima=0.0)
        latencia = round(time.perf_counter() - inicio, 3)
        execucoes.append({
            "latencia_s": latencia,
            "hash": _hash(ranking),
            "ranking": [(t["secao"], t["similaridade"]) for t in ranking],
        })

    hashes = {e["hash"] for e in execucoes}
    ranking_ref = execucoes[0]["ranking"]

    posicoes = {s: i + 1 for i, (s, _) in enumerate(ranking_ref)}
    similaridades = dict(ranking_ref)

    # 2) Configurações de produção por perfil.
    perfis = {}
    for perfil, top_k in PERFIS_TOP_K.items():
        busca = buscar_contexto(pergunta["pergunta"], top_k=top_k)
        secoes = [t["secao"] for t in busca["trechos"]]
        esperado = [s for s, sim in ranking_ref[:top_k] if sim >= SIMILARIDADE_MINIMA]
        perfis[perfil] = {
            "top_k": top_k,
            "trechos": [(t["secao"], t["similaridade"]) for t in busca["trechos"]],
            "cortados_pelo_limiar": [s for s, sim in ranking_ref[:top_k]
                                     if sim < SIMILARIDADE_MINIMA],
            "igual_ao_prefixo_do_ranking": secoes == esperado,
            **metricas_contexto(secoes, pergunta),
        }

    return {
        "id": pergunta["id"],
        "categoria": pergunta["categoria"],
        "pergunta": pergunta["pergunta"],
        "comportamento_esperado": pergunta["comportamento_esperado"],
        "chunks_essenciais": pergunta["chunks_essenciais"],
        "chunks_aceitaveis": pergunta["chunks_aceitaveis"],
        "determinismo": {
            "n": n,
            "identico_byte_a_byte": len(hashes) == 1,
            "hashes_distintos": sorted(hashes),
            "latencias_s": [e["latencia_s"] for e in execucoes],
        },
        "ranking_completo": ranking_ref,
        "similaridade_max": ranking_ref[0][1] if ranking_ref else None,
        "essenciais_no_ranking": {
            s: {"posicao": posicoes.get(s), "similaridade": similaridades.get(s)}
            for s in pergunta["chunks_essenciais"]
        },
        "perfis": perfis,
        "execucoes_brutas": execucoes,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5)
    args = parser.parse_args(argv)

    conjunto = json.loads((DIR / "perguntas.json").read_text(encoding="utf-8"))
    alvo = [p for p in conjunto["perguntas"] if p["categoria"] != "guardrail"]

    inicio = datetime.now(timezone.utc).isoformat(timespec="seconds")
    resultados = []
    for p in alvo:
        r = avaliar_pergunta(p, args.n)
        resultados.append(r)
        prod = r["perfis"]["leigo_ansioso"]
        print(f"{r['id']:3} det={r['determinismo']['identico_byte_a_byte']} "
              f"max={r['similaridade_max']} k3={[s for s, _ in prod['trechos']]} "
              f"P={prod['precisao']} R={prod['recall']}", flush=True)

    saida = {
        "gerado_em_utc": inicio,
        "configuracao": {
            "modelo_embeddings": MODELO_NOME,
            "similaridade_minima": SIMILARIDADE_MINIMA,
            "perfis_top_k": PERFIS_TOP_K,
            "n_repeticoes_determinismo": args.n,
            "perguntas_fonte": "sprint4/avaliacao/perguntas.json",
            "excluidas": "categoria guardrail (bloqueio antes da busca no contrato v1.0)",
        },
        "resultados": resultados,
    }
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = DIR / "execucoes" / f"recuperacao_{carimbo}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[recuperacao] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
