"""
Integração do Agente com NLP
DASA / Genera - Sprint 3

Responsável por integrar:

1. agente especialista e RAG da Sprint 2;
2. simplificação de linguagem da Sprint 3;
3. métricas de legibilidade;
4. histórico de interações;
5. atualização automática do resumo das conversas.

A Sprint 2 permanece preservada.
Esta camada apenas utiliza sua saída e aplica os recursos
de NLP desenvolvidos na Sprint 3.
"""

import sys
from pathlib import Path


# ============================================================
# CONFIGURAÇÃO DOS CAMINHOS
# ============================================================

ARQUIVO_ATUAL = Path(__file__).resolve()

RAIZ_PROJETO = ARQUIVO_ATUAL.parents[3]

PASTA_AGENTE_SPRINT2 = (
    RAIZ_PROJETO
    / "sprint2"
    / "agente"
)

PASTA_NLP_SPRINT3 = (
    RAIZ_PROJETO
    / "sprint3"
    / "nlp"
)


if str(PASTA_AGENTE_SPRINT2) not in sys.path:
    sys.path.insert(
        0,
        str(PASTA_AGENTE_SPRINT2)
    )

if str(PASTA_NLP_SPRINT3) not in sys.path:
    sys.path.insert(
        0,
        str(PASTA_NLP_SPRINT3)
    )


# ============================================================
# IMPORTAÇÕES
# ============================================================

import agente_especialista as agente_sprint2

from nlp_simplificacao import simplificar_texto

from resumos_automaticos import (
    gerar_resumo_interacoes,
    formatar_resumo_interacoes,
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def criar_interacao(pergunta, resposta):
    """
    Cria uma interação no formato utilizado
    pelo módulo de resumos automáticos.
    """

    return {
        "pergunta": pergunta,
        "resposta": resposta
    }


def preparar_resposta_nlp(
    resposta_original,
    modo="paciente"
):
    """
    Aplica a camada de NLP sobre a resposta do agente.

    No modo paciente:
    - simplifica termos técnicos;
    - calcula métricas antes e depois.

    No modo técnico:
    - preserva o texto original;
    - mantém métricas para rastreabilidade.
    """

    resultado_nlp = simplificar_texto(
        resposta_original
    )

    if modo == "paciente":
        resposta_final = resultado_nlp[
            "texto_simplificado"
        ]

        metricas_final = resultado_nlp[
            "metricas_simplificado"
        ]

    else:
        resposta_final = resultado_nlp[
            "texto_original"
        ]

        metricas_final = resultado_nlp[
            "metricas_original"
        ]

    return {
        "resposta_original":
            resultado_nlp[
                "texto_original"
            ],

        "resposta_final":
            resposta_final,

        "metricas_original":
            resultado_nlp[
                "metricas_original"
            ],

        "metricas_final":
            metricas_final
    }


# ============================================================
# FLUXO PRINCIPAL
# ============================================================

def responder_com_nlp(
    pergunta,
    trechos_recuperados,
    historico=None,
    modo="paciente"
):
    """
    Executa o fluxo completo de integração.

    Etapas:
    1. pergunta enviada ao agente da Sprint 2;
    2. validação e resposta baseada no RAG;
    3. aplicação da simplificação NLP;
    4. cálculo das métricas de legibilidade;
    5. atualização do histórico;
    6. atualização automática do resumo.
    """

    if historico is None:
        historico = []

    historico_atualizado = list(
        historico
    )

    # --------------------------------------------------------
    # AGENTE / RAG DA SPRINT 2
    # --------------------------------------------------------

    resultado_agente = agente_sprint2.responder(
        pergunta=pergunta,
        trechos_recuperados=trechos_recuperados,
        modo=modo
    )

    status = resultado_agente.get(
        "status"
    )

    categoria = resultado_agente.get(
        "categoria"
    )

    resposta_agente = resultado_agente.get(
        "resposta",
        ""
    )

    fontes = resultado_agente.get(
        "fontes",
        []
    )

    # --------------------------------------------------------
    # CASOS BLOQUEADOS OU SEM CONTEXTO
    # --------------------------------------------------------

    if status != "respondido":

        resumo_historico = gerar_resumo_interacoes(
            historico_atualizado
        )

        return {
            "status":
                status,

            "categoria":
                categoria,

            "modo":
                modo,

            "resposta_original":
                resposta_agente,

            "resposta_final":
                resposta_agente,

            "fontes":
                fontes,

            "metricas_original":
                {},

            "metricas_final":
                {},

            "historico":
                historico_atualizado,

            "resumo_interacoes":
                resumo_historico
        }

    # --------------------------------------------------------
    # NLP
    # --------------------------------------------------------

    resultado_nlp = preparar_resposta_nlp(
        resposta_original=resposta_agente,
        modo=modo
    )

    resposta_final = resultado_nlp[
        "resposta_final"
    ]

    # --------------------------------------------------------
    # HISTÓRICO
    # --------------------------------------------------------

    nova_interacao = criar_interacao(
        pergunta=pergunta,
        resposta=resposta_final
    )

    historico_atualizado.append(
        nova_interacao
    )

    # --------------------------------------------------------
    # RESUMO AUTOMÁTICO
    # --------------------------------------------------------

    resumo_historico = gerar_resumo_interacoes(
        historico_atualizado
    )

    # --------------------------------------------------------
    # SAÍDA ESTRUTURADA
    # --------------------------------------------------------

    return {
        "status":
            status,

        "categoria":
            categoria,

        "modo":
            modo,

        "resposta_original":
            resultado_nlp[
                "resposta_original"
            ],

        "resposta_final":
            resposta_final,

        "fontes":
            fontes,

        "metricas_original":
            resultado_nlp[
                "metricas_original"
            ],

        "metricas_final":
            resultado_nlp[
                "metricas_final"
            ],

        "historico":
            historico_atualizado,

        "resumo_interacoes":
            resumo_historico
    }


# ============================================================
# FORMATAÇÃO DA DEMONSTRAÇÃO
# ============================================================

def exibir_resultado(
    numero_teste,
    pergunta,
    resultado
):
    """
    Exibe o resultado da integração de forma clara.
    """

    print(
        "\n" + "=" * 70
    )

    print(
        f"TESTE {numero_teste} - AGENTE + NLP"
    )

    print(
        "=" * 70
    )

    print(
        f"\nPERGUNTA DO USUÁRIO:\n{pergunta}"
    )

    print(
        f"\nSTATUS: {resultado['status']}"
    )

    print(
        f"MODO: {resultado.get('modo', 'paciente')}"
    )

    print(
        "\nRESPOSTA TÉCNICA ORIGINAL:"
    )

    print(
        resultado[
            "resposta_original"
        ]
    )

    print(
        "\nRESPOSTA SIMPLIFICADA PARA O USUÁRIO:"
    )

    print(
        resultado[
            "resposta_final"
        ]
    )

    if resultado["metricas_original"]:

        print(
            "\nMÉTRICAS - TEXTO ORIGINAL:"
        )

        print(
            resultado[
                "metricas_original"
            ]
        )

        print(
            "\nMÉTRICAS - TEXTO SIMPLIFICADO:"
        )

        print(
            resultado[
                "metricas_final"
            ]
        )

    print(
        "\n" + "-" * 70
    )

    print(
        "RESUMO ATUALIZADO DAS INTERAÇÕES"
    )

    print(
        "-" * 70
    )

    print(
        formatar_resumo_interacoes(
            resultado[
                "resumo_interacoes"
            ]
        )
    )


# ============================================================
# RESPOSTA TÉCNICA CONTROLADA PARA TESTE
# ============================================================

def gerar_resposta_tecnica_teste(
    prompt_final
):
    """
    Simula uma resposta técnica do modelo exclusivamente
    para demonstrar a atuação da camada NLP.

    Esta função é utilizada apenas nos testes abaixo.
    O arquivo original da Sprint 2 não é alterado.
    """

    return """
O relatório identificou uma variante genética associada a uma
predisposição genética para determinada condição.

Também foram avaliados marcadores genéticos presentes no DNA.

Esse resultado indica risco aumentado, mas não significa que
a pessoa necessariamente desenvolverá a condição.

O genótipo deve ser interpretado em conjunto com outros fatores,
como histórico familiar, hábitos de vida e acompanhamento profissional.

O resultado apresenta uma associação genética e não representa
um diagnóstico definitivo.
"""


# ============================================================
# TESTE COMPLETO DE INTEGRAÇÃO
# ============================================================

if __name__ == "__main__":

    # Guarda a função original da Sprint 2.
    resposta_simulada_original = (
        agente_sprint2.gerar_resposta_simulada
    )

    try:

        # Substitui SOMENTE durante este teste.
        agente_sprint2.gerar_resposta_simulada = (
            gerar_resposta_tecnica_teste
        )

        historico_teste = []

        # ====================================================
        # TESTE 1
        # ====================================================

        pergunta_1 = (
            "Meu resultado indica que eu tenho "
            "uma chance maior de desenvolver alguma condição?"
        )

        trechos_1 = [
            (
                "Foi identificada uma variante genética "
                "associada a predisposição genética."
            ),
            (
                "A presença dessa variante representa "
                "uma associação estatística e não um diagnóstico."
            )
        ]

        resultado_1 = responder_com_nlp(
            pergunta=pergunta_1,
            trechos_recuperados=trechos_1,
            historico=historico_teste,
            modo="paciente"
        )

        exibir_resultado(
            numero_teste=1,
            pergunta=pergunta_1,
            resultado=resultado_1
        )

        historico_teste = resultado_1[
            "historico"
        ]

        # ====================================================
        # TESTE 2
        # ====================================================

        pergunta_2 = (
            "Pode explicar esse resultado "
            "de um jeito mais simples?"
        )

        trechos_2 = [
            (
                "Marcadores genéticos são analisados "
                "para identificar possíveis associações "
                "com determinadas características."
            ),
            (
                "Predisposição genética não representa "
                "certeza de desenvolvimento de uma condição."
            )
        ]

        resultado_2 = responder_com_nlp(
            pergunta=pergunta_2,
            trechos_recuperados=trechos_2,
            historico=historico_teste,
            modo="paciente"
        )

        exibir_resultado(
            numero_teste=2,
            pergunta=pergunta_2,
            resultado=resultado_2
        )

        historico_teste = resultado_2[
            "historico"
        ]

        # ====================================================
        # VALIDAÇÃO FINAL
        # ====================================================

        print(
            "\n" + "=" * 70
        )

        print(
            "VALIDAÇÃO FINAL DA INTEGRAÇÃO"
        )

        print(
            "=" * 70
        )

        print(
            f"\nTotal de interações armazenadas: "
            f"{len(historico_teste)}"
        )

        print(
            "\nResumo final do histórico:"
        )

        print(
            formatar_resumo_interacoes(
                gerar_resumo_interacoes(
                    historico_teste
                )
            )
        )

    finally:

        # Restaura a função original da Sprint 2.
        agente_sprint2.gerar_resposta_simulada = (
            resposta_simulada_original
        )