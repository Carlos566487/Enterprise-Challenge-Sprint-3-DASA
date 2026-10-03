"""
Re-medição da ancoragem sobre respostas JÁ GRAVADAS — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Recalcula validar_ancoragem() com o código ATUAL de
sprint3/rag_personalizacao/ancoragem.py sobre as respostas e os trechos
gravados em execucoes/geracao_*.jsonl, e compara com o resultado que o
detector antigo gravou na hora da geração. Nenhuma chamada ao LLM.

Mede:
  • índice bruto de ancoragem antes × depois;
  • quantos achados de "contagem_errada" da revisão manual (números por
    extenso) passam a ser detectados;
  • respostas que MUDARAM de veredito, nos dois sentidos — em especial as que
    passaram a ser reprovadas, para conferir uma a uma se são falha real ou
    alarme falso novo.

Uso:
    python sprint4/avaliacao/reancorar.py
"""

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from sprint3.rag_personalizacao import validar_ancoragem  # noqa: E402

BATERIAS = {
    "0,43": "execucoes/geracao_limiar043_20261002_215449.jsonl",
    "0,50": "execucoes/geracao_20261003_133602.jsonl",
}
REVISAO = "execucoes/revisao_manual_validada_20261003_135236.json"


def main() -> int:
    revisao = json.loads((DIR / REVISAO).read_text(encoding="utf-8"))
    contagens = [a for a in revisao["aceitos"] if a["tipo"] == "contagem_errada"]

    saida = {"gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "detector": "sprint3/rag_personalizacao/ancoragem.py (versão atual)",
             "baterias": {}}
    novos_vereditos = {}
    for nome, arq in BATERIAS.items():
        linhas = [json.loads(x) for x in (DIR / arq).read_text(encoding="utf-8").splitlines() if x.strip()]
        resp = [l for l in linhas if l["status"] == "respondido"]
        mudancas = []
        antes_ok = depois_ok = 0
        for l in resp:
            trechos = [f["conteudo"] for f in l["fontes"]]
            novo = validar_ancoragem(l["resposta"], trechos)
            antigo = l["ancoragem"]
            antes_ok += 1 if antigo["ancorado"] else 0
            depois_ok += 1 if novo["ancorado"] else 0
            novos_vereditos[(arq, l["id"], l["perfil"], l["repeticao"])] = novo
            if bool(antigo["ancorado"]) != bool(novo["ancorado"]) or \
                    antigo["termos_nao_ancorados"] != novo["termos_nao_ancorados"]:
                mudancas.append({
                    "id": l["id"], "perfil": l["perfil"], "repeticao": l["repeticao"],
                    "antes": {"ancorado": antigo["ancorado"], "termos": antigo["termos_nao_ancorados"]},
                    "depois": {"ancorado": novo["ancorado"], "termos": novo["termos_nao_ancorados"]},
                })
        saida["baterias"][nome] = {
            "arquivo": arq, "respondidas": len(resp),
            "ancoradas_antes": antes_ok, "taxa_antes": round(antes_ok / len(resp), 4),
            "ancoradas_depois": depois_ok, "taxa_depois": round(depois_ok / len(resp), 4),
            "passaram_a_ancorado": [m for m in mudancas if m["depois"]["ancorado"] and not m["antes"]["ancorado"]],
            "passaram_a_nao_ancorado": [m for m in mudancas if not m["depois"]["ancorado"] and m["antes"]["ancorado"]],
            "continuam_nao_ancorados": [m for m in mudancas if not m["depois"]["ancorado"] and not m["antes"]["ancorado"]],
        }

    detectadas = []
    for a in contagens:
        v = novos_vereditos.get((a["arquivo"], a["id"], a["perfil"], a["repeticao"]))
        detectadas.append({"id": a["id"], "perfil": a["perfil"], "repeticao": a["repeticao"],
                           "arquivo": a["arquivo"], "citacao": a["citacao"],
                           "detectada_agora": bool(v) and not v["ancorado"],
                           "termos": v["termos_nao_ancorados"] if v else None})
    saida["contagens_por_extenso"] = {
        "total_revisao_manual": len(contagens),
        "detectadas_agora": sum(d["detectada_agora"] for d in detectadas),
        "detalhe": detectadas,
    }

    destino = DIR / "execucoes" / f"reancoragem_{datetime.now():%Y%m%d_%H%M%S}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    for nome, b in saida["baterias"].items():
        print(f"{nome}: bruto {b['ancoradas_antes']}/{b['respondidas']} ({b['taxa_antes']}) -> "
              f"{b['ancoradas_depois']}/{b['respondidas']} ({b['taxa_depois']}) | "
              f"viraram ancoradas {len(b['passaram_a_ancorado'])} | "
              f"viraram NÃO ancoradas {len(b['passaram_a_nao_ancorado'])}")
        for m in b["passaram_a_nao_ancorado"] + b["continuam_nao_ancorados"]:
            print("   NÃO ANCORADA:", m["id"], m["perfil"], "r%d" % m["repeticao"], m["depois"]["termos"])
    c = saida["contagens_por_extenso"]
    print(f"contagens por extenso detectadas: {c['detectadas_agora']}/{c['total_revisao_manual']}")
    for d in c["detalhe"]:
        if not d["detectada_agora"]:
            print("   NÃO detectada:", d["id"], d["perfil"], "r%d" % d["repeticao"], "|", d["citacao"], "|", d["termos"])
    print(f"[reancoragem] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
