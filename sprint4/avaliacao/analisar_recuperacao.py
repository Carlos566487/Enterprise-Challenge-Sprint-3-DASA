"""
Análise derivada da recuperação e contabilidade de chamadas — Sprint 4
Engenheiro de IA & PLN — Avaliação e Validação

Não executa busca nenhuma: lê a saída bruta de avaliar_recuperacao.py
(execucoes/recuperacao_*.json) e deriva, de forma determinística:

  1. Métricas por perfil e por categoria (precisão e recall de contexto).
  2. Roteamento: comportamento obtido (algum trecho ≥ limiar ou sem_contexto)
     x comportamento esperado de perguntas.json.
  3. Varredura de limiar: o que cada limiar entre 0,30 e 0,60 produziria,
     recalculado sobre o ranking completo gravado. Como a busca é
     determinística e cada configuração de perfil é o prefixo do ranking
     (verificado na execução bruta), a derivação é exata para esses dados.
  4. Contabilidade de chamadas ao LLM para a Parte B (N=3; N=5 nas críticas),
     separando as evitadas por guardrail e por sem_contexto.

Uso:
    python sprint4/avaliacao/analisar_recuperacao.py execucoes/recuperacao_<ts>.json
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]

PERFIS_TOP_K = {"leigo_ansioso": 3, "leigo_curioso": 4, "medico": 5}
LIMIARES = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
N_PADRAO, N_CRITICA = 3, 5


def _div(a, b):
    return round(a / b, 4) if b else None


def _media(valores):
    v = [x for x in valores if x is not None]
    return round(sum(v) / len(v), 4) if v else None


def recortar(ranking, top_k, limiar):
    return [s for s, sim in ranking[:top_k] if sim >= limiar]


def metricas(secoes, pergunta):
    essenciais = set(pergunta["chunks_essenciais"])
    relevantes = essenciais | set(pergunta["chunks_aceitaveis"])
    return {
        "precisao": _div(sum(1 for s in secoes if s in relevantes), len(secoes)),
        "recall": _div(sum(1 for s in essenciais if s in secoes), len(essenciais)),
    }


def roteamento(secoes, pergunta):
    obtido = "com_contexto" if secoes else "sem_contexto"
    esperado = pergunta["comportamento_esperado"]
    if esperado == "respondido":
        ok = obtido == "com_contexto"
    else:  # sem_contexto / sem_contexto_ou_esclarecimento
        ok = obtido == "sem_contexto"
    return obtido, ok


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    caminho = Path(argv[0]) if argv else sorted((DIR / "execucoes").glob("recuperacao_*.json"))[-1]
    if not caminho.is_absolute():
        caminho = (DIR / caminho) if (DIR / caminho).exists() else (RAIZ / caminho)
    bruto = json.loads(caminho.read_text(encoding="utf-8"))
    conjunto = json.loads((DIR / "perguntas.json").read_text(encoding="utf-8"))
    por_id = {p["id"]: p for p in conjunto["perguntas"]}
    limiar_prod = bruto["configuracao"]["similaridade_minima"]

    # ── 1 e 2: estado atual (limiar de produção) ─────────────────────────────
    tabela = []
    for r in bruto["resultados"]:
        p = por_id[r["id"]]
        linha = {"id": r["id"], "categoria": r["categoria"],
                 "similaridade_max": r["similaridade_max"],
                 "essenciais_no_ranking": r["essenciais_no_ranking"],
                 "deterministico": r["determinismo"]["identico_byte_a_byte"],
                 "prefixo_ok": all(v["igual_ao_prefixo_do_ranking"] for v in r["perfis"].values()),
                 "perfis": {}}
        for perfil, top_k in PERFIS_TOP_K.items():
            secoes = [s for s, _ in r["perfis"][perfil]["trechos"]]
            obtido, ok = roteamento(secoes, p)
            linha["perfis"][perfil] = {"secoes": secoes, **metricas(secoes, p),
                                       "roteamento_obtido": obtido, "roteamento_ok": ok}
        tabela.append(linha)

    legitimas = [l for l in tabela if por_id[l["id"]]["comportamento_esperado"] == "respondido"]
    sem_resposta = [l for l in tabela if por_id[l["id"]]["comportamento_esperado"] != "respondido"]

    agregados = {}
    for perfil in PERFIS_TOP_K:
        agregados[perfil] = {
            "precisao_media_legitimas_com_contexto": _media(
                [l["perfis"][perfil]["precisao"] for l in legitimas]),
            "recall_medio_legitimas": _media(
                [l["perfis"][perfil]["recall"] if l["perfis"][perfil]["recall"] is not None else 0.0
                 for l in legitimas]),
            "legitimas_sem_nenhum_trecho": [l["id"] for l in legitimas
                                            if not l["perfis"][perfil]["secoes"]],
            "sem_resposta_que_receberam_trecho": [l["id"] for l in sem_resposta
                                                  if l["perfis"][perfil]["secoes"]],
            "roteamento_correto": sum(l["perfis"][perfil]["roteamento_ok"] for l in tabela),
            "total": len(tabela),
        }

    por_categoria = {}
    for cat in sorted({l["categoria"] for l in tabela}):
        linhas = [l for l in tabela if l["categoria"] == cat]
        por_categoria[cat] = {
            "perguntas": [l["id"] for l in linhas],
            "similaridade_max": {l["id"]: l["similaridade_max"] for l in linhas},
            "similaridade_max_media": _media([l["similaridade_max"] for l in linhas]),
            "recall_medio_leigo_ansioso": _media(
                [l["perfis"]["leigo_ansioso"]["recall"] for l in linhas]),
        }

    # ── 3: varredura de limiar ──────────────────────────────────────────────
    varredura = []
    for limiar in LIMIARES:
        for perfil, top_k in PERFIS_TOP_K.items():
            rec, prec, zero, falso = [], [], [], []
            for r in bruto["resultados"]:
                p = por_id[r["id"]]
                secoes = recortar(r["ranking_completo"], top_k, limiar)
                m = metricas(secoes, p)
                if p["comportamento_esperado"] == "respondido":
                    rec.append(m["recall"] if m["recall"] is not None else 0.0)
                    if m["precisao"] is not None:
                        prec.append(m["precisao"])
                    if not secoes:
                        zero.append(r["id"])
                elif secoes:
                    falso.append(r["id"])
            varredura.append({
                "limiar": limiar, "perfil": perfil, "top_k": top_k,
                "recall_medio_legitimas": _media(rec),
                "precisao_media_quando_ha_contexto": _media(prec),
                "legitimas_sem_trecho": zero,
                "sem_resposta_com_trecho": falso,
            })

    separacao = {
        "menor_similaridade_de_chunk_essencial": min(
            (v["similaridade"], l["id"], s) for l in legitimas
            for s, v in l["essenciais_no_ranking"].items()),
        "maior_similaridade_em_pergunta_sem_resposta": max(
            (l["similaridade_max"], l["id"]) for l in sem_resposta),
    }

    # ── 4: contabilidade de chamadas da Parte B ─────────────────────────────
    recuperacao_por_id = {l["id"]: l for l in tabela}
    # sem_contexto é "correto" quando a pergunta não tem resposta na base e
    # "indevido" quando tinha (falha de recuperação, não economia).
    contas = {"chamadas_llm": 0, "evitadas_guardrail": 0,
              "evitadas_sem_contexto_correto": 0, "evitadas_sem_contexto_indevido": 0}
    detalhe = []
    for p in conjunto["perguntas"]:
        n = N_CRITICA if p["critica_n5"] else N_PADRAO
        for perfil in PERFIS_TOP_K:
            if p["categoria"] == "guardrail":
                destino = "evitadas_guardrail"
            elif not recuperacao_por_id[p["id"]]["perfis"][perfil]["secoes"]:
                destino = ("evitadas_sem_contexto_indevido"
                           if p["comportamento_esperado"] == "respondido"
                           else "evitadas_sem_contexto_correto")
            else:
                destino = "chamadas_llm"
            contas[destino] += n
            detalhe.append({"id": p["id"], "perfil": perfil, "n": n, "destino": destino})
    contas["execucoes_totais"] = sum(d["n"] for d in detalhe)

    saida = {
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fonte_bruta": str(caminho.relative_to(RAIZ)).replace("\\", "/"),
        "limiar_producao": limiar_prod,
        "deterministico_todas": all(l["deterministico"] for l in tabela),
        "prefixo_ok_todas": all(l["prefixo_ok"] for l in tabela),
        "agregados_por_perfil": agregados,
        "por_categoria": por_categoria,
        "separacao_de_similaridade": separacao,
        "varredura_de_limiar": varredura,
        "contabilidade_parte_b": {
            "regra": f"N={N_PADRAO} por pergunta e perfil; N={N_CRITICA} nas críticas",
            "natureza": ("derivada da recuperação medida e do guardrail — ambos determinísticos; "
                         "a Parte B confirma com o instrumento de custo"),
            **contas,
            "detalhe": detalhe,
        },
        "por_pergunta": tabela,
    }
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = DIR / "execucoes" / f"analise_recuperacao_{carimbo}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({k: saida[k] for k in ("deterministico_todas", "prefixo_ok_todas",
                                            "agregados_por_perfil", "separacao_de_similaridade")},
                     ensure_ascii=False, indent=1))
    for v in varredura:
        if v["perfil"] == "leigo_ansioso":
            print(f"limiar {v['limiar']:.2f} k=3 recall={v['recall_medio_legitimas']} "
                  f"prec={v['precisao_media_quando_ha_contexto']} "
                  f"legit_sem_trecho={v['legitimas_sem_trecho']} falso_contexto={v['sem_resposta_com_trecho']}")
    c = saida["contabilidade_parte_b"]
    print(f"contabilidade: execucoes={c['execucoes_totais']} llm={c['chamadas_llm']} "
          f"guardrail={c['evitadas_guardrail']} sc_correto={c['evitadas_sem_contexto_correto']} sc_indevido={c['evitadas_sem_contexto_indevido']}")
    print(f"[analise] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
