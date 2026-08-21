"""
Perfis de Personalização — Sprint 3 / Genera AI / Dasa
Cientista de IA — Personalização & RAG

Define os perfis de usuário suportados e as regras explícitas de
personalização: o que PODE variar por perfil e o que NUNCA varia.

Princípio central:
    A personalização atua sobre a FORMA da resposta (tom, profundidade,
    vocabulário, quantidade de trechos recuperados).
    Nunca sobre o CONTEÚDO (fatos, números, marcadores, nível de risco),
    que permanece ancorado no relatório genético do paciente.
"""

from dataclasses import dataclass


# ─────────────────────────────────────────────────────────────────────────────
# REGRAS DE PERSONALIZAÇÃO (documentadas e verificáveis)
# ─────────────────────────────────────────────────────────────────────────────

PODE_VARIAR = (
    "tom da resposta (acolhedor, didático, objetivo)",
    "profundidade da explicação",
    "vocabulário (simples x técnico)",
    "quantidade de trechos recuperados (top_k)",
    "ordem de apresentação das informações",
    "omissão de introduções já vistas pelo usuário (continuidade)",
)

NUNCA_VARIA = (
    "os fatos do relatório (doença, categoria, nível de risco)",
    "valores numéricos (percentis, escores, percentuais)",
    "marcadores genéticos (SNPs, genes, alelos)",
    "o veredito dos guardrails médicos",
    "o limiar de similaridade da busca semântica",
    "a exigência de que toda resposta seja ancorada no relatório",
)


# ─────────────────────────────────────────────────────────────────────────────
# ESTRUTURA DO PERFIL
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Perfil:
    """
    Configuração imutável de um perfil de usuário.

    Campos:
        id        — identificador estável usado no contrato público
        rotulo    — nome legível para exibição no dashboard
        modo      — modo aceito pelo agente da Sprint 2: "paciente" | "tecnico"
        top_k     — quantos trechos recuperar da base vetorial
        diretiva  — instrução de FORMA anexada à pergunta enviada ao agente
        descricao — para que serve este perfil
    """

    id: str
    rotulo: str
    modo: str
    top_k: int
    diretiva: str
    descricao: str


# ─────────────────────────────────────────────────────────────────────────────
# PERFIS SUPORTADOS
# ─────────────────────────────────────────────────────────────────────────────
#
# IMPORTANTE — as diretivas abaixo são anexadas à pergunta antes de chegar ao
# agente da Sprint 2, e os guardrails fazem matching por substring na pergunta.
# Portanto NENHUMA diretiva pode conter termos das listas de guardrail
# (ex.: "diagnóstico", "tratamento", "dose", "consulta médica").
# Isso é verificado programaticamente por validar_diretivas() e por teste.

PERFIL_LEIGO_ANSIOSO = Perfil(
    id="leigo_ansioso",
    rotulo="Paciente (ansioso)",
    modo="paciente",
    top_k=3,
    diretiva=(
        "Adapte a FORMA da resposta: use tom calmo e acolhedor, frases curtas "
        "e linguagem simples. Deixe claro que predisposição genética representa "
        "tendência estatística, e não certeza. Evite linguagem alarmista. "
        "Não altere nenhum dado do relatório."
    ),
    descricao=(
        "Paciente leigo que demonstra preocupação. Prioriza acolhimento e "
        "contextualização do risco, sem minimizar nem dramatizar o resultado."
    ),
)

PERFIL_LEIGO_CURIOSO = Perfil(
    id="leigo_curioso",
    rotulo="Paciente (curioso)",
    modo="paciente",
    top_k=4,
    diretiva=(
        "Adapte a FORMA da resposta: use linguagem simples, porém explique o "
        "mecanismo biológico por trás do resultado sempre que o relatório "
        "trouxer essa informação. Pode aprofundar a explicação. "
        "Não altere nenhum dado do relatório."
    ),
    descricao=(
        "Paciente leigo que quer entender o porquê. Prioriza explicação do "
        "mecanismo em linguagem acessível, com mais trechos recuperados."
    ),
)

PERFIL_MEDICO = Perfil(
    id="medico",
    rotulo="Profissional de saúde",
    modo="tecnico",
    top_k=5,
    diretiva=(
        "Adapte a FORMA da resposta: use linguagem técnica e objetiva, "
        "priorizando marcadores genéticos, escores e classificação de risco "
        "exatamente como constam no relatório. "
        "Não altere nenhum dado do relatório."
    ),
    descricao=(
        "Profissional de saúde avaliando o paciente. Prioriza precisão "
        "técnica, marcadores e percentis, com recuperação mais ampla."
    ),
)


PERFIS = {
    PERFIL_LEIGO_ANSIOSO.id: PERFIL_LEIGO_ANSIOSO,
    PERFIL_LEIGO_CURIOSO.id: PERFIL_LEIGO_CURIOSO,
    PERFIL_MEDICO.id: PERFIL_MEDICO,
}

PERFIL_PADRAO = PERFIL_LEIGO_ANSIOSO.id


# Diretiva de continuidade — aplicada quando o histórico indica que o usuário
# já interagiu antes. Também não pode conter termos de guardrail.
DIRETIVA_CONTINUIDADE = (
    "O usuário já consultou este relatório em interações anteriores; "
    "evite repetir explicações introdutórias já apresentadas."
)


# ─────────────────────────────────────────────────────────────────────────────
# ACESSO E VALIDAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def obter_perfil(perfil_id: str) -> Perfil:
    """
    Retorna o Perfil correspondente ao identificador.

    Raises:
        ValueError: se o perfil não existir (falha explícita, sem fallback
                    silencioso — o dashboard deve receber erro claro).
    """
    if perfil_id not in PERFIS:
        disponiveis = ", ".join(sorted(PERFIS))
        raise ValueError(
            f"Perfil desconhecido: {perfil_id!r}. Perfis válidos: {disponiveis}."
        )
    return PERFIS[perfil_id]


def listar_perfis() -> list:
    """Lista os perfis disponíveis, para o dashboard montar o seletor."""
    return [
        {
            "id": p.id,
            "rotulo": p.rotulo,
            "modo": p.modo,
            "descricao": p.descricao,
        }
        for p in PERFIS.values()
    ]


def _termos_de_guardrail() -> list:
    """
    Carrega as listas de termos bloqueados do módulo de guardrails da Sprint 2.

    Import local (e não no topo) para que este módulo possa ser lido e testado
    sem depender do sys.path da Sprint 2 já estar configurado.
    """
    from guardrails import (
        TERMOS_DIAGNOSTICO,
        TERMOS_PRESCRICAO,
        TERMOS_RISCO_ALTO,
        TERMOS_FORA_ESCOPO,
    )

    return (
        list(TERMOS_DIAGNOSTICO)
        + list(TERMOS_PRESCRICAO)
        + list(TERMOS_RISCO_ALTO)
        + list(TERMOS_FORA_ESCOPO)
    )


def validar_diretivas() -> dict:
    """
    Verifica que nenhuma diretiva de personalização contém termos que
    disparariam os guardrails médicos da Sprint 2.

    Sem esta garantia, anexar a diretiva à pergunta poderia transformar uma
    pergunta legítima em uma pergunta bloqueada (falso positivo de guardrail).

    Returns:
        {"valido": bool, "violacoes": [{"perfil": str, "termo": str}, ...]}
    """
    termos = _termos_de_guardrail()
    violacoes = []

    alvos = [(p.id, p.diretiva) for p in PERFIS.values()]
    alvos.append(("_continuidade", DIRETIVA_CONTINUIDADE))

    for nome, texto in alvos:
        texto_normalizado = texto.lower()
        for termo in termos:
            if termo.lower() in texto_normalizado:
                violacoes.append({"perfil": nome, "termo": termo})

    return {"valido": len(violacoes) == 0, "violacoes": violacoes}
