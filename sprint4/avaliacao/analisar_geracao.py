"""
Análise da camada de geração (Parte B) — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Lê a saída bruta de avaliar_geracao.py (execucoes/<rotulo>_<ts>.jsonl) e
deriva, sem nenhuma chamada nova ao LLM:

  • ancoragem (métrica principal): taxa de ancorado, score_sobreposicao e o
    catálogo de termos_nao_ancorados por resposta;
  • fatos esperados presentes e fatos_fora_da_base que apareceram — este
    segundo pega alucinação que a ancoragem não vê quando o número inventado
    coincide com outro número do contexto (ver validação do detector);
  • roteamento: status obtido x comportamento_esperado;
  • consistência da geração (camada estocástica), por (pergunta, perfil):
    similaridade de cosseno média e mínima entre as N respostas
    (all-MiniLM-L6-v2, o mesmo modelo da base) e estabilidade da ancoragem;
  • simplificação: aplicada / motivo / quebras de ancoragem;
  • custo: tokens somados do usage real devolvido pela OpenAI e custo em
    USD se, e somente se, os preços forem informados na linha de comando.

Uso:
    python sprint4/avaliacao/analisar_geracao.py execucoes/geracao_<ts>.jsonl \
        [--preco-entrada USD_POR_MILHAO --preco-saida USD_POR_MILHAO]
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]
if str(DIR) not in sys.path:
    sys.path.insert(0, str(DIR))

from instrumento_custo import estimar_custo  # noqa: E402


def _media(v):
    v = [x for x in v if x is not None]
    return round(sum(v) / len(v), 4) if v else None


def _normalizar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto.replace(",", ".").lower())


def fato_presente(fato: str, texto: str) -> bool:
    return _normalizar(fato) in _normalizar(texto)


def valores_fora_da_base(descricao: str) -> list:
    """'escore_poligênico_percentil = 67' -> ['67']; 'CRM/SP 87432' -> ['87432']."""
    lado = descricao.split("=", 1)[-1]
    return re.findall(r"\d+(?:[.,]\d+)?", lado)


def similaridade_par_a_par(textos: list, modelo) -> list:
    if len(textos) < 2 or modelo is None:
        return []
    vetores = modelo.encode(textos, normalize_embeddings=True)
    return [round(float(vetores[i] @ vetores[j]), 4) for i, j in combinations(range(len(textos)), 2)]


def carregar_modelo():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def analisar(linhas: list, perguntas: dict, modelo=None, precos=(None, None)) -> dict:
    por_resposta = []
    for l in linhas:
        p = perguntas[l["id"]]
        texto = l.get("resposta") or ""
        respondeu = l["status"] == "respondido"
        esperado = p["comportamento_esperado"]
        roteamento_ok = (l["status"] == esperado
                         or (esperado == "sem_contexto_ou_esclarecimento" and l["status"] == "sem_contexto"))
        fora = [v for d in p.get("fatos_fora_da_base", []) for v in valores_fora_da_base(d)]
        por_resposta.append({
            "id": l["id"], "perfil": l["perfil"], "repeticao": l["repeticao"],
            "status": l["status"], "roteamento_ok": roteamento_ok,
            "ancorado": l["ancoragem"]["ancorado"] if respondeu else None,
            "score_sobreposicao": l["ancoragem"]["score_sobreposicao"] if respondeu else None,
            "termos_nao_ancorados": l["ancoragem"]["termos_nao_ancorados"] if respondeu else [],
            "fatos_esperados_presentes": [f for f in p["fatos_esperados"] if fato_presente(f, texto)] if respondeu else [],
            "fatos_esperados_total": len(p["fatos_esperados"]),
            "valores_fora_da_base_na_resposta": [v for v in fora if fato_presente(v, texto)] if respondeu else [],
            "simplificacao_aplicada": l["simplificacao"]["aplicada"],
            "simplificacao_motivo": l["simplificacao"]["motivo"],
            "chamou_llm": l["chamou_llm"],
        })

    respondidas = [r for r in por_resposta if r["status"] == "respondido"]

    grupos = defaultdict(list)
    for l in linhas:
        grupos[(l["id"], l["perfil"])].append(l)
    consistencia = []
    for (pid, perfil), itens in sorted(grupos.items()):
        textos = [i["resposta"] for i in itens if i["status"] == "respondido"]
        sims = similaridade_par_a_par(textos, modelo)
        ancorados = {i["ancoragem"]["ancorado"] for i in itens if i["status"] == "respondido"}
        consistencia.append({
            "id": pid, "perfil": perfil, "n": len(itens),
            "status_distintos": sorted({i["status"] for i in itens}),
            "similaridade_media": _media(sims),
            "similaridade_minima": min(sims) if sims else None,
            "ancoragem_estavel": len(ancorados) <= 1,
            "termos_nao_ancorados_por_repeticao": [i["ancoragem"]["termos_nao_ancorados"] for i in itens],
        })

    chamadas = [c for l in linhas for c in l["chamadas_sdk"]]
    tok_in = sum(c["usage"]["prompt_tokens"] or 0 for c in chamadas)
    tok_out = sum(c["usage"]["completion_tokens"] or 0 for c in chamadas)

    return {
        "execucoes": len(linhas),
        "chamadas_llm": sum(1 for l in linhas if l["chamou_llm"]),
        "evitadas_guardrail": sum(1 for l in linhas if l["status"] == "bloqueado" and not l["chamou_llm"]),
        "evitadas_sem_contexto": sum(1 for l in linhas if l["status"] == "sem_contexto"),
        "roteamento_correto": sum(r["roteamento_ok"] for r in por_resposta),
        "ancoragem": {
            "respondidas": len(respondidas),
            "ancoradas": sum(1 for r in respondidas if r["ancorado"]),
            "taxa": round(sum(1 for r in respondidas if r["ancorado"]) / len(respondidas), 4) if respondidas else None,
            "score_sobreposicao_medio": _media([r["score_sobreposicao"] for r in respondidas]),
        },
        "valores_fora_da_base_apresentados": [r for r in por_resposta if r["valores_fora_da_base_na_resposta"]],
        "simplificacao": {
            "aplicada": sum(1 for r in por_resposta if r["simplificacao_aplicada"]),
            "quebrou_ancoragem": sum(1 for r in por_resposta if r["simplificacao_motivo"] == "quebrou_ancoragem"),
        },
        "custo": {
            "tokens_entrada": tok_in, "tokens_saida": tok_out,
            "chamadas_com_usage": sum(1 for c in chamadas if c["usage"]["total_tokens"] is not None),
            "tokens_por_chamada_media": round((tok_in + tok_out) / len(chamadas), 1) if chamadas else None,
            "usd": estimar_custo(tok_in, tok_out, *precos),
            "usd_nota": None if precos[0] is not None else "NÃO CALCULADO — preços não informados",
            "modelos_respondidos": sorted({c["modelo_respondido"] for c in chamadas if c["modelo_respondido"]}),
            "parametros_enviados_distintos": sorted({json.dumps(c["parametros_enviados"], sort_keys=True)
                                                    for c in chamadas}),
        },
        "consistencia_geracao": consistencia,
        "por_resposta": por_resposta,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("entrada")
    parser.add_argument("--preco-entrada", type=float, default=None)
    parser.add_argument("--preco-saida", type=float, default=None)
    parser.add_argument("--sem-similaridade", action="store_true",
                        help="não carrega o modelo de embeddings (similaridade = NÃO MEDIDO)")
    args = parser.parse_args(argv)

    caminho = Path(args.entrada)
    if not caminho.is_absolute():
        caminho = DIR / caminho
    linhas = [json.loads(x) for x in caminho.read_text(encoding="utf-8").splitlines() if x.strip()]
    perguntas = {p["id"]: p for p in
                 json.loads((DIR / "perguntas.json").read_text(encoding="utf-8"))["perguntas"]}

    modelo = None if args.sem_similaridade else carregar_modelo()
    resultado = analisar(linhas, perguntas, modelo, (args.preco_entrada, args.preco_saida))
    resultado["fonte_bruta"] = str(caminho.relative_to(RAIZ)).replace("\\", "/")
    resultado["gerado_em_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    destino = caminho.with_name(f"analise_{caminho.stem}.json")
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: resultado[k] for k in ("execucoes", "chamadas_llm", "evitadas_guardrail",
                                                "evitadas_sem_contexto", "roteamento_correto",
                                                "ancoragem", "simplificacao", "custo")},
                     ensure_ascii=False, indent=1))
    print(f"[analise_geracao] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
