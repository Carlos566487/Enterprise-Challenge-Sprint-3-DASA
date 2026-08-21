"""
Adaptador RAG Personalizado + NLP — Sprint 3 / Genera AI / Dasa
Cientista de IA — Personalização & RAG

Compõe duas camadas que hoje vivem separadas no repositório:

    sprint3/rag_personalizacao/  →  responder_personalizado()
        resposta REAL do GPT-4.1 Mini, personalizada por perfil,
        validada contra o relatório (ancoragem)

    sprint3/nlp/nlp_simplificacao.py  →  simplificar_texto()
        função PURA (texto técnico → texto simples + métricas)

Por que este módulo mora fora dos dois pacotes
──────────────────────────────────────────────────────────────────────────────
O contrato de sprint3/rag_personalizacao/ tem independência de sprint3/nlp/
como garantia explícita, travada por teste. Colocar este adaptador lá dentro
criaria exatamente a dependência que aquele pacote promete não ter.

Aqui a dependência aponta em uma direção só:

    sprint3/integracao/  --depende-->  sprint3/rag_personalizacao/
                         --depende-->  sprint3/nlp/ (só a função pura)

Nenhum dos dois depende deste módulo. Apagar este diretório não afeta nenhum
dos outros dois.

IMPORTANTE: nada em sprint3/nlp/ é modificado. Apenas importamos a função
pura, exatamente como sprint3/interface/app.py já faz.

Três regras de segurança
──────────────────────────────────────────────────────────────────────────────
1. NUNCA simplifica mensagem de guardrail.
   Só simplifica quando status == "respondido". As mensagens de recusa são
   texto aprovado por governança — parafrasear seria adulterar.

2. NUNCA simplifica para o perfil médico.
   Trocar "genótipo" por "informações do DNA" destrói a precisão que o
   profissional precisa.

3. REVALIDA a ancoragem depois de simplificar.
   A simplificação reescreve termos DEPOIS da validação original — ou seja,
   o texto exibido não é o texto que foi validado. Se a reescrita quebrar a
   ancoragem (perder ou inventar número, SNP ou gene), o adaptador devolve o
   texto original e sinaliza o motivo.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

for _caminho in (RAIZ, RAIZ / "sprint3" / "nlp"):
    if str(_caminho) not in sys.path:
        sys.path.insert(0, str(_caminho))

from sprint3.rag_personalizacao import (                     # noqa: E402
    responder_personalizado,
    validar_ancoragem,
)

VERSAO_CONTRATO_INTEGRACAO = "1.0"

# Motivos possíveis para a simplificação não ter sido aplicada.
MOTIVO_OK = "ok"
MOTIVO_PERFIL_TECNICO = "perfil_tecnico"
MOTIVO_STATUS = "status_nao_respondido"
MOTIVO_ANCORAGEM = "quebrou_ancoragem"
MOTIVO_INDISPONIVEL = "nlp_indisponivel"
MOTIVO_VAZIO = "texto_vazio"


def _carregar_simplificador():
    """
    Importa a função pura da Tayná sob demanda.

    Import tardio e tolerante: se sprint3/nlp/ não estiver disponível, o
    adaptador continua funcionando e devolve a resposta sem simplificar,
    sinalizando o motivo — nunca derruba a resposta ao usuário.
    """
    try:
        from nlp_simplificacao import simplificar_texto
        return simplificar_texto
    except ImportError:
        return None


def _sem_simplificacao(motivo: str) -> dict:
    return {
        "aplicada": False,
        "motivo": motivo,
        "metricas_original": {},
        "metricas_simplificado": {},
    }


def responder_com_linguagem_simples(
    pergunta: str,
    perfil: str = "leigo_ansioso",
    usuario_id: str = "anonimo",
    api_key: str = None,
    historico=None,
    politica_ancoragem: str = "sinalizar",
    fn_buscar=None,
    fn_llm=None,
    fn_simplificar=None,
) -> dict:
    """
    Resposta personalizada, fundamentada no relatório e em linguagem simples.

    Args:
        pergunta:    pergunta do usuário em linguagem natural.
        perfil:      "leigo_ansioso" | "leigo_curioso" | "medico".
        usuario_id:  identificador para o histórico.
        api_key:     chave OpenAI (não exigida em perguntas bloqueadas).
        historico:   implementação de RepositorioHistorico. Default: memória.
        politica_ancoragem: "sinalizar" (padrão) | "bloquear".
        fn_buscar:   injeção da busca semântica (testes).
        fn_llm:      injeção do caminho de LLM (testes).
        fn_simplificar: injeção do simplificador (testes). Default: a função
                     pura de sprint3/nlp/nlp_simplificacao.py.

    Returns:
        dict — todas as chaves do contrato v1.0 de responder_personalizado(),
        preservadas sem alteração, mais:

            "versao_contrato_integracao": "1.0"
            "resposta_simplificada": str
                Texto pronto para exibição. Igual a "resposta" quando a
                simplificação não foi aplicada — o consumidor pode sempre
                renderizar este campo sem verificar nada antes.
            "simplificacao": {
                "aplicada": bool,
                "motivo": str,
                "metricas_original": dict,
                "metricas_simplificado": dict,
            }

    Raises:
        ValueError: propagado de responder_personalizado() para perfil
        desconhecido, pergunta vazia ou política inválida.
    """
    resultado = responder_personalizado(
        pergunta=pergunta,
        perfil=perfil,
        usuario_id=usuario_id,
        api_key=api_key,
        historico=historico,
        politica_ancoragem=politica_ancoragem,
        fn_buscar=fn_buscar,
        fn_llm=fn_llm,
    )

    resultado["versao_contrato_integracao"] = VERSAO_CONTRATO_INTEGRACAO

    resposta = resultado.get("resposta", "")

    # Default seguro: exibir o texto original.
    resultado["resposta_simplificada"] = resposta

    # ── Regra 1: nunca simplificar mensagem de guardrail ─────────────────────
    if resultado.get("status") != "respondido":
        resultado["simplificacao"] = _sem_simplificacao(MOTIVO_STATUS)
        return resultado

    # ── Regra 2: nunca simplificar para o perfil médico ──────────────────────
    if resultado.get("modo_efetivo") == "tecnico":
        resultado["simplificacao"] = _sem_simplificacao(MOTIVO_PERFIL_TECNICO)
        return resultado

    if not resposta or not resposta.strip():
        resultado["simplificacao"] = _sem_simplificacao(MOTIVO_VAZIO)
        return resultado

    simplificar = fn_simplificar or _carregar_simplificador()
    if simplificar is None:
        resultado["simplificacao"] = _sem_simplificacao(MOTIVO_INDISPONIVEL)
        return resultado

    saida_nlp = simplificar(resposta)
    texto_simplificado = saida_nlp.get("texto_simplificado", "") or ""

    if not texto_simplificado.strip():
        resultado["simplificacao"] = _sem_simplificacao(MOTIVO_VAZIO)
        return resultado

    # ── Regra 3: revalidar ancoragem sobre o texto JÁ simplificado ───────────
    trechos = [f.get("conteudo", "") for f in resultado.get("fontes", [])]
    checagem = validar_ancoragem(texto_simplificado, trechos)

    if not checagem["ancorado"]:
        # A reescrita introduziu ou corrompeu um fato: mantém o original.
        resultado["simplificacao"] = {
            "aplicada": False,
            "motivo": MOTIVO_ANCORAGEM,
            "metricas_original": saida_nlp.get("metricas_original", {}),
            "metricas_simplificado": saida_nlp.get("metricas_simplificado", {}),
            "termos_nao_ancorados": checagem["termos_nao_ancorados"],
        }
        return resultado

    resultado["resposta_simplificada"] = texto_simplificado
    resultado["simplificacao"] = {
        "aplicada": True,
        "motivo": MOTIVO_OK,
        "metricas_original": saida_nlp.get("metricas_original", {}),
        "metricas_simplificado": saida_nlp.get("metricas_simplificado", {}),
    }
    return resultado
