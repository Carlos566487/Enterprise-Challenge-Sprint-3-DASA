"""
Avaliação dos guardrails — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

100% sem chave de API: o bloqueio acontece antes de qualquer chamada ao LLM.

  1. Perguntas de guardrail de perguntas.json, pelo contrato v1.0
     (responder_personalizado) nos 3 perfis, com espiões no lugar da busca e
     do LLM: prova que nenhuma busca e nenhuma chamada é feita. As mesmas
     perguntas também pelo caminho do dashboard (responder_com_llm), com
     chamar_openai substituído por um contador.
  2. Mensagens de recusa: auditadas pelo revisor de linguagem da governança
     (sprint3/governanca, só leitura) — aprovada = nenhuma alteração seria
     feita — e verificadas quanto a orientar procura de profissional.
  3. Falso positivo: guardrail_fronteira.json — um caso por termo das quatro
     listas; registra se foi bloqueado e QUAL termo disparou (a primeira
     lista que casar vence, como em verificar_guardrails).
  4. Falso negativo: casos de evasão do mesmo arquivo.
  5. As perguntas legítimas de perguntas.json não podem ser bloqueadas.

Uso:
    python sprint4/avaliacao/avaliar_guardrails.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]
for _c in (RAIZ, RAIZ / "sprint2" / "agente", RAIZ / "sprint2" / "interface"):
    if str(_c) not in sys.path:
        sys.path.insert(0, str(_c))

import guardrails  # noqa: E402
import llm_connector  # noqa: E402
from sprint3.governanca.revisor_linguagem import auditar_resposta  # noqa: E402
from sprint3.rag_personalizacao import PERFIS, responder_personalizado  # noqa: E402

LISTAS = (
    ("TERMOS_DIAGNOSTICO", "diagnostico"),
    ("TERMOS_PRESCRICAO", "prescricao"),
    ("TERMOS_RISCO_ALTO", "risco_alto"),
    ("TERMOS_FORA_ESCOPO", "fora_escopo"),
)
TRECHO_FICTICIO = ["Condição: Diabetes Mellitus Tipo 2. Nível de risco: Alto."]
MARCAS_ENCAMINHAMENTO = ("profissional", "médic", "especialista")


def termo_que_dispara(pergunta: str):
    """Replica a ordem de verificar_guardrails e devolve (lista, termo)."""
    texto = guardrails.normalizar_texto(pergunta)
    for nome_lista, _ in LISTAS:
        for termo in getattr(guardrails, nome_lista):
            if termo in texto:
                return nome_lista, termo
    return None, None


def avaliar_mensagem(mensagem: str) -> dict:
    auditoria = auditar_resposta(mensagem)
    minuscula = mensagem.lower()
    return {
        "mensagem": mensagem,
        "aprovada_pelo_revisor_de_linguagem": auditoria["aprovado"],
        "alteracoes_que_o_revisor_faria": auditoria["alteracoes"],
        "orienta_profissional": any(m in minuscula for m in MARCAS_ENCAMINHAMENTO),
        "palavras": len(mensagem.split()),
    }


def perguntas_de_guardrail_pelo_contrato(perguntas: list) -> list:
    linhas = []
    for p in perguntas:
        for perfil in PERFIS:
            contagem = {"busca": 0, "llm": 0}

            def espiao_busca(pergunta, top_k):
                contagem["busca"] += 1
                return {"trechos": []}

            def espiao_llm(pergunta, trechos, modo, api_key):
                contagem["llm"] += 1
                return {"status": "respondido", "resposta": "", "categoria": "resposta_rag"}

            r = responder_personalizado(
                pergunta=p["pergunta"], perfil=perfil, usuario_id=f"aval-{p['id']}",
                api_key=None, fn_buscar=espiao_busca, fn_llm=espiao_llm,
            )
            linhas.append({
                "id": p["id"], "perfil": perfil, "pergunta": p["pergunta"],
                "status": r["status"], "categoria": r["categoria"],
                "categoria_esperada": p["categoria_guardrail_esperada"],
                "confere": r["status"] == "bloqueado"
                and r["categoria"] == p["categoria_guardrail_esperada"],
                "chamadas_busca": contagem["busca"],
                "chamadas_llm": contagem["llm"],
                "fontes": r["fontes"],
                "resposta": r["resposta"],
            })
    return linhas


def perguntas_de_guardrail_pelo_dashboard(perguntas: list) -> list:
    """Caminho do app.py: responder_com_llm() direto. chamar_openai contado."""
    linhas = []
    original = llm_connector.chamar_openai
    contagem = {"openai": 0}

    def contador(*args, **kwargs):
        contagem["openai"] += 1
        return "(não deveria ser chamado)"

    llm_connector.chamar_openai = contador
    try:
        for p in perguntas:
            antes = contagem["openai"]
            r = llm_connector.responder_com_llm(
                pergunta=p["pergunta"], trechos=TRECHO_FICTICIO,
                modo="paciente", api_key="sk-nao-usada",
            )
            linhas.append({
                "id": p["id"], "status": r["status"], "categoria": r["categoria"],
                "chamadas_openai": contagem["openai"] - antes,
            })
    finally:
        llm_connector.chamar_openai = original
    return linhas


def main() -> int:
    conjunto = json.loads((DIR / "perguntas.json").read_text(encoding="utf-8"))
    fronteira = json.loads((DIR / "guardrail_fronteira.json").read_text(encoding="utf-8"))

    g = [p for p in conjunto["perguntas"] if p["categoria"] == "guardrail"]
    legitimas = [p for p in conjunto["perguntas"] if p["categoria"] != "guardrail"]

    contrato = perguntas_de_guardrail_pelo_contrato(g)
    dashboard = perguntas_de_guardrail_pelo_dashboard(g)

    mensagens = {}
    for linha in contrato:
        mensagens.setdefault(linha["categoria"], avaliar_mensagem(linha["resposta"]))

    fp = []
    for caso in fronteira["falsos_positivos"]:
        v = guardrails.verificar_guardrails(caso["pergunta"])
        lista, termo = termo_que_dispara(caso["pergunta"])
        fp.append({
            **{k: caso[k] for k in ("id", "lista", "termo", "legitimidade",
                                    "condicao_relacionada", "pergunta")},
            "bloqueada": not v["permitido"],
            "categoria_bloqueio": v["categoria"],
            "termo_que_disparou": termo,
            "lista_que_disparou": lista,
            "disparou_pelo_termo_alvo": termo == caso["termo"],
        })

    evasao = []
    for caso in fronteira["evasao"]["casos"]:
        v = guardrails.verificar_guardrails(caso["pergunta"])
        evasao.append({**caso, "bloqueada": not v["permitido"],
                       "categoria_bloqueio": v["categoria"]})

    legit = []
    for p in legitimas:
        v = guardrails.verificar_guardrails(p["pergunta"])
        legit.append({"id": p["id"], "pergunta": p["pergunta"],
                      "bloqueada": not v["permitido"], "categoria": v["categoria"]})

    def conta(linhas, chave):
        return sum(1 for l in linhas if l[chave])

    resumo = {
        "guardrail_contrato": {
            "execucoes": len(contrato),
            "conferem": conta(contrato, "confere"),
            "chamadas_busca_total": sum(l["chamadas_busca"] for l in contrato),
            "chamadas_llm_total": sum(l["chamadas_llm"] for l in contrato),
            "fontes_vazias": sum(1 for l in contrato if l["fontes"] == []),
        },
        "guardrail_dashboard": {
            "execucoes": len(dashboard),
            "bloqueadas": sum(1 for l in dashboard if l["status"] == "bloqueado"),
            "chamadas_openai_total": sum(l["chamadas_openai"] for l in dashboard),
        },
        "falsos_positivos": {
            "casos": len(fp),
            "bloqueados": conta(fp, "bloqueada"),
            "legitimos": sum(1 for l in fp if l["legitimidade"] == "legitima"),
            "legitimos_bloqueados": sum(1 for l in fp
                                        if l["legitimidade"] == "legitima" and l["bloqueada"]),
            "disparados_por_outro_termo": [l["id"] for l in fp
                                           if l["bloqueada"] and not l["disparou_pelo_termo_alvo"]],
        },
        "evasao": {
            "casos": len(evasao),
            "bloqueados": conta(evasao, "bloqueada"),
            "nao_bloqueados": [l["id"] for l in evasao if not l["bloqueada"]],
        },
        "legitimas_do_conjunto": {
            "casos": len(legit),
            "bloqueadas_indevidamente": [l["id"] for l in legit if l["bloqueada"]],
        },
    }

    saida = {
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fontes": ["sprint4/avaliacao/perguntas.json", "sprint4/avaliacao/guardrail_fronteira.json"],
        "resumo": resumo,
        "mensagens_de_recusa": mensagens,
        "guardrail_contrato": contrato,
        "guardrail_dashboard": dashboard,
        "falsos_positivos": fp,
        "evasao": evasao,
        "legitimas_do_conjunto": legit,
    }
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = DIR / "execucoes" / f"guardrails_{carimbo}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    for cat, m in mensagens.items():
        print(cat, "| revisor aprova:", m["aprovada_pelo_revisor_de_linguagem"],
              "| orienta profissional:", m["orienta_profissional"])
    for l in fp:
        print(f"{l['id']} bloqueada={l['bloqueada']} ({l['legitimidade']}) "
              f"alvo='{l['termo']}' disparou='{l['termo_que_disparou']}'")
    print(f"[guardrails] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
