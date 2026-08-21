"""
RAG Personalização — Sprint 3 / Genera AI / Dasa
Cientista de IA — Personalização & RAG

Superfície pública do pacote. O dashboard e qualquer outro consumidor devem
importar exclusivamente daqui — os módulos internos podem ser reorganizados
sem quebrar quem depende deste contrato.

Uso a partir da raiz do repositório:

    import sys
    sys.path.insert(0, "<raiz do repo>")

    from sprint3.rag_personalizacao import responder_personalizado

    resultado = responder_personalizado(
        pergunta="Eu tenho risco de diabetes?",
        perfil="leigo_ansioso",
        usuario_id="paciente-001",
        api_key=OPENAI_API_KEY,
    )

Este pacote NÃO depende de sprint3/nlp/ — ver README_rag_personalizacao.md,
seção "Relação com sprint3/nlp/".
"""

import sys
from pathlib import Path

# Os módulos internos usam imports planos (mesma convenção de sprint2/agente).
# Garantir o próprio diretório no sys.path permite que este pacote funcione
# tanto importado como pacote quanto executado diretamente.
_DIR_PACOTE = Path(__file__).resolve().parent
if str(_DIR_PACOTE) not in sys.path:
    sys.path.insert(0, str(_DIR_PACOTE))

from ancoragem import extrair_fatos, validar_ancoragem            # noqa: E402
from historico import (                                           # noqa: E402
    HistoricoJSON,
    HistoricoMemoria,
    RepositorioHistorico,
)
from perfis import (                                              # noqa: E402
    NUNCA_VARIA,
    PERFIS,
    PODE_VARIAR,
    listar_perfis,
    obter_perfil,
    validar_diretivas,
)
from personalizador import (                                      # noqa: E402
    VERSAO_CONTRATO,
    montar_pergunta_personalizada,
    responder_personalizado,
)

__all__ = [
    "responder_personalizado",
    "VERSAO_CONTRATO",
    "montar_pergunta_personalizada",
    "listar_perfis",
    "obter_perfil",
    "validar_diretivas",
    "PERFIS",
    "PODE_VARIAR",
    "NUNCA_VARIA",
    "RepositorioHistorico",
    "HistoricoMemoria",
    "HistoricoJSON",
    "validar_ancoragem",
    "extrair_fatos",
]
