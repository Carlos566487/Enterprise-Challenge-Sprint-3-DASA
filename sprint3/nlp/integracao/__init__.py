"""
sprint3/nlp/integracao — Integração do NLP com Agente Especialista
Genera AI · Dasa · FIAP Sprint 3

Autora: Tayná Esteves (RM562491)

Este submódulo demonstra a integração entre:
- Agente Especialista (Sprint 2)
- Módulo de NLP (Sprint 3)
- Histórico de interações

Nota: Este módulo usa resposta simulada para testes.
Para produção, use sprint3/integracao/adaptador_nlp.py que integra
com o RAG personalizado real.
"""

import sys
from pathlib import Path

_DIR_PACOTE = Path(__file__).resolve().parent
if str(_DIR_PACOTE) not in sys.path:
    sys.path.insert(0, str(_DIR_PACOTE))

# Este módulo é principalmente para demonstração/testes
# A integração real está em sprint3/integracao/

__all__ = []
