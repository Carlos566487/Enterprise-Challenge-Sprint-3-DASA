"""
Curva de limiar e separação entre populações — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Lê um ou mais arquivos de coletar_rankings.py e aplica os cortes
ANALITICAMENTE, reproduzindo a ordem de produção de buscar_trechos():
primeiro top_k (n_results da consulta), depois o filtro de similaridade.
A validade do método foi conferida: os 18 pontos da varredura real
(varredura_limiar_20260928_205359.json, 288 buscas) batem com a derivação.

Para cada modelo:
  • curva: limiar 0,35 → 0,60 (passo 0,01) × top_k 3, 4, 5 (perfis) e 6, 10
    (análise de top_k; 6 é a posição do essencial da F3) —
      ganho: respondíveis (11) com ≥1 chunk essencial; recall e precisão;
      custo: perguntas SEM resposta (5) que recebem trecho, e trechos
             irrelevantes admitidos nas respondíveis;
      X2 (Parkinson): o que recebe em cada ponto;
      guardrail (4): quantas receberiam trecho — só relevante no dashboard,
             que busca antes do guardrail (no contrato v1.0 nem chegam à busca);
  • separação: melhor similaridade de chunk essencial de cada respondível ×
    similaridade máxima de cada pergunta sem resposta; AUC (probabilidade de
    uma respondível pontuar acima de uma sem resposta) e se existe algum
    limiar que separe as duas populações;
  • fronteira de compromisso: pontos não dominados em (ganho, custo);
  • top_k: posição dos chunks essenciais no top 10 real.

Uso:
    python sprint4/avaliacao/curva_limiar.py execucoes/rankings_producao_<ts>.json \
        [execucoes/rankings_multilingue_<ts>.json]
"""

import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]

LIMIARES = [round(0.35 + 0.01 * i, 2) for i in range(26)]
TOP_KS = (3, 4, 5, 6, 10)


def _div(a, b):
    return round(a / b, 4) if b else None


def cortar(ranking, top_k, limiar):
    return [(s, sim) for s, sim in ranking[:top_k] if sim >= limiar]


def ponto(resultados, perguntas, limiar, top_k):
    resp, sem, guard = [], [], []
    x2 = None
    for r in resultados:
        p = perguntas[r["id"]]
        secoes = [s for s, _ in cortar(r["top25"], top_k, limiar)]
        if p["categoria"] == "guardrail":
            guard.append((r["id"], secoes))
            continue
        if r["id"] == "X2":
            x2 = secoes
        if p["comportamento_esperado"] == "respondido":
            ess = set(p["chunks_essenciais"])
            rel = ess | set(p["chunks_aceitaveis"])
            resp.append({
                "id": r["id"], "secoes": secoes,
                "tem_essencial": bool(ess & set(secoes)),
                "recall": _div(len(ess & set(secoes)), len(ess)),
                "precisao": _div(sum(1 for s in secoes if s in rel), len(secoes)),
                "irrelevantes": [s for s in secoes if s not in rel],
            })
        else:
            sem.append((r["id"], secoes))
    recs = [x["recall"] for x in resp]
    precs = [x["precisao"] for x in resp if x["precisao"] is not None]
    return {
        "limiar": limiar, "top_k": top_k,
        "respondiveis_com_essencial": sum(x["tem_essencial"] for x in resp),
        "respondiveis_total": len(resp),
        "respondiveis_sem_essencial": [x["id"] for x in resp if not x["tem_essencial"]],
        "recall_medio": round(statistics.mean(recs), 4),
        "precisao_media": round(statistics.mean(precs), 4) if precs else None,
        "sem_resposta_com_trecho": [i for i, s in sem if s],
        "sem_resposta_total": len(sem),
        "irrelevantes_admitidos": sum(len(x["irrelevantes"]) for x in resp),
        "x2_recebe": x2,
        "guardrail_com_trecho": [i for i, s in guard if s],
    }


def separacao(resultados, perguntas):
    melhor_essencial, max_sem = {}, {}
    for r in resultados:
        p = perguntas[r["id"]]
        if p["categoria"] == "guardrail":
            continue
        sims = dict(r["top25"])
        if p["comportamento_esperado"] == "respondido":
            vals = [sims[s] for s in p["chunks_essenciais"] if s in sims]
            melhor_essencial[r["id"]] = max(vals) if vals else None
        else:
            max_sem[r["id"]] = r["top25"][0][1]
    a = [v for v in melhor_essencial.values() if v is not None]
    b = list(max_sem.values())
    pares = [(x, y) for x in a for y in b]
    auc = sum(1.0 if x > y else 0.5 if x == y else 0.0 for x, y in pares) / len(pares)
    return {
        "melhor_essencial_por_respondivel": melhor_essencial,
        "maxima_por_pergunta_sem_resposta": max_sem,
        "menor_melhor_essencial": min(a), "maior_sem_resposta": max(b),
        "existe_limiar_que_separa": min(a) > max(b),
        "auc_separacao": round(auc, 4),
        "sem_resposta_acima_da_menor_respondivel": [i for i, v in max_sem.items() if v >= min(a)],
        "respondiveis_abaixo_da_maior_sem_resposta": [i for i, v in melhor_essencial.items()
                                                     if v is not None and v <= max(b)],
    }


def faixa(resultados):
    todas = [sim for r in resultados for _, sim in r["top25"]]
    amplitudes = [r["top25"][0][1] - r["top25"][-1][1] for r in resultados]
    margens = [r["top25"][0][1] - r["top25"][1][1] for r in resultados]
    return {"n": len(todas), "min": min(todas), "max": max(todas),
            "desvio": round(statistics.pstdev(todas), 4),
            "p05": sorted(todas)[int(0.05 * (len(todas) - 1))],
            "p95": sorted(todas)[int(0.95 * (len(todas) - 1))],
            "amplitude_media_por_pergunta": round(statistics.mean(amplitudes), 4),
            "margem_top1_top2_media": round(statistics.mean(margens), 4),
            "top1_medio": round(statistics.mean(r["top25"][0][1] for r in resultados), 4)}


def fronteira(pontos):
    """Pontos não dominados: mais ganho e menos custo (sem-resposta, irrelevantes)."""
    def custo(p):
        return (len(p["sem_resposta_com_trecho"]), p["irrelevantes_admitidos"])
    nd = []
    for p in pontos:
        dominado = any(q["respondiveis_com_essencial"] >= p["respondiveis_com_essencial"]
                       and custo(q) <= custo(p) and q is not p
                       and (q["respondiveis_com_essencial"] > p["respondiveis_com_essencial"]
                            or custo(q) < custo(p))
                       for q in pontos)
        if not dominado:
            nd.append(p)
    # colapsa limiares consecutivos com o mesmo resultado
    faixas = []
    for p in sorted(nd, key=lambda x: x["limiar"]):
        chave = (p["respondiveis_com_essencial"], tuple(p["sem_resposta_com_trecho"]),
                 p["irrelevantes_admitidos"])
        if faixas and faixas[-1]["chave"] == chave:
            faixas[-1]["ate"] = p["limiar"]
        else:
            faixas.append({"chave": chave, "de": p["limiar"], "ate": p["limiar"]})
    return [{"limiares": f"{f['de']:.2f}–{f['ate']:.2f}", "respondiveis_com_essencial": f["chave"][0],
             "sem_resposta_com_trecho": list(f["chave"][1]), "irrelevantes_admitidos": f["chave"][2]}
            for f in faixas]


def qualidade_ranking(resultados, perguntas):
    """
    Métricas SEM limiar, só da ordenação: para cada respondível, a posição do
    melhor chunk essencial no top 25 real. hits@1, hits@3 e MRR. Separa a
    pergunta "o modelo ordena bem?" da pergunta "algum limiar separa?".
    """
    posicoes = {}
    for r in resultados:
        p = perguntas[r["id"]]
        if p["comportamento_esperado"] != "respondido":
            continue
        pos = {s: i + 1 for i, (s, _) in enumerate(r["top25"])}
        achadas = [pos[s] for s in p["chunks_essenciais"] if s in pos]
        posicoes[r["id"]] = min(achadas) if achadas else None
    validas = [v for v in posicoes.values()]
    return {
        "posicao_melhor_essencial": posicoes,
        "hits_at_1": sum(1 for v in validas if v == 1),
        "hits_at_3": sum(1 for v in validas if v is not None and v <= 3),
        "mrr": round(statistics.mean(1 / v if v else 0.0 for v in validas), 4),
        "total": len(validas),
    }


def posicoes_top10(resultados, perguntas):
    linhas = []
    for r in resultados:
        p = perguntas[r["id"]]
        if p["comportamento_esperado"] != "respondido":
            continue
        pos = {s: i + 1 for i, (s, _) in enumerate(r["top10"])}
        sims = dict(r["top10"])
        for s in p["chunks_essenciais"]:
            linhas.append({"id": r["id"], "chunk": s, "posicao_top10": pos.get(s),
                           "similaridade": sims.get(s), "fora_do_top3": pos.get(s, 99) > 3})
    return linhas


def analisar_modelo(caminho, perguntas):
    bruto = json.loads(caminho.read_text(encoding="utf-8"))
    res = bruto["resultados"]
    pontos = {k: [ponto(res, perguntas, t, k) for t in LIMIARES] for k in TOP_KS}
    return {
        "arquivo": str(caminho.relative_to(RAIZ)).replace("\\", "/"),
        "modelo": bruto["modelo"],
        "faixa_similaridades": faixa(res),
        "separacao": separacao(res, perguntas),
        "qualidade_ranking": qualidade_ranking(res, perguntas),
        "curva": {str(k): v for k, v in pontos.items()},
        "fronteira_top3": fronteira(pontos[3]),
        "existe_ponto_perfeito": [
            {"top_k": k, "limiar": p["limiar"]} for k in TOP_KS for p in pontos[k]
            if p["respondiveis_com_essencial"] == p["respondiveis_total"]
            and not p["sem_resposta_com_trecho"]],
        "posicoes_essenciais_top10": posicoes_top10(res, perguntas),
        "a1_x2": {i: dict(r["top25"][:3]) | {"top1": r["top25"][0]}
                  for r in res for i in [r["id"]] if i in ("A1", "X2")},
    }


def tabela_md(analise, k=3):
    linhas = ["| Limiar | Respondíveis com essencial (de 11) | Recall | Precisão | "
              "**Sem resposta que recebem trecho (de 5)** | Irrelevantes admitidos | X2 (Parkinson) recebe |",
              "|---:|---:|---:|---:|---|---:|---|"]
    for p in analise["curva"][str(k)]:
        sem = ", ".join(p["sem_resposta_com_trecho"]) or "—"
        x2 = ", ".join(p["x2_recebe"]) or "—"
        prec = "—" if p["precisao_media"] is None else f"{p['precisao_media']:.2f}"
        linhas.append(f"| {p['limiar']:.2f} | {p['respondiveis_com_essencial']} | {p['recall_medio']:.2f} | "
                      f"{prec} | "
                      f"**{len(p['sem_resposta_com_trecho'])}** ({sem}) | {p['irrelevantes_admitidos']} | {x2} |")
    return "\n".join(linhas)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    perguntas = {p["id"]: p for p in
                 json.loads((DIR / "perguntas.json").read_text(encoding="utf-8"))["perguntas"]}
    analises = []
    for arg in argv:
        caminho = Path(arg)
        if not caminho.is_absolute():
            caminho = DIR / caminho
        analises.append(analisar_modelo(caminho, perguntas))

    saida = {"gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "metodo": "cortes analíticos sobre ranking real: top_k primeiro, filtro depois (ordem de buscar_trechos)",
             "analises": analises}
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = DIR / "execucoes" / f"curva_limiar_{carimbo}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")

    for a in analises:
        print(f"\n===== {a['modelo']} =====")
        print("faixa:", a["faixa_similaridades"])
        s = a["separacao"]
        print("separação: menor essencial", s["menor_melhor_essencial"], "| maior sem-resposta",
              s["maior_sem_resposta"], "| separa?", s["existe_limiar_que_separa"], "| AUC", s["auc_separacao"])
        print("  melhor essencial:", s["melhor_essencial_por_respondivel"])
        print("  máx sem resposta:", s["maxima_por_pergunta_sem_resposta"])
        print("ranking (sem limiar):", a["qualidade_ranking"])
        print("ponto perfeito (11/11 e 0 sem-resposta):", a["existe_ponto_perfeito"] or "NENHUM")
        print("fronteira top3:")
        for f in a["fronteira_top3"]:
            print("  ", f)
        print("essenciais fora do top 3:", [(l["id"], l["chunk"], l["posicao_top10"], l["similaridade"])
                                            for l in a["posicoes_essenciais_top10"] if l["fora_do_top3"]])
        print("A1/X2:", a["a1_x2"])
    print(f"\n[curva] {destino.relative_to(RAIZ)}")
    (DIR / "execucoes" / f"curva_limiar_{carimbo}_tabelas.md").write_text(
        "\n\n".join(f"### {a['modelo']} — top_k=3\n\nFonte: `{destino.name}`\n\n{tabela_md(a)}"
                    for a in analises), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
