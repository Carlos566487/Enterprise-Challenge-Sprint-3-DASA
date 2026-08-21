"""
sprint3/governanca/revisor_linguagem.py
Genera AI · Dasa · FIAP Sprint 3

Camada de revisão de linguagem responsável para respostas do agente.

Decisão de design (Carlos Eduardo — Governança):
  Dados genéticos são intrinsecamente probabilísticos. Afirmações categóricas
  ("você vai desenvolver X") violam a boa prática médica e podem causar
  ansiedade desnecessária ou, inversamente, falsa segurança. Esta camada
  garante que toda resposta do Genera AI:

    1. Evite terminologia alarmista sem contexto estatístico.
    2. Apresente risco como predisposição, nunca como certeza.
    3. Inclua chamada à consulta especializada quando relevante.

  A revisão é feita por substituição determinística (regex) + heurística,
  sem chamar o LLM de novo — mantém latência e custo sob controle.

Integração:
  Chamar `revisar_linguagem(texto)` APÓS a resposta do LLM e ANTES de
  exibi-la ao usuário. Compatível com o fluxo de `personalizador.py`
  (sprint3/rag_personalizacao).

  Exemplo de integração no personalizador:
    from sprint3.governanca import revisar_linguagem
    resposta_revisada = revisar_linguagem(resultado["resposta"])
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Regras de substituição
# ---------------------------------------------------------------------------

@dataclass
class RegrasAlarmismo:
    """
    Par (padrão_regex, substituição) que define o que é considerado linguagem
    alarmista e como deve ser reformulado.

    Justificativa técnica: usar regex compilado com re.IGNORECASE permite
    capturar variações de capitalização sem multiplicar os padrões.
    """

    substituicoes: list[tuple[str, str]] = field(default_factory=lambda: [
        # ------------------------------------------------------------------ #
        # CATEGORIA 1 — Afirmações de certeza sobre desenvolvimento de doença
        # ------------------------------------------------------------------ #
        (
            r"você (vai|irá|irá) desenvolver",
            "você tem predisposição a desenvolver",
        ),
        (
            r"você (terá|tem) (certeza de|certamente)",
            "segundo o relatório, você apresenta indicadores de",
        ),
        (
            r"vai (desenvolver|ter|contrair)",
            "pode ter maior predisposição a",
        ),
        (
            r"certamente (desenvolverá|terá|apresentará)",
            "segundo os dados do relatório, pode apresentar",
        ),

        # ------------------------------------------------------------------ #
        # CATEGORIA 2 — Escalas de risco sem contexto estatístico
        # ------------------------------------------------------------------ #
        (
            r"risco (muito )?altíssimo",
            "risco elevado (consulte um especialista para avaliação clínica)",
        ),
        (
            r"risco (extremamente|muito) (alto|elevado)",
            "risco aumentado em relação à média populacional",
        ),
        (
            r"risco crítico",
            "risco que merece acompanhamento especializado",
        ),
        (
            r"alto risco",
            "maior atenção recomendada",
        ),

        # ------------------------------------------------------------------ #
        # CATEGORIA 3 — Previsões médicas absolutas
        # ------------------------------------------------------------------ #
        (
            r"você (não )?sobreviverá",
            "[informação fora do escopo do relatório genético]",
        ),
        (
            r"sua expectativa de vida",
            "fatores genéticos relacionados à longevidade",
        ),
        (
            r"você (definitivamente|com certeza) (tem|possui)",
            "o relatório indica predisposição a",
        ),

        # ------------------------------------------------------------------ #
        # CATEGORIA 4 — Diagnósticos implícitos
        # ------------------------------------------------------------------ #
        (
            r"você (tem|possui) (diabetes|câncer|hipertensão|doença cardíaca)",
            r"você apresenta marcadores genéticos associados a \2",
        ),
        (
            r"(diagnóstico|diagnose) (de|é)",
            "predisposição genética relacionada a",
        ),
    ])


# ---------------------------------------------------------------------------
# Heurísticas de contexto ausente
# ---------------------------------------------------------------------------

TERMOS_RISCO_SEM_CONTEXTO = re.compile(
    r"\b(risco|predisposição|probabilidade|chance)\b",
    re.IGNORECASE,
)

CONTEXTO_OBRIGATORIO_PATTERN = re.compile(
    r"(segundo o relatório|predisposição|tendência estatística"
    r"|consulte|marcadores genéticos|média populacional"
    r"|acompanhamento|especialista)",
    re.IGNORECASE,
)

SUFIXO_CONTEXTO = (
    " Segundo o relatório, este dado reflete uma tendência estatística — "
    "consulte um especialista para confirmação clínica."
)


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------

def revisar_linguagem(
    texto: str,
    regras: RegrasAlarmismo | None = None,
    adicionar_contexto_ausente: bool = True,
) -> tuple[str, list[str]]:
    """
    Revisa o texto de uma resposta do agente aplicando as regras de
    linguagem responsável.

    Args:
        texto:
            Resposta gerada pelo LLM a ser revisada.
        regras:
            Instância de RegrasAlarmismo. Se None, usa o conjunto padrão.
        adicionar_contexto_ausente:
            Se True, detecta afirmações de risco sem contexto e adiciona
            SUFIXO_CONTEXTO ao final do parágrafo afetado.

    Returns:
        Tupla (texto_revisado, lista_de_alteracoes) onde lista_de_alteracoes
        documenta cada substituição realizada para rastreabilidade.

    Exemplo:
        >>> texto, log = revisar_linguagem(
        ...     "Você vai desenvolver diabetes com risco altíssimo."
        ... )
        >>> print(texto)
        Você tem predisposição a desenvolver diabetes com risco elevado
        (consulte um especialista para avaliação clínica).
        >>> print(log)
        ['[alarmismo] "você vai desenvolver" → "você tem predisposição..."',
         '[alarmismo] "risco altíssimo" → "risco elevado..."']

    Notas:
        - A função é idempotente: aplicá-la duas vezes no mesmo texto não
          produz duplicações graças à verificação de contexto.
        - Não chama o LLM; latência adicional é desprezível (<1 ms típico).
    """
    if regras is None:
        regras = RegrasAlarmismo()

    texto_revisado = texto
    alteracoes: list[str] = []

    # 1. Substituições de alarmismo
    for padrao_str, substituicao in regras.substituicoes:
        padrao = re.compile(padrao_str, re.IGNORECASE)
        novo_texto = padrao.sub(substituicao, texto_revisado)
        if novo_texto != texto_revisado:
            alteracoes.append(
                f'[alarmismo] "{padrao_str}" → "{substituicao}"'
            )
            texto_revisado = novo_texto

    # 2. Detectar risco sem contexto e adicionar nota
    if adicionar_contexto_ausente:
        paragrafos = texto_revisado.split("\n")
        paragrafos_revisados = []
        for paragrafo in paragrafos:
            tem_risco = TERMOS_RISCO_SEM_CONTEXTO.search(paragrafo)
            tem_contexto = CONTEXTO_OBRIGATORIO_PATTERN.search(paragrafo)
            if tem_risco and not tem_contexto:
                # Só adiciona o sufixo se o parágrafo não for muito curto
                # (evita anotar listas de marcadores com 1 palavra)
                if len(paragrafo.split()) >= 5:
                    paragrafo = paragrafo.rstrip() + SUFIXO_CONTEXTO
                    alteracoes.append(
                        "[contexto ausente] sufixo de contextualização adicionado"
                    )
            paragrafos_revisados.append(paragrafo)
        texto_revisado = "\n".join(paragrafos_revisados)

    return texto_revisado, alteracoes


# ---------------------------------------------------------------------------
# Utilitário de auditoria
# ---------------------------------------------------------------------------

def auditar_resposta(texto: str) -> dict:
    """
    Retorna um relatório de auditoria sem modificar o texto.
    Útil para logging e para testes unitários que verificam se
    uma resposta passaria pela revisão sem alterações.

    Returns:
        {
          "aprovado": bool,
          "numero_de_alteracoes": int,
          "alteracoes": list[str],
          "texto_revisado": str,
        }
    """
    texto_revisado, alteracoes = revisar_linguagem(texto)
    return {
        "aprovado": len(alteracoes) == 0,
        "numero_de_alteracoes": len(alteracoes),
        "alteracoes": alteracoes,
        "texto_revisado": texto_revisado,
    }
