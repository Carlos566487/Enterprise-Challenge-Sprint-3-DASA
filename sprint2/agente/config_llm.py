"""
Configurações do modelo de linguagem.
"""

MODELO = "gpt-4.1-mini"

TEMPERATURA = 0.2

TOP_P = 0.8

MAX_TOKENS = 700

FREQUENCY_PENALTY = 0

PRESENCE_PENALTY = 0


CONFIG = {

"usar_rag": True,

"mostrar_fontes": True,

"modo_padrao": "paciente",

"permitir_resposta_sem_contexto": False

}
