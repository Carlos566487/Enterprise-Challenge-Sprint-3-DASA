"""
Módulo de NLP — Resumos Automáticos
DASA / Genera — Sprint 3

Responsável por:

1. gerar resumo estruturado do relatório genético;
2. analisar o histórico de interações entre usuário e agente;
3. identificar automaticamente os principais temas discutidos;
4. gerar uma síntese acessível das interações;
5. atualizar o resumo quando novas interações forem adicionadas.

O módulo utiliza regras determinísticas e rastreáveis para reduzir
o risco de criar interpretações que não estejam presentes nos dados
originais ou nas interações do usuário.
"""

import json
import re
from pathlib import Path


# ============================================================
# VOCABULÁRIO CONTROLADO DE TEMAS
# ============================================================

TEMAS_INTERACAO = {

    "diabetes": {
        "palavras": [
            "diabetes",
            "glicose",
            "glicemia",
            "insulina",
            "diabetes mellitus"
        ],
        "descricao":
            "risco genético relacionado ao diabetes"
    },

    "cancer": {
        "palavras": [
            "câncer",
            "cancer",
            "carcinoma",
            "brca",
            "brca1",
            "brca2",
            "tumor",
            "oncologia",
            "oncológico",
            "oncologico"
        ],
        "descricao":
            "predisposição genética relacionada ao câncer"
    },

    "cardiovascular": {
        "palavras": [
            "hipertensão",
            "hipertensao",
            "pressão arterial",
            "pressao arterial",
            "cardiovascular",
            "coração",
            "coracao",
            "cardíaco",
            "cardiaco"
        ],
        "descricao":
            "risco e características cardiovasculares"
    },

    "ancestralidade": {
        "palavras": [
            "ancestralidade",
            "ancestral",
            "origem genética",
            "origem genetica",
            "origem",
            "população",
            "populacao",
            "etnia",
            "europeia",
            "africana",
            "asiática",
            "asiatica"
        ],
        "descricao":
            "ancestralidade genética"
    },

    "interpretacao_risco": {
        "palavras": [
            "risco alto",
            "risco médio",
            "risco medio",
            "risco baixo",
            "risco aumentado",
            "risco reduzido",
            "chance maior",
            "chance menor",
            "predisposição",
            "predisposicao",
            "predisposição genética",
            "predisposicao genetica",
            "percentil",
            "o que significa",
            "significa risco",
            "probabilidade",
            "chance de desenvolver"
        ],
        "descricao":
            "interpretação dos níveis de risco genético"
    },

    "alteracoes_dna": {
        "palavras": [
            "variante genética",
            "variante genetica",
            "alteração no dna",
            "alteracao no dna",
            "alteração genética",
            "alteracao genetica",
            "polimorfismo",
            "alelo"
        ],
        "descricao":
            "alterações e características encontradas no DNA"
    },

    "informacoes_dna": {
        "palavras": [
            "marcadores genéticos",
            "marcadores geneticos",
            "características do dna",
            "caracteristicas do dna",
            "informações do dna",
            "informacoes do dna",
            "genótipo",
            "genotipo"
        ],
        "descricao":
            "informações analisadas no DNA"
    },

    "acompanhamento": {
        "palavras": [
            "preciso procurar um médico",
            "preciso procurar médico",
            "devo procurar um médico",
            "devo procurar médico",
            "preciso de médico",
            "consulta médica",
            "consulta medica",
            "acompanhamento médico",
            "acompanhamento medico",
            "qual médico",
            "qual medico",
            "especialista",
            "endocrinologista",
            "cardiologista",
            "geneticista",
            "oncologista"
        ],
        "descricao":
            "necessidade de acompanhamento profissional"
    },

    "diagnostico": {
        "palavras": [
            "diagnóstico",
            "diagnostico",
            "tenho a doença",
            "tenho essa doença",
            "significa que tenho",
            "certeza de desenvolver",
            "vou desenvolver",
            "vou ter essa condição",
            "vou ter essa condicao"
        ],
        "descricao":
            "diferença entre predisposição genética e diagnóstico"
    },

    "metabolismo": {
        "palavras": [
            "metabolismo",
            "metabólico",
            "metabolico",
            "metabólica",
            "metabolica"
        ],
        "descricao":
            "características genéticas relacionadas ao metabolismo"
    }
}


# ============================================================
# TEMAS QUE PODEM SER COMPLEMENTADOS PELA RESPOSTA
# ============================================================

TEMAS_COMPLEMENTARES_RESPOSTA = {
    "diabetes",
    "cancer",
    "cardiovascular",
    "ancestralidade",
    "alteracoes_dna",
    "informacoes_dna",
    "metabolismo"
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def carregar_dados(caminho_arquivo):
    """
    Carrega dados estruturados a partir de um arquivo JSON.
    """

    caminho = Path(caminho_arquivo)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    with open(
        caminho,
        "r",
        encoding="utf-8"
    ) as arquivo:

        return json.load(
            arquivo
        )


def limpar_texto(texto):
    """
    Normaliza espaços e quebras de linha.
    """

    if texto is None:
        return ""

    texto = str(
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def normalizar_texto(texto):
    """
    Retorna versão normalizada para análise temática.
    """

    return limpar_texto(
        texto
    ).lower()


def garantir_lista(valor):
    """
    Garante que um campo possa ser tratado como lista.
    """

    if valor is None:
        return []

    if isinstance(
        valor,
        list
    ):
        return valor

    return [
        valor
    ]


def formatar_item(item):
    """
    Converte diferentes estruturas de dados em texto legível.
    """

    if isinstance(
        item,
        dict
    ):

        partes = []

        for chave, valor in item.items():

            if valor not in (
                None,
                "",
                [],
                {}
            ):

                chave_formatada = (
                    chave
                    .replace("_", " ")
                    .capitalize()
                )

                partes.append(
                    f"{chave_formatada}: {valor}"
                )

        return " | ".join(
            partes
        )

    return limpar_texto(
        item
    )


def pluralizar(
    quantidade,
    singular,
    plural=None
):
    """
    Escolhe singular ou plural de acordo com a quantidade.
    """

    if plural is None:
        plural = (
            singular + "s"
        )

    if quantidade == 1:
        return singular

    return plural


# ============================================================
# RESUMO AUTOMÁTICO DO RELATÓRIO
# ============================================================

def gerar_resumo_relatorio(dados):
    """
    Gera resumo estruturado do relatório genético.

    Somente dados efetivamente presentes no JSON são utilizados.
    """

    paciente = dados.get(
        "paciente",
        {}
    )

    sumario = dados.get(
        "sumario",
        {}
    )

    total = sumario.get(
        "total_condicoes_analisadas",
        0
    )

    alto_risco = sumario.get(
        "condicoes_alto_risco",
        0
    )

    medio_risco = sumario.get(
        "condicoes_medio_risco",
        0
    )

    baixo_risco = sumario.get(
        "condicoes_baixo_risco",
        0
    )

    riscos = garantir_lista(
        sumario.get(
            "principais_riscos_medico"
        )
    )

    recomendacoes = garantir_lista(
        sumario.get(
            "recomendacoes_prioritarias"
        )
    )

    riscos_formatados = []

    for risco in riscos:

        risco_formatado = formatar_item(
            risco
        )

        if risco_formatado:

            riscos_formatados.append(
                risco_formatado
            )

    recomendacoes_formatadas = []

    for recomendacao in recomendacoes:

        recomendacao_formatada = formatar_item(
            recomendacao
        )

        if recomendacao_formatada:

            recomendacoes_formatadas.append(
                recomendacao_formatada
            )

    palavra_condicao = pluralizar(
        total,
        "condição",
        "condições"
    )

    resumo_textual = (
        f"O relatório analisou {total} "
        f"{palavra_condicao} genéticas: "
        f"{alto_risco} foram classificadas como alto risco, "
        f"{medio_risco} como médio risco e "
        f"{baixo_risco} como baixo risco."
    )

    return {

        "id_relatorio":
            paciente.get(
                "id_relatorio"
            ),

        "total_condicoes":
            total,

        "distribuicao_risco": {
            "alto":
                alto_risco,

            "medio":
                medio_risco,

            "baixo":
                baixo_risco
        },

        "principais_riscos":
            riscos_formatados,

        "recomendacoes":
            recomendacoes_formatadas,

        "resumo_textual":
            resumo_textual
    }


def formatar_resumo_relatorio(resumo):
    """
    Formata o resumo estruturado do relatório para apresentação.
    """

    linhas = [
        "RESUMO AUTOMÁTICO DO RELATÓRIO",
        "",
        resumo[
            "resumo_textual"
        ]
    ]

    if resumo[
        "principais_riscos"
    ]:

        linhas.extend([
            "",
            "PRINCIPAIS RESULTADOS IDENTIFICADOS:"
        ])

        for risco in resumo[
            "principais_riscos"
        ]:

            linhas.append(
                f"- {risco}"
            )

    if resumo[
        "recomendacoes"
    ]:

        linhas.extend([
            "",
            "RECOMENDAÇÕES PRESENTES NO RELATÓRIO:"
        ])

        for recomendacao in resumo[
            "recomendacoes"
        ]:

            linhas.append(
                f"- {recomendacao}"
            )

    return "\n".join(
        linhas
    )


# ============================================================
# IDENTIFICAÇÃO DE TEMAS
# ============================================================

def identificar_temas(texto):
    """
    Identifica os temas presentes em determinado texto.

    Cada tema é incluído apenas uma vez.
    """

    texto_normalizado = normalizar_texto(
        texto
    )

    temas_encontrados = []

    for nome_tema, configuracao in (
        TEMAS_INTERACAO.items()
    ):

        for palavra in configuracao[
            "palavras"
        ]:

            if (
                palavra.lower()
                in texto_normalizado
            ):

                temas_encontrados.append(
                    nome_tema
                )

                break

    return temas_encontrados


def identificar_temas_interacao(
    pergunta,
    resposta
):
    """
    Identifica os temas de uma interação.

    Estratégia:

    1. A pergunta do usuário é a principal fonte para
       compreender sua intenção.

    2. A resposta do agente pode complementar a análise
       com temas objetivos, como uma condição ou
       ancestralidade.

    3. Temas genéricos, como acompanhamento e diagnóstico,
       não são inferidos apenas porque aparecem em uma
       resposta padrão do agente.

    Isso evita classificar uma conversa como
    "acompanhamento profissional" apenas porque o agente
    incluiu um disclaimer ou orientação genérica.
    """

    temas_pergunta = identificar_temas(
        pergunta
    )

    temas_resposta = identificar_temas(
        resposta
    )

    temas_finais = list(
        temas_pergunta
    )

    for tema in temas_resposta:

        if (
            tema
            in TEMAS_COMPLEMENTARES_RESPOSTA
            and tema not in temas_finais
        ):

            temas_finais.append(
                tema
            )

    return temas_finais


# ============================================================
# ANÁLISE DO HISTÓRICO
# ============================================================

def analisar_interacoes(interacoes):
    """
    Analisa perguntas e respostas do histórico.

    Retorna:
    - interações válidas;
    - frequência dos temas;
    - ordem dos temas.
    """

    interacoes_validas = []

    ordem_temas = []

    frequencia_temas = {}

    for interacao in interacoes:

        pergunta = limpar_texto(
            interacao.get(
                "pergunta",
                ""
            )
        )

        resposta = limpar_texto(
            interacao.get(
                "resposta",
                ""
            )
        )

        if (
            not pergunta
            and not resposta
        ):
            continue

        temas = identificar_temas_interacao(
            pergunta,
            resposta
        )

        for tema in temas:

            frequencia_temas[
                tema
            ] = (
                frequencia_temas.get(
                    tema,
                    0
                )
                + 1
            )

            if (
                tema
                not in ordem_temas
            ):

                ordem_temas.append(
                    tema
                )

        interacoes_validas.append({

            "pergunta":
                pergunta,

            "resposta":
                resposta,

            "temas":
                temas
        })

    temas_ordenados = sorted(
        ordem_temas,

        key=lambda tema: (

            -frequencia_temas.get(
                tema,
                0
            ),

            ordem_temas.index(
                tema
            )
        )
    )

    return {

        "interacoes":
            interacoes_validas,

        "frequencia_temas":
            frequencia_temas,

        "temas_ordenados":
            temas_ordenados
    }


# ============================================================
# SÍNTESE DOS TEMAS
# ============================================================

def gerar_sintese_temas(temas):
    """
    Converte os temas identificados em uma frase
    natural e acessível.
    """

    descricoes = [

        TEMAS_INTERACAO[
            tema
        ][
            "descricao"
        ]

        for tema in temas

        if tema
        in TEMAS_INTERACAO
    ]

    if not descricoes:

        return (
            "As interações abordaram dúvidas "
            "relacionadas ao conteúdo do relatório genético."
        )

    if len(
        descricoes
    ) == 1:

        return (
            "O principal tema abordado foi "
            f"{descricoes[0]}."
        )

    if len(
        descricoes
    ) == 2:

        return (
            "Os principais temas abordados foram "
            f"{descricoes[0]} e "
            f"{descricoes[1]}."
        )

    inicio = ", ".join(
        descricoes[:-1]
    )

    return (
        "Os principais temas abordados foram "
        f"{inicio} e "
        f"{descricoes[-1]}."
    )


# ============================================================
# RESUMO DAS INTERAÇÕES
# ============================================================

def gerar_resumo_interacoes(interacoes):
    """
    Gera resumo semântico do histórico de interações.

    A saída estruturada pode ser consumida pelo
    front-end ou dashboard.
    """

    if not interacoes:

        return {

            "total_interacoes":
                0,

            "temas":
                [],

            "frequencia_temas":
                {},

            "ultima_duvida":
                None,

            "resumo_textual":
                (
                    "Ainda não existem "
                    "interações para resumir."
                )
        }

    analise = analisar_interacoes(
        interacoes
    )

    interacoes_validas = analise[
        "interacoes"
    ]

    temas = analise[
        "temas_ordenados"
    ]

    if not interacoes_validas:

        return {

            "total_interacoes":
                0,

            "temas":
                [],

            "frequencia_temas":
                {},

            "ultima_duvida":
                None,

            "resumo_textual":
                (
                    "Não foram encontradas "
                    "interações válidas."
                )
        }

    total = len(
        interacoes_validas
    )

    ultima_duvida = (
        interacoes_validas[
            -1
        ][
            "pergunta"
        ]
    )

    sintese_temas = gerar_sintese_temas(
        temas
    )

    palavra_interacao = pluralizar(
        total,
        "interação",
        "interações"
    )

    palavra_valida = pluralizar(
        total,
        "válida",
        "válidas"
    )

    resumo_textual = (
        f"O histórico possui {total} "
        f"{palavra_interacao} "
        f"{palavra_valida}. "
        f"{sintese_temas}"
    )

    if ultima_duvida:

        resumo_textual += (
            " A dúvida mais recente do usuário foi: "
            f"\"{ultima_duvida}\""
        )

    descricoes_temas = [

        TEMAS_INTERACAO[
            tema
        ][
            "descricao"
        ]

        for tema in temas

        if tema
        in TEMAS_INTERACAO
    ]

    return {

        "total_interacoes":
            total,

        "temas":
            descricoes_temas,

        "frequencia_temas":
            analise[
                "frequencia_temas"
            ],

        "ultima_duvida":
            ultima_duvida,

        "resumo_textual":
            resumo_textual
    }


# ============================================================
# ATUALIZAÇÃO DO RESUMO
# ============================================================

def atualizar_resumo_interacoes(
    interacoes,
    nova_interacao
):
    """
    Atualiza o resumo após receber uma nova interação.

    A lista original não é modificada.
    """

    historico_atualizado = list(
        interacoes
    )

    historico_atualizado.append(
        nova_interacao
    )

    return gerar_resumo_interacoes(
        historico_atualizado
    )


# ============================================================
# FORMATAÇÃO
# ============================================================

def formatar_resumo_interacoes(resumo):
    """
    Formata o resumo das interações para apresentação.
    """

    linhas = [

        "RESUMO AUTOMÁTICO DAS INTERAÇÕES",

        "",

        resumo[
            "resumo_textual"
        ]
    ]

    if resumo[
        "temas"
    ]:

        linhas.extend([
            "",
            "TEMAS IDENTIFICADOS:"
        ])

        for tema in resumo[
            "temas"
        ]:

            linhas.append(
                f"- {tema}"
            )

    return "\n".join(
        linhas
    )


# ============================================================
# TESTES
# ============================================================

if __name__ == "__main__":

    raiz_projeto = (
        Path(
            __file__
        )
        .resolve()
        .parents[2]
    )

    caminho_json = (
        raiz_projeto
        / "dados_estruturados.json"
    )

    dados = carregar_dados(
        caminho_json
    )

    # ========================================================
    # TESTE 1 — RESUMO DO RELATÓRIO
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "TESTE 1 - RESUMO AUTOMÁTICO DO RELATÓRIO"
    )

    print(
        "=" * 70
    )

    resumo_relatorio = gerar_resumo_relatorio(
        dados
    )

    print(
        formatar_resumo_relatorio(
            resumo_relatorio
        )
    )

    # ========================================================
    # HISTÓRICO DE TESTE
    # ========================================================

    interacoes_teste = [

        {
            "pergunta":
                (
                    "Meu relatório indica uma "
                    "chance maior de desenvolver diabetes?"
                ),

            "resposta":
                (
                    "O resultado mostra uma relação genética "
                    "com diabetes, mas não é um diagnóstico."
                )
        },

        {
            "pergunta":
                (
                    "O que significa essa "
                    "alteração no DNA?"
                ),

            "resposta":
                (
                    "Uma alteração no DNA é uma característica "
                    "genética identificada durante a análise."
                )
        },

        {
            "pergunta":
                (
                    "Preciso procurar um médico "
                    "por causa desse resultado?"
                ),

            "resposta":
                (
                    "O acompanhamento profissional pode ajudar "
                    "na interpretação do resultado."
                )
        }
    ]

    # ========================================================
    # TESTE 2 — RESUMO DAS INTERAÇÕES
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "TESTE 2 - RESUMO AUTOMÁTICO DAS INTERAÇÕES"
    )

    print(
        "=" * 70
    )

    resumo_interacoes = gerar_resumo_interacoes(
        interacoes_teste
    )

    print(
        formatar_resumo_interacoes(
            resumo_interacoes
        )
    )

    # ========================================================
    # TESTE 3 — DETECÇÃO DE ANCESTRALIDADE
    # ========================================================

    interacao_ancestralidade = {

        "pergunta":
            (
                "O que meu relatório diz "
                "sobre ancestralidade?"
            ),

        "resposta":
            (
                "O relatório mostra predominância "
                "de ancestralidade europeia."
            )
    }

    print(
        "\n" + "=" * 70
    )

    print(
        "TESTE 3 - IDENTIFICAÇÃO DE ANCESTRALIDADE"
    )

    print(
        "=" * 70
    )

    resumo_ancestralidade = gerar_resumo_interacoes(
        [
            interacao_ancestralidade
        ]
    )

    print(
        formatar_resumo_interacoes(
            resumo_ancestralidade
        )
    )

    # ========================================================
    # TESTE 4 — ATUALIZAÇÃO AUTOMÁTICA
    # ========================================================

    nova_interacao = {

        "pergunta":
            (
                "Isso significa que "
                "eu tenho a doença?"
            ),

        "resposta":
            (
                "Não. Uma chance genética maior "
                "não equivale a um diagnóstico."
            )
    }

    print(
        "\n" + "=" * 70
    )

    print(
        "TESTE 4 - ATUALIZAÇÃO AUTOMÁTICA DO RESUMO"
    )

    print(
        "=" * 70
    )

    resumo_atualizado = atualizar_resumo_interacoes(
        interacoes_teste,
        nova_interacao
    )

    print(
        formatar_resumo_interacoes(
            resumo_atualizado
        )
    )