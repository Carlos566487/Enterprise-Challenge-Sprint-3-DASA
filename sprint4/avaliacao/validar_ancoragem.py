"""
Validação do detector de ancoragem — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

A ancoragem (sprint3/rag_personalizacao/ancoragem.py) é a métrica principal da
avaliação. Antes de confiar nos números que ela produz, este script mede o
próprio detector contra casos com rótulo conhecido (casos_ancoragem.json):

    classe positiva = resposta INFIEL (alucinação)
    VP  detector marca ancorado=False numa resposta infiel
    FP  detector marca ancorado=False numa resposta fiel
    FN  detector marca ancorado=True  numa resposta infiel
    VN  detector marca ancorado=True  numa resposta fiel

O texto de cada contexto é lido da base vetorial real (sem modelo de
embeddings — só leitura de documentos) e gravado junto do resultado, para que
cada linha seja auditável mesmo se a base for regenerada.

Uso:
    python sprint4/avaliacao/validar_ancoragem.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from sprint3.rag_personalizacao import validar_ancoragem  # noqa: E402

BASE_VETORIAL = RAIZ / "sprint2" / "vetorial" / "base_vetorial"
COLECAO = "genera_relatorio"


def carregar_chunks_por_secao() -> dict:
    import chromadb

    colecao = chromadb.PersistentClient(path=str(BASE_VETORIAL)).get_collection(COLECAO)
    dados = colecao.get(include=["documents", "metadatas"])
    return {m["secao"]: doc for m, doc in zip(dados["metadatas"], dados["documents"])}


def classificar(fiel: bool, ancorado: bool) -> str:
    if not fiel:
        return "VP" if not ancorado else "FN"
    return "FP" if not ancorado else "VN"


def _div(a, b):
    return round(a / b, 4) if b else None


def metricas(linhas: list) -> dict:
    cont = {k: sum(1 for l in linhas if l["classe"] == k) for k in ("VP", "FP", "FN", "VN")}
    return {
        **cont,
        "total": len(linhas),
        "precisao": _div(cont["VP"], cont["VP"] + cont["FP"]),
        "recall": _div(cont["VP"], cont["VP"] + cont["FN"]),
        "acuracia": _div(cont["VP"] + cont["VN"], len(linhas)),
    }


def main() -> int:
    casos = json.loads((DIR / "casos_ancoragem.json").read_text(encoding="utf-8"))
    chunks = carregar_chunks_por_secao()

    linhas = []
    for caso in casos["casos"]:
        trechos = [chunks[s] for s in caso["contexto"]]
        saida = validar_ancoragem(caso["resposta"], trechos)
        linhas.append({
            "id": caso["id"],
            "grupo": caso["grupo"],
            "fiel": caso["fiel"],
            "ancorado_detector": saida["ancorado"],
            "classe": classificar(caso["fiel"], saida["ancorado"]),
            "termos_nao_ancorados": saida["termos_nao_ancorados"],
            "score_sobreposicao": saida["score_sobreposicao"],
            "resposta": caso["resposta"],
            "justificativa_rotulo": caso["justificativa"],
            "contexto_secoes": caso["contexto"],
            "contexto_textos": trechos,
        })

    grupos = sorted({l["grupo"] for l in linhas})
    resultado = {
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "detector": "sprint3/rag_personalizacao/ancoragem.py::validar_ancoragem",
        "casos_fonte": "sprint4/avaliacao/casos_ancoragem.json",
        "metricas_geral": metricas(linhas),
        "metricas_por_grupo": {g: metricas([l for l in linhas if l["grupo"] == g]) for g in grupos},
        "casos": linhas,
    }

    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = DIR / "execucoes" / f"validacao_ancoragem_{carimbo}.json"
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[ancoragem] {destino.relative_to(RAIZ)}")
    print(f"  geral: {resultado['metricas_geral']}")
    for g, m in resultado["metricas_por_grupo"].items():
        print(f"  {g}: {m}")
    for l in linhas:
        print(f"  {l['id']} {l['classe']} ancorado={l['ancorado_detector']} "
              f"nao_ancorados={l['termos_nao_ancorados']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
