"""
Varredura do limiar de similaridade — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Chama a busca REAL (sprint2/vetorial/buscar.py::buscar_contexto) com o
parâmetro opcional `similaridade_minima`, que já existe na assinatura com
padrão 0,50 — buscar.py não é alterado e nenhum chamador muda de
comportamento. Para cada limiar de 0,35 a 0,60 (passo 0,05) e cada top_k de
perfil (3, 4, 5), roda as 16 perguntas não-guardrail de perguntas.json.

Curva entregue, por ponto:
  • respondíveis recuperadas — das 11 perguntas com resposta na base, quantas
    recebem ao menos um chunk ESSENCIAL (e quantas recebem algum trecho);
  • ruído admitido — chunks fora de essenciais ∪ aceitáveis recuperados nas
    perguntas respondíveis, e perguntas SEM resposta que recebem trecho;
  • recall e precisão médios de contexto.

Critério do ponto ótimo (fixado neste arquivo antes da execução real, mas
depois de ver a varredura derivada do ranking gravado — não é cego):
  1. maximizar respondíveis com chunk essencial;
  2. entre empatados, minimizar perguntas sem resposta que recebem trecho;
  3. entre empatados, minimizar chunks irrelevantes admitidos;
  4. entre empatados, o MAIOR limiar (mais conservador).

Também confere cada ponto contra o ranking completo gravado em
execucoes/recuperacao_*.json (prefixo filtrado): a varredura derivada do
relatório anterior precisa bater com a varredura real.

Uso:
    python sprint4/avaliacao/varrer_limiar.py execucoes/recuperacao_<ts>.json
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from sprint2.vetorial.buscar import SIMILARIDADE_MINIMA, buscar_contexto  # noqa: E402

LIMIARES = (0.35, 0.40, 0.45, 0.50, 0.55, 0.60)
TOP_KS = {"leigo_ansioso": 3, "leigo_curioso": 4, "medico": 5}


def _media(v):
    v = [x for x in v if x is not None]
    return round(sum(v) / len(v), 4) if v else None


def avaliar_ponto(perguntas, limiar, top_k, rankings):
    linhas, divergencias = [], []
    for p in perguntas:
        busca = buscar_contexto(p["pergunta"], top_k=top_k, similaridade_minima=limiar)
        secoes = [t["secao"] for t in busca["trechos"]]
        derivado = [s for s, sim in rankings[p["id"]][:top_k] if sim >= limiar]
        if secoes != derivado:
            divergencias.append({"id": p["id"], "real": secoes, "derivado": derivado})
        essenciais = set(p["chunks_essenciais"])
        relevantes = essenciais | set(p["chunks_aceitaveis"])
        linhas.append({
            "id": p["id"], "respondivel": p["comportamento_esperado"] == "respondido",
            "secoes": secoes,
            "similaridades": [t["similaridade"] for t in busca["trechos"]],
            "essenciais_recuperados": sorted(essenciais & set(secoes)),
            "irrelevantes": [s for s in secoes if s not in relevantes],
            "recall": (round(len(essenciais & set(secoes)) / len(essenciais), 4)
                       if essenciais else None),
            "precisao": (round(sum(1 for s in secoes if s in relevantes) / len(secoes), 4)
                         if secoes else None),
        })

    resp = [l for l in linhas if l["respondivel"]]
    sem = [l for l in linhas if not l["respondivel"]]
    return {
        "limiar": limiar, "top_k": top_k,
        "respondiveis_total": len(resp),
        "respondiveis_com_essencial": sum(1 for l in resp if l["essenciais_recuperados"]),
        "respondiveis_com_algum_trecho": sum(1 for l in resp if l["secoes"]),
        "sem_resposta_total": len(sem),
        "sem_resposta_com_trecho": [l["id"] for l in sem if l["secoes"]],
        "irrelevantes_admitidos": sum(len(l["irrelevantes"]) for l in resp),
        "recall_medio": _media([l["recall"] if l["recall"] is not None else 0.0 for l in resp]),
        "precisao_media": _media([l["precisao"] for l in resp]),
        "confere_com_derivado": not divergencias,
        "divergencias": divergencias,
        "perguntas": linhas,
    }


def escolher_otimo(pontos):
    return sorted(pontos, key=lambda p: (-p["respondiveis_com_essencial"],
                                         len(p["sem_resposta_com_trecho"]),
                                         p["irrelevantes_admitidos"],
                                         -p["limiar"]))[0]


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    caminho = Path(argv[0])
    if not caminho.is_absolute():
        caminho = DIR / caminho
    bruto = json.loads(caminho.read_text(encoding="utf-8"))
    rankings = {r["id"]: r["ranking_completo"] for r in bruto["resultados"]}
    perguntas = [p for p in json.loads((DIR / "perguntas.json").read_text(encoding="utf-8"))["perguntas"]
                 if p["categoria"] != "guardrail"]

    inicio = datetime.now(timezone.utc).isoformat(timespec="seconds")
    pontos = []
    for perfil, top_k in TOP_KS.items():
        for limiar in LIMIARES:
            ponto = avaliar_ponto(perguntas, limiar, top_k, rankings)
            ponto["perfil"] = perfil
            pontos.append(ponto)
            print(f"{perfil:13} k={top_k} t={limiar:.2f} essencial={ponto['respondiveis_com_essencial']}/"
                  f"{ponto['respondiveis_total']} algum={ponto['respondiveis_com_algum_trecho']} "
                  f"irrelev={ponto['irrelevantes_admitidos']} sem_resp_c_trecho={ponto['sem_resposta_com_trecho']} "
                  f"R={ponto['recall_medio']} P={ponto['precisao_media']} "
                  f"confere={ponto['confere_com_derivado']}", flush=True)

    otimos = {perfil: escolher_otimo([p for p in pontos if p["perfil"] == perfil])
              for perfil in TOP_KS}
    saida = {
        "gerado_em_utc": inicio,
        "busca": "sprint2/vetorial/buscar.py::buscar_contexto(similaridade_minima=...) — parâmetro existente, arquivo não alterado",
        "limiar_producao": SIMILARIDADE_MINIMA,
        "criterio_otimo": ["max respondíveis com essencial", "min sem-resposta com trecho",
                           "min irrelevantes admitidos", "maior limiar"],
        "otimo_por_perfil": {k: {"limiar": v["limiar"],
                                 "respondiveis_com_essencial": v["respondiveis_com_essencial"],
                                 "sem_resposta_com_trecho": v["sem_resposta_com_trecho"],
                                 "irrelevantes_admitidos": v["irrelevantes_admitidos"]}
                             for k, v in otimos.items()},
        "todos_conferem_com_derivado": all(p["confere_com_derivado"] for p in pontos),
        "pontos": pontos,
    }
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = DIR / "execucoes" / f"varredura_limiar_{carimbo}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(saida["otimo_por_perfil"], ensure_ascii=False))
    print("todos conferem com a varredura derivada:", saida["todos_conferem_com_derivado"])
    print(f"[varredura] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
