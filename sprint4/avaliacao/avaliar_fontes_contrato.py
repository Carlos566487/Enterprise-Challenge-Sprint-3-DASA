"""
Fontes no nível do contrato — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Verifica o campo `fontes` de responder_personalizado() (contrato v1.0) e de
responder_com_linguagem_simples() (contrato de integração v1.0) em TODOS os
caminhos de status. Aqui se testa MECANISMO, não qualidade: a busca é a real
(sprint2/vetorial/buscar.py) quando o caminho exige trechos, e o LLM é
substituído por respostas fixas — nenhuma métrica de qualidade de geração
sai deste script.

Regra verificada:
  • quando há resposta baseada em trechos (respondido, nao_ancorado):
    fontes não vazia e cada item com conteudo, secao, fonte, similaridade;
  • quando não há trecho usado (bloqueado, sem_contexto, bloqueio interno
    do agente): fontes == [].
  • o adaptador de integração devolve exatamente as mesmas fontes.

Uso:
    python sprint4/avaliacao/avaliar_fontes_contrato.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from sprint3.integracao import responder_com_linguagem_simples  # noqa: E402
from sprint3.rag_personalizacao import responder_personalizado  # noqa: E402

CHAVES_FONTE = ("conteudo", "secao", "fonte", "similaridade")


def llm_copia_primeiro_trecho(pergunta, trechos, modo, api_key):
    """Resposta fixa ancorada: devolve o primeiro trecho recuperado."""
    return {"status": "respondido", "resposta": trechos[0], "categoria": "resposta_rag"}


def llm_inventa_numero(pergunta, trechos, modo, api_key):
    """Resposta fixa NÃO ancorada: número inexistente no relatório."""
    return {"status": "respondido",
            "resposta": "Seu escore poligênico está no percentil 97.",
            "categoria": "resposta_rag"}


def llm_bloqueio_interno(pergunta, trechos, modo, api_key):
    """Simula o agente bloqueando depois do pré-check (defesa dupla)."""
    return {"status": "bloqueado", "resposta": "Bloqueado pelo agente.",
            "categoria": "diagnostico", "fontes": []}


def busca_vazia(pergunta, top_k):
    return {"trechos": []}


CENARIOS = (
    {"nome": "respondido_ancorado", "pergunta": "Qual é o meu nível de risco para diabetes tipo 2?",
     "fn_buscar": None, "fn_llm": llm_copia_primeiro_trecho, "politica": "sinalizar",
     "status_esperado": "respondido", "fontes_esperadas": "preenchidas"},
    {"nome": "respondido_nao_ancorado_sinalizar", "pergunta": "Qual é o meu nível de risco para diabetes tipo 2?",
     "fn_buscar": None, "fn_llm": llm_inventa_numero, "politica": "sinalizar",
     "status_esperado": "respondido", "fontes_esperadas": "preenchidas"},
    {"nome": "nao_ancorado_bloquear", "pergunta": "Qual é o meu nível de risco para diabetes tipo 2?",
     "fn_buscar": None, "fn_llm": llm_inventa_numero, "politica": "bloquear",
     "status_esperado": "nao_ancorado", "fontes_esperadas": "preenchidas"},
    {"nome": "bloqueado_guardrail", "pergunta": "Qual remédio devo tomar para prevenir a pressão alta?",
     "fn_buscar": None, "fn_llm": llm_copia_primeiro_trecho, "politica": "sinalizar",
     "status_esperado": "bloqueado", "fontes_esperadas": "vazias"},
    {"nome": "sem_contexto", "pergunta": "Qual é o meu tipo sanguíneo?",
     "fn_buscar": busca_vazia, "fn_llm": llm_copia_primeiro_trecho, "politica": "sinalizar",
     "status_esperado": "sem_contexto", "fontes_esperadas": "vazias"},
    {"nome": "bloqueio_interno_do_agente", "pergunta": "Qual é o meu nível de risco para diabetes tipo 2?",
     "fn_buscar": None, "fn_llm": llm_bloqueio_interno, "politica": "sinalizar",
     "status_esperado": "bloqueado", "fontes_esperadas": "vazias"},
)


def verificar_fontes(fontes: list, esperado: str) -> dict:
    if esperado == "vazias":
        return {"ok": fontes == [], "detalhe": f"{len(fontes)} fontes (esperado 0)"}
    faltando = [
        {"indice": i, "chaves_ausentes": [k for k in CHAVES_FONTE if k not in f]}
        for i, f in enumerate(fontes) if any(k not in f for k in CHAVES_FONTE)
    ]
    tipos_ok = all(isinstance(f.get("similaridade"), (int, float))
                   and isinstance(f.get("conteudo"), str) and f.get("conteudo")
                   for f in fontes)
    return {
        "ok": bool(fontes) and not faltando and tipos_ok,
        "detalhe": f"{len(fontes)} fontes; itens incompletos={faltando}; tipos_ok={tipos_ok}",
    }


def main() -> int:
    linhas = []
    for perfil in ("leigo_ansioso", "leigo_curioso", "medico"):
        for c in CENARIOS:
            kwargs = dict(pergunta=c["pergunta"], perfil=perfil,
                          usuario_id=f"fontes-{c['nome']}", api_key=None,
                          politica_ancoragem=c["politica"], fn_llm=c["fn_llm"])
            if c["fn_buscar"] is not None:
                kwargs["fn_buscar"] = c["fn_buscar"]

            contrato = responder_personalizado(**kwargs)
            integracao = responder_com_linguagem_simples(**kwargs)

            v_contrato = verificar_fontes(contrato["fontes"], c["fontes_esperadas"])
            v_integ = verificar_fontes(integracao["fontes"], c["fontes_esperadas"])
            linhas.append({
                "cenario": c["nome"],
                "perfil": perfil,
                "busca": "real" if c["fn_buscar"] is None else "injetada (vazia)",
                "status_contrato": contrato["status"],
                "status_esperado": c["status_esperado"],
                "status_ok": contrato["status"] == c["status_esperado"],
                "fontes_contrato_ok": v_contrato["ok"],
                "fontes_contrato_detalhe": v_contrato["detalhe"],
                "fontes_integracao_ok": v_integ["ok"],
                "integracao_preserva_fontes": integracao["fontes"] == contrato["fontes"],
                "secoes": [f.get("secao") for f in contrato["fontes"]],
                "fontes_contrato": contrato["fontes"],
                "simplificacao": integracao.get("simplificacao"),
            })
            print(f"{perfil:14} {c['nome']:34} status={contrato['status']:13} "
                  f"fontes_ok={v_contrato['ok']} integ_ok={v_integ['ok']} "
                  f"iguais={linhas[-1]['integracao_preserva_fontes']} secoes={linhas[-1]['secoes']}",
                  flush=True)

    resumo = {
        "execucoes": len(linhas),
        "status_ok": sum(l["status_ok"] for l in linhas),
        "fontes_contrato_ok": sum(l["fontes_contrato_ok"] for l in linhas),
        "fontes_integracao_ok": sum(l["fontes_integracao_ok"] for l in linhas),
        "integracao_preserva_fontes": sum(l["integracao_preserva_fontes"] for l in linhas),
    }
    saida = {
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "natureza": "teste de MECANISMO (LLM substituído por respostas fixas); não mede qualidade",
        "resumo": resumo,
        "execucoes": linhas,
    }
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = DIR / "execucoes" / f"fontes_contrato_{carimbo}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False))
    print(f"[fontes] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
