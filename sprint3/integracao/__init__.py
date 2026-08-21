"""
Integração RAG Personalizado + NLP — Sprint 3 / Genera AI / Dasa

Superfície pública do módulo de integração.

Uso a partir da raiz do repositório:

    import sys
    sys.path.insert(0, "<raiz do repo>")

    from sprint3.integracao import responder_com_linguagem_simples

    resultado = responder_com_linguagem_simples(
        pergunta="Eu tenho risco de diabetes?",
        perfil="leigo_ansioso",
        usuario_id="paciente-001",
        api_key=OPENAI_API_KEY,
    )
    texto_para_exibir = resultado["resposta_simplificada"]

Este módulo é a ÚNICA ponte entre sprint3/rag_personalizacao/ e sprint3/nlp/.
Nenhum dos dois pacotes depende dele — ver README_integracao.md.
"""

import sys
from pathlib import Path

_DIR_PACOTE = Path(__file__).resolve().parent
if str(_DIR_PACOTE) not in sys.path:
    sys.path.insert(0, str(_DIR_PACOTE))

from adaptador_nlp import (                                  # noqa: E402
    VERSAO_CONTRATO_INTEGRACAO,
    responder_com_linguagem_simples,
)

__all__ = [
    "responder_com_linguagem_simples",
    "VERSAO_CONTRATO_INTEGRACAO",
]
