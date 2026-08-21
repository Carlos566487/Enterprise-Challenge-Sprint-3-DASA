"""
Módulo de NLP — Simplificação de Linguagem
DASA / Genera — Sprint 3

Responsável por transformar linguagem técnica relacionada à genética
em explicações mais claras e acessíveis para usuários leigos.

O módulo também calcula métricas simples de legibilidade para permitir
a comparação objetiva entre o texto técnico original e sua versão
simplificada.

A estratégia utiliza regras determinísticas e rastreáveis, evitando
alterações no significado clínico do conteúdo.
"""

import re


# ============================================================
# REGRAS DE SIMPLIFICAÇÃO
# ============================================================

REGRAS_SIMPLIFICACAO = [
    (
        "uma variante genética associada a uma predisposição genética",
        "uma alteração no DNA ligada a uma chance maior"
    ),
    (
        "variante genética associada a uma predisposição genética",
        "alteração no DNA ligada a uma chance maior"
    ),
    (
        "foram avaliados marcadores genéticos presentes no DNA",
        "foram analisadas características do DNA"
    ),
    (
        "foram avaliados marcadores genéticos",
        "foram analisadas características do DNA"
    ),
    (
        "marcadores genéticos presentes no DNA",
        "características do DNA"
    ),
    (
        "marcadores genéticos",
        "características do DNA"
    ),
    (
        "o genótipo deve ser interpretado em conjunto com outros fatores",
        "essas informações do DNA devem ser analisadas junto com outros fatores"
    ),
    (
        "o genótipo deve ser interpretado",
        "essas informações do DNA devem ser analisadas"
    ),
    (
        "não significa que a pessoa necessariamente desenvolverá a condição",
        "não significa que a pessoa terá essa condição"
    ),
    (
        "não representa um diagnóstico definitivo",
        "não é um diagnóstico"
    ),
    (
        "apresenta uma associação genética",
        "mostra uma relação com fatores genéticos"
    ),
    (
        "predisposição genética",
        "maior chance ligada à genética"
    ),
    (
        "variante genética",
        "alteração no DNA"
    ),
    (
        "risco aumentado",
        "chance maior"
    ),
    (
        "risco reduzido",
        "chance menor"
    ),
    (
        "genótipo",
        "informações do DNA"
    ),
    (
        "fenótipo",
        "característica observável"
    ),
    (
        "herdabilidade",
        "influência da genética"
    ),
    (
        "polimorfismo",
        "variação comum no DNA"
    ),
    (
        "alelo",
        "versão de um gene"
    )
]


# ============================================================
# NORMALIZAÇÃO DO TEXTO
# ============================================================

def limpar_texto(texto: str) -> str:
    """
    Normaliza espaços, tabulações e quebras de linha.

    As quebras internas são transformadas em espaços para impedir
    que uma expressão técnica seja dividida em duas linhas e deixe
    de ser reconhecida pelas regras de NLP.
    """

    if not texto:
        return ""

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


# ============================================================
# SUBSTITUIÇÃO SEGURA
# ============================================================

def criar_padrao_flexivel(expressao: str):
    """
    Cria um padrão regex capaz de reconhecer uma expressão
    mesmo quando houver diferentes quantidades de espaços.
    """

    palavras = expressao.split()

    padrao = r"\s+".join(
        re.escape(palavra)
        for palavra in palavras
    )

    return re.compile(
        padrao,
        flags=re.IGNORECASE
    )


def substituir_expressao(
    texto: str,
    original: str,
    simplificado: str
) -> str:
    """
    Substitui uma expressão técnica por uma versão acessível.
    """

    padrao = criar_padrao_flexivel(
        original
    )

    return padrao.sub(
        simplificado,
        texto
    )


# ============================================================
# APLICAÇÃO DAS REGRAS
# ============================================================

def aplicar_regras(texto: str) -> str:
    """
    Aplica as regras de simplificação.

    As expressões maiores são processadas primeiro para evitar
    substituições parciais e problemas de concordância.
    """

    resultado = texto

    regras_ordenadas = sorted(
        REGRAS_SIMPLIFICACAO,
        key=lambda item: len(item[0]),
        reverse=True
    )

    for original, simplificado in regras_ordenadas:

        resultado = substituir_expressao(
            resultado,
            original,
            simplificado
        )

    return resultado


# ============================================================
# AJUSTES DE FLUIDEZ
# ============================================================

def ajustar_fluidez(texto: str) -> str:
    """
    Faz ajustes finais para manter naturalidade e clareza.
    """

    ajustes = [
        (
            "ligada a uma chance maior para determinada condição",
            "ligada a uma chance maior de desenvolver determinada condição"
        ),
        (
            "maior chance ligada à genética para determinada condição",
            "maior chance de desenvolver determinada condição por fatores genéticos"
        ),
        (
            "chance maior para determinada condição",
            "chance maior de desenvolver determinada condição"
        )
    ]

    resultado = texto

    for original, simplificado in ajustes:

        resultado = substituir_expressao(
            resultado,
            original,
            simplificado
        )

    return resultado


# ============================================================
# CAPITALIZAÇÃO
# ============================================================

def corrigir_capitalizacao(texto: str) -> str:
    """
    Garante letra maiúscula no início do texto
    e após pontuação final.
    """

    if not texto:
        return ""

    texto = texto[0].upper() + texto[1:]

    texto = re.sub(
        r"([.!?]\s+)([a-záàâãéêíóôõúç])",
        lambda match: (
            match.group(1)
            + match.group(2).upper()
        ),
        texto
    )

    return texto


# ============================================================
# MÉTRICAS DE LEGIBILIDADE
# ============================================================

def dividir_frases(texto: str) -> list:
    """
    Divide o texto em frases.
    """

    frases = re.split(
        r"[.!?]+",
        texto
    )

    return [
        frase.strip()
        for frase in frases
        if frase.strip()
    ]


def calcular_metricas(texto: str) -> dict:
    """
    Calcula métricas simples de legibilidade.

    Retorna:
    - quantidade de palavras;
    - quantidade de frases;
    - média de palavras por frase;
    - média de caracteres por palavra.
    """

    palavras = re.findall(
        r"\b\w+\b",
        texto
    )

    frases = dividir_frases(
        texto
    )

    quantidade_palavras = len(
        palavras
    )

    quantidade_frases = len(
        frases
    )

    if quantidade_palavras > 0:

        media_caracteres = (
            sum(
                len(palavra)
                for palavra in palavras
            )
            / quantidade_palavras
        )

    else:
        media_caracteres = 0

    if quantidade_frases > 0:

        media_palavras_frase = (
            quantidade_palavras
            / quantidade_frases
        )

    else:
        media_palavras_frase = 0

    return {
        "palavras":
            quantidade_palavras,

        "frases":
            quantidade_frases,

        "media_palavras_por_frase":
            round(
                media_palavras_frase,
                2
            ),

        "media_caracteres_por_palavra":
            round(
                media_caracteres,
                2
            )
    }


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def simplificar_texto(texto: str) -> dict:
    """
    Função principal do módulo.

    Recebe um texto técnico e retorna:
    - texto original normalizado;
    - texto simplificado;
    - métricas do texto original;
    - métricas do texto simplificado.
    """

    if not texto or not texto.strip():

        return {
            "texto_original": "",
            "texto_simplificado": "",
            "metricas_original": {},
            "metricas_simplificado": {}
        }

    texto_original = limpar_texto(
        texto
    )

    texto_simplificado = aplicar_regras(
        texto_original
    )

    texto_simplificado = ajustar_fluidez(
        texto_simplificado
    )

    texto_simplificado = limpar_texto(
        texto_simplificado
    )

    texto_simplificado = corrigir_capitalizacao(
        texto_simplificado
    )

    return {
        "texto_original":
            texto_original,

        "texto_simplificado":
            texto_simplificado,

        "metricas_original":
            calcular_metricas(
                texto_original
            ),

        "metricas_simplificado":
            calcular_metricas(
                texto_simplificado
            )
    }


# ============================================================
# TESTE ISOLADO
# ============================================================

if __name__ == "__main__":

    texto_teste = """
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

    resultado = simplificar_texto(
        texto_teste
    )

    print(
        "\nTEXTO ORIGINAL:"
    )

    print(
        resultado[
            "texto_original"
        ]
    )

    print(
        "\nTEXTO SIMPLIFICADO:"
    )

    print(
        resultado[
            "texto_simplificado"
        ]
    )

    print(
        "\nMÉTRICAS DO TEXTO ORIGINAL:"
    )

    print(
        resultado[
            "metricas_original"
        ]
    )

    print(
        "\nMÉTRICAS DO TEXTO SIMPLIFICADO:"
    )

    print(
        resultado[
            "metricas_simplificado"
        ]
    )