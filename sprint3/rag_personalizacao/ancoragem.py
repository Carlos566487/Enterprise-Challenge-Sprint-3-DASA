"""
Validação de Ancoragem — Sprint 3 / Genera AI / Dasa
Cientista de IA — Personalização & RAG

Verifica programaticamente que a resposta gerada não introduz informação
factual ausente dos trechos recuperados do relatório genético.

Estratégia em duas camadas
──────────────────────────────────────────────────────────────────────────────
1. REGRA DURA (decide `ancorado`)
   Todo elemento factual verificável presente na resposta precisa aparecer
   também no contexto recuperado:
       • números e percentuais   (89, 42,3%, 1.37)
       • identificadores de SNP  (RS7903146)
       • símbolos de gene        (TCF7L2, BRCA2)
   Estes são exatamente os elementos que uma alucinação de LLM inventa e que
   um leitor tomaria como verdade clínica.

2. SCORE SUAVE (apenas informativo)
   Proporção de palavras de conteúdo da resposta que aparecem no contexto.
   Nunca decide bloqueio — texto de enquadramento responsável ("procure um
   profissional", "não representa certeza") é desejável e legitimamente não
   aparece nos trechos.

Por que não exigir sobreposição total de vocabulário:
    O system prompt da Sprint 2 obriga o agente a contextualizar o risco e a
    orientar acompanhamento profissional. Esse texto é de FORMA, não de fato,
    e reprová-lo geraria falso positivo em toda resposta correta.
"""

import re
import unicodedata


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

# Siglas que casam com o padrão de gene mas não são genes.
SIGLAS_NAO_GENE = {
    "DNA", "RNA", "SNP", "SNPS", "LGPD", "PDF", "JSON", "API", "GPT",
    "OMS", "SUS", "CRM", "ACMG", "IMC", "EUA", "IA", "RAG", "LLM",
    "LGPDA", "FIAP", "DASA",
}

# Stopwords em português para o score de sobreposição.
STOPWORDS = {
    "a", "ao", "aos", "as", "com", "como", "da", "das", "de", "do", "dos",
    "e", "em", "essa", "esse", "esta", "este", "isso", "ja", "mas", "mais",
    "na", "nao", "nas", "no", "nos", "o", "os", "ou", "para", "pela", "pelo",
    "por", "que", "se", "sem", "ser", "seu", "sua", "tem", "um", "uma",
    "voce", "sao", "foi", "pode", "poder", "ter", "the", "of",
}

RE_SNP = re.compile(r"\brs\s?\d+\b", re.IGNORECASE)
RE_NUMERO = re.compile(r"\d+(?:[.,]\d+)?")
RE_GENE = re.compile(r"\b[A-Z][A-Z0-9]{2,}\b")
RE_MARCADOR_LISTA = re.compile(r"(?m)^\s*\d+\s*[.)\-]\s+")
RE_PALAVRA = re.compile(r"[a-z0-9]+")


# ─────────────────────────────────────────────────────────────────────────────
# NORMALIZAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def sem_acento(texto: str) -> str:
    """Remove acentos preservando as letras (café -> cafe)."""
    normalizado = unicodedata.normalize("NFD", texto)
    return "".join(c for c in normalizado if unicodedata.category(c) != "Mn")


def _normalizar_numero(token: str) -> str:
    """
    Uniformiza a notação numérica para comparação.

    '42,3' e '42.3' são o mesmo fato; '89' e '89.0' também.
    """
    valor = token.replace(",", ".")
    try:
        numero = float(valor)
    except ValueError:
        return valor
    if numero.is_integer():
        return str(int(numero))
    return str(numero)


def _normalizar_snp(token: str) -> str:
    return token.replace(" ", "").upper()


# ─────────────────────────────────────────────────────────────────────────────
# EXTRAÇÃO DE FATOS
# ─────────────────────────────────────────────────────────────────────────────

def extrair_fatos(texto: str) -> dict:
    """
    Extrai da string os elementos factuais verificáveis.

    Marcadores de lista ("1. ", "2) ") são removidos antes da extração de
    números, para não confundir numeração de tópicos com dado clínico.

    Returns:
        {"numeros": set, "snps": set, "genes": set}
    """
    if not texto:
        return {"numeros": set(), "snps": set(), "genes": set()}

    snps = {_normalizar_snp(t) for t in RE_SNP.findall(texto)}

    # Remove os SNPs antes de procurar números, senão "RS7903146" vira o
    # número 7903146 e polui a comparação.
    texto_sem_snp = RE_SNP.sub(" ", texto)
    texto_sem_lista = RE_MARCADOR_LISTA.sub("", texto_sem_snp)

    numeros = {_normalizar_numero(t) for t in RE_NUMERO.findall(texto_sem_lista)}

    genes = {
        t for t in RE_GENE.findall(texto_sem_snp)
        if t not in SIGLAS_NAO_GENE
    }

    return {"numeros": numeros, "snps": snps, "genes": genes}


def _palavras_conteudo(texto: str) -> set:
    """Palavras significativas, sem acento, sem stopwords, sem números."""
    base = sem_acento(texto.lower())
    return {
        p for p in RE_PALAVRA.findall(base)
        if p not in STOPWORDS and len(p) > 2 and not p.isdigit()
    }


# ─────────────────────────────────────────────────────────────────────────────
# VALIDAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def validar_ancoragem(resposta: str, trechos: list) -> dict:
    """
    Valida se a resposta está ancorada nos trechos recuperados do relatório.

    Args:
        resposta: texto gerado pelo LLM.
        trechos:  lista de strings com o conteúdo dos trechos recuperados.

    Returns:
        {
          "ancorado": bool,               # regra dura: nenhum fato inventado
          "termos_nao_ancorados": [...],  # o que apareceu só na resposta
          "score_sobreposicao": float,    # 0.0–1.0, informativo
          "detalhes": {"numeros": [...], "snps": [...], "genes": [...]},
        }
    """
    contexto = " ".join(trechos or [])

    fatos_resposta = extrair_fatos(resposta or "")
    fatos_contexto = extrair_fatos(contexto)

    numeros_orfaos = sorted(fatos_resposta["numeros"] - fatos_contexto["numeros"])
    snps_orfaos = sorted(fatos_resposta["snps"] - fatos_contexto["snps"])
    genes_orfaos = sorted(fatos_resposta["genes"] - fatos_contexto["genes"])

    nao_ancorados = numeros_orfaos + snps_orfaos + genes_orfaos

    palavras_resposta = _palavras_conteudo(resposta or "")
    palavras_contexto = _palavras_conteudo(contexto)

    if palavras_resposta:
        comuns = palavras_resposta & palavras_contexto
        score = round(len(comuns) / len(palavras_resposta), 4)
    else:
        score = 0.0

    return {
        "ancorado": len(nao_ancorados) == 0,
        "termos_nao_ancorados": nao_ancorados,
        "score_sobreposicao": score,
        "detalhes": {
            "numeros": numeros_orfaos,
            "snps": snps_orfaos,
            "genes": genes_orfaos,
        },
    }


def mensagem_ancoragem_falha() -> str:
    """
    Resposta segura usada quando a política é "bloquear" e a validação falha.

    Mantém o mesmo tom das mensagens de guardrail da Sprint 2: não inventa,
    não alarma, e direciona para verificação profissional.
    """
    return (
        "Não consegui confirmar todos os detalhes dessa resposta diretamente "
        "no seu relatório genético. Para não apresentar informação que eu não "
        "consiga rastrear até o documento, prefiro não responder desta vez. "
        "Você pode reformular a pergunta ou levar esse ponto ao profissional "
        "de saúde que acompanha o seu caso."
    )
