"""
Camada de Personalização do RAG — Sprint 3 / Genera AI / Dasa
Cientista de IA — Personalização & RAG

Envolve o pipeline da Sprint 2 (busca semântica + agente + LLM real) com uma
camada de personalização por perfil e histórico, sem modificar nenhum arquivo
da Sprint 2.

Fluxo
──────────────────────────────────────────────────────────────────────────────
    pergunta + perfil + usuario_id
        ↓
    [1] guardrails sobre a pergunta CRUA          (sprint2/agente/guardrails.py)
        ↓  bloqueado → retorna sem buscar e sem gastar token
    [2] busca semântica com top_k do perfil        (sprint2/vetorial/buscar.py)
        ↓  sem trechos → retorna "sem_contexto"
    [3] monta pergunta personalizada (perfil + continuidade do histórico)
        ↓
    [4] responder_com_llm()                  (sprint2/interface/llm_connector.py)
        ↓  ← SEMPRE o caminho real (GPT-4.1 Mini), nunca a resposta simulada
    [5] validação de ancoragem no relatório        (ancoragem.py)
        ↓
    [6] registro no histórico                      (historico.py)
        ↓
    contrato de saída estável (versão 1.0)

Decisão de projeto — por que os guardrails rodam na pergunta CRUA
──────────────────────────────────────────────────────────────────────────────
A personalização é injetada anexando uma diretiva de forma à pergunta. Como os
guardrails da Sprint 2 fazem matching por substring, uma diretiva mal redigida
poderia transformar uma pergunta legítima em bloqueada. Por isso o veredito de
segurança é sempre calculado sobre o texto original do usuário, antes de
qualquer personalização. As diretivas ainda são validadas contra as listas de
termos por perfis.validar_diretivas() e por teste automatizado.
"""

import sys
from pathlib import Path

from ancoragem import mensagem_ancoragem_falha, validar_ancoragem
from historico import HistoricoMemoria
from perfis import DIRETIVA_CONTINUIDADE, PERFIL_PADRAO, obter_perfil

VERSAO_CONTRATO = "1.0"

POLITICAS_ANCORAGEM = ("sinalizar", "bloquear")
POLITICA_ANCORAGEM_PADRAO = "sinalizar"


# ─────────────────────────────────────────────────────────────────────────────
# ACESSO AOS MÓDULOS DA SPRINT 2
# ─────────────────────────────────────────────────────────────────────────────

RAIZ = Path(__file__).resolve().parents[2]


def _configurar_path() -> None:
    """
    Insere os diretórios da Sprint 2 no sys.path.

    Necessário porque os módulos da Sprint 2 não formam um pacote Python:
    agente_especialista.py faz `from prompts import ...` sem prefixo, o que só
    resolve com sprint2/agente no path (mesmo contrato usado por app.py).
    """
    caminhos = [
        RAIZ / "sprint2" / "agente",
        RAIZ / "sprint2" / "interface",
        RAIZ,
    ]
    for caminho in caminhos:
        if str(caminho) not in sys.path:
            sys.path.insert(0, str(caminho))


_configurar_path()


def _buscar_padrao(pergunta: str, top_k: int) -> dict:
    """
    Busca semântica real (Integrante 2).

    Import tardio: mantém chromadb e sentence-transformers fora do custo de
    importar este módulo, e permite rodar os testes com busca injetada sem a
    base vetorial construída.
    """
    from sprint2.vetorial.buscar import buscar_contexto

    return buscar_contexto(pergunta=pergunta, top_k=top_k)


def _llm_padrao(pergunta: str, trechos: list, modo: str, api_key: str) -> dict:
    """
    Caminho de resposta REAL (GPT-4.1 Mini via Integrante 4).

    Requisito explícito da Sprint 3: nunca usar gerar_resposta_simulada().
    responder_com_llm() já executa os guardrails do agente internamente e só
    chama a API quando o status permite.
    """
    from llm_connector import responder_com_llm

    return responder_com_llm(
        pergunta=pergunta,
        trechos=trechos,
        modo=modo,
        api_key=api_key,
    )


def _verificar_guardrails(pergunta: str) -> dict:
    """Guardrails médicos da Sprint 2 aplicados ao texto original do usuário."""
    from guardrails import verificar_guardrails

    return verificar_guardrails(pergunta)


# ─────────────────────────────────────────────────────────────────────────────
# MONTAGEM DA PERGUNTA PERSONALIZADA
# ─────────────────────────────────────────────────────────────────────────────

def montar_pergunta_personalizada(
    pergunta: str,
    perfil,
    resumo_historico: dict = None,
) -> str:
    """
    Combina a pergunta original com as diretivas de FORMA.

    O histórico contribui apenas com continuidade (evitar repetir introduções).
    Nenhum fato do histórico é injetado no prompt — o único conteúdo factual
    permitido vem dos trechos recuperados da base vetorial.
    """
    partes = [pergunta.strip(), "", f"[Orientação de estilo] {perfil.diretiva}"]

    if resumo_historico and resumo_historico.get("total_interacoes", 0) > 0:
        partes.append(f"[Continuidade] {DIRETIVA_CONTINUIDADE}")

    return "\n".join(partes)


def _resposta_base(pergunta: str, perfil, resumo_historico: dict) -> dict:
    """Esqueleto do contrato de saída, preenchido por cada caminho de retorno."""
    return {
        "versao_contrato": VERSAO_CONTRATO,
        "pergunta": pergunta,
        "perfil": perfil.id,
        "modo_efetivo": perfil.modo,
        "status": None,
        "categoria": None,
        "resposta": "",
        "fontes": [],
        "ancoragem": {
            "ancorado": None,
            "termos_nao_ancorados": [],
            "score_sobreposicao": 0.0,
            "politica": None,
        },
        "historico_resumo": resumo_historico,
    }


# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÃO PRINCIPAL — CONTRATO PÚBLICO
# ─────────────────────────────────────────────────────────────────────────────

def responder_personalizado(
    pergunta: str,
    perfil: str = PERFIL_PADRAO,
    usuario_id: str = "anonimo",
    api_key: str = None,
    historico=None,
    politica_ancoragem: str = POLITICA_ANCORAGEM_PADRAO,
    fn_buscar=None,
    fn_llm=None,
) -> dict:
    """
    Gera uma resposta personalizada por perfil e histórico, ancorada no relatório.

    Args:
        pergunta:    pergunta do usuário em linguagem natural.
        perfil:      "leigo_ansioso" | "leigo_curioso" | "medico".
        usuario_id:  identificador do usuário para o histórico.
        api_key:     chave OpenAI. Obrigatória apenas quando a pergunta passa
                     pelos guardrails e há contexto — bloqueios não gastam token.
        historico:   implementação de RepositorioHistorico. Default: memória.
                     ▸ Ponto de troca para a persistência real (Integrante 1).
        politica_ancoragem:
                     "sinalizar" (padrão) devolve a resposta marcando
                     ancoragem.ancorado=False; "bloquear" substitui a resposta
                     por uma mensagem segura quando a validação falha.
        fn_buscar:   injeção da busca semântica (testes). Default: real.
        fn_llm:      injeção do caminho de LLM (testes). Default: real.

    Returns:
        dict — contrato estável versão 1.0. Ver README_rag_personalizacao.md.

    Raises:
        ValueError: perfil desconhecido, pergunta vazia ou política inválida.
    """
    if not pergunta or not pergunta.strip():
        raise ValueError("A pergunta não pode estar vazia.")

    if politica_ancoragem not in POLITICAS_ANCORAGEM:
        validas = ", ".join(POLITICAS_ANCORAGEM)
        raise ValueError(
            f"politica_ancoragem inválida: {politica_ancoragem!r}. "
            f"Valores aceitos: {validas}."
        )

    perfil_obj = obter_perfil(perfil)

    if historico is None:
        historico = HistoricoMemoria()
    if fn_buscar is None:
        fn_buscar = _buscar_padrao
    if fn_llm is None:
        fn_llm = _llm_padrao

    resumo_historico = historico.resumir(usuario_id)
    resultado = _resposta_base(pergunta, perfil_obj, resumo_historico)

    # ── [1] Guardrails sobre a pergunta CRUA ─────────────────────────────────
    veredito = _verificar_guardrails(pergunta)

    if not veredito["permitido"]:
        historico.registrar(
            usuario_id=usuario_id,
            pergunta=pergunta,
            perfil=perfil_obj.id,
            secoes_citadas=[],
        )
        resultado.update({
            "status": "bloqueado",
            "categoria": veredito["categoria"],
            "resposta": veredito["mensagem"],
            "historico_resumo": historico.resumir(usuario_id),
        })
        resultado["ancoragem"]["politica"] = politica_ancoragem
        return resultado

    # ── [2] Busca semântica com a profundidade do perfil ─────────────────────
    busca = fn_buscar(pergunta, perfil_obj.top_k)
    trechos_ricos = busca.get("trechos", [])
    trechos_texto = [t["conteudo"] for t in trechos_ricos]
    secoes = [t.get("secao", "") for t in trechos_ricos]

    if not trechos_texto:
        historico.registrar(
            usuario_id=usuario_id,
            pergunta=pergunta,
            perfil=perfil_obj.id,
            secoes_citadas=[],
        )
        resultado.update({
            "status": "sem_contexto",
            "categoria": "sem_contexto",
            "resposta": (
                "Não encontrei informações suficientes no relatório enviado "
                "para responder com segurança."
            ),
            "historico_resumo": historico.resumir(usuario_id),
        })
        resultado["ancoragem"]["politica"] = politica_ancoragem
        return resultado

    # ── [3] Pergunta personalizada ───────────────────────────────────────────
    pergunta_final = montar_pergunta_personalizada(
        pergunta=pergunta,
        perfil=perfil_obj,
        resumo_historico=resumo_historico,
    )

    # ── [4] Resposta real via LLM ────────────────────────────────────────────
    saida_llm = fn_llm(pergunta_final, trechos_texto, perfil_obj.modo, api_key)

    status_llm = saida_llm.get("status", "respondido")
    resposta_llm = saida_llm.get("resposta", "")

    resultado["fontes"] = trechos_ricos
    resultado["categoria"] = saida_llm.get("categoria")

    # O agente pode bloquear internamente mesmo após o pré-check (defesa dupla).
    if status_llm != "respondido":
        historico.registrar(
            usuario_id=usuario_id,
            pergunta=pergunta,
            perfil=perfil_obj.id,
            secoes_citadas=secoes,
        )
        resultado.update({
            "status": status_llm,
            "resposta": resposta_llm,
            "fontes": [],
            "historico_resumo": historico.resumir(usuario_id),
        })
        resultado["ancoragem"]["politica"] = politica_ancoragem
        return resultado

    # ── [5] Validação de ancoragem ───────────────────────────────────────────
    checagem = validar_ancoragem(resposta_llm, trechos_texto)
    resultado["ancoragem"] = {
        "ancorado": checagem["ancorado"],
        "termos_nao_ancorados": checagem["termos_nao_ancorados"],
        "score_sobreposicao": checagem["score_sobreposicao"],
        "politica": politica_ancoragem,
    }

    if not checagem["ancorado"] and politica_ancoragem == "bloquear":
        resposta_final = mensagem_ancoragem_falha()
        status_final = "nao_ancorado"
        categoria_final = "ancoragem_falhou"
    else:
        resposta_final = resposta_llm
        status_final = "respondido"
        categoria_final = saida_llm.get("categoria", "resposta_rag")

    # ── [6] Histórico ────────────────────────────────────────────────────────
    historico.registrar(
        usuario_id=usuario_id,
        pergunta=pergunta,
        perfil=perfil_obj.id,
        secoes_citadas=secoes,
    )

    resultado.update({
        "status": status_final,
        "categoria": categoria_final,
        "resposta": resposta_final,
        "historico_resumo": historico.resumir(usuario_id),
    })
    return resultado
