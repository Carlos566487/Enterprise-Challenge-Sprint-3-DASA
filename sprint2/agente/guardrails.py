"""
Guardrails do Agente Genera AI

Este módulo valida perguntas do usuário antes da geração da resposta.
O objetivo é impedir diagnósticos, prescrições, previsões médicas absolutas
e respostas fora do escopo do relatório genético.
"""

TERMOS_DIAGNOSTICO = [
    "tenho câncer",
    "estou com câncer",
    "tenho diabetes",
    "estou doente",
    "qual doença eu tenho",
    "me diagnostique",
    "diagnóstico",
    "vou desenvolver",
    "vou ter",
]

TERMOS_PRESCRICAO = [
    "qual remédio",
    "que remédio",
    "posso tomar",
    "devo tomar",
    "qual medicamento",
    "tratamento",
    "dose",
    "dosagem",
    "prescrição",
]

TERMOS_RISCO_ALTO = [
    "vou morrer",
    "quanto tempo vou viver",
    "minha expectativa de vida",
    "posso ignorar o médico",
    "não preciso ir ao médico",
    "devo operar",
    "cirurgia",
]

TERMOS_FORA_ESCOPO = [
    "horóscopo",
    "signo",
    "dieta para emagrecer",
    "treino",
    "resultado de exame de sangue",
    "pressão arterial",
    "consulta médica",
]


def normalizar_texto(texto: str) -> str:
    """
    Padroniza o texto para facilitar a validação.
    """
    return texto.lower().strip()


def verificar_guardrails(pergunta: str) -> dict:
    """
    Verifica se a pergunta viola alguma regra de segurança.

    Retorna um dicionário com:
    - permitido: bool
    - categoria: str
    - mensagem: str
    """

    pergunta_normalizada = normalizar_texto(pergunta)

    if any(termo in pergunta_normalizada for termo in TERMOS_DIAGNOSTICO):
        return {
            "permitido": False,
            "categoria": "diagnostico",
            "mensagem": (
                "Posso ajudar a interpretar informações presentes no relatório genético, "
                "mas não posso realizar diagnósticos médicos. Para uma avaliação clínica, "
                "é necessário procurar um profissional de saúde."
            ),
        }

    if any(termo in pergunta_normalizada for termo in TERMOS_PRESCRICAO):
        return {
            "permitido": False,
            "categoria": "prescricao",
            "mensagem": (
                "Não posso indicar medicamentos, doses ou tratamentos. "
                "Meu papel é apenas explicar informações do relatório genético de forma educativa."
            ),
        }

    if any(termo in pergunta_normalizada for termo in TERMOS_RISCO_ALTO):
        return {
            "permitido": False,
            "categoria": "risco_alto",
            "mensagem": (
                "Essa pergunta envolve uma decisão ou previsão médica sensível. "
                "O relatório genético pode indicar predisposições, mas não determina sozinho "
                "diagnóstico, prognóstico ou conduta médica."
            ),
        }

    if any(termo in pergunta_normalizada for termo in TERMOS_FORA_ESCOPO):
        return {
            "permitido": False,
            "categoria": "fora_escopo",
            "mensagem": (
                "Essa pergunta está fora do escopo do agente. "
                "Eu consigo responder apenas sobre informações presentes no relatório genético enviado."
            ),
        }

    return {
        "permitido": True,
        "categoria": "permitida",
        "mensagem": "Pergunta permitida.",
    }


def validar_contexto(contexto: str) -> dict:
    """
    Verifica se existem trechos recuperados suficientes para responder.
    """

    if contexto is None or contexto.strip() == "":
        return {
            "permitido": False,
            "categoria": "sem_contexto",
            "mensagem": (
                "Não encontrei informações suficientes no relatório enviado para responder com segurança."
            ),
        }

    return {
        "permitido": True,
        "categoria": "contexto_valido",
        "mensagem": "Contexto válido.",
    }
