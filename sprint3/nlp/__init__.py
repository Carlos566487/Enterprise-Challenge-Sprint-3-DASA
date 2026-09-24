"""
sprint3/nlp — Módulo de NLP e Automação de Resumos
Genera AI · Dasa · FIAP Sprint 3

Autora: Tayná Esteves (RM562491)
Responsabilidade: NLP & Automação de Resumos

Este módulo oferece:
- Simplificação de linguagem técnica para acessível
- Geração de resumos automáticos do relatório
- Geração de resumos das interações do usuário
- Métricas de legibilidade

Exporta:
  - simplificar_texto()          : função principal de simplificação
  - gerar_resumo_relatorio()     : resumo do relatório genético
  - gerar_resumo_interacoes()    : resumo do histórico de perguntas
  - formatar_resumo_interacoes() : formatação do resumo
"""

import sys
from pathlib import Path

# Adiciona o diretório ao sys.path para permitir imports relativos
_DIR_PACOTE = Path(__file__).resolve().parent
if str(_DIR_PACOTE) not in sys.path:
    sys.path.insert(0, str(_DIR_PACOTE))

try:
    from nlp_simplificacao import (  # noqa: E402
        calcular_metricas,
        dividir_frases,
        limpar_texto,
        simplificar_termos,
        simplificar_texto,
        substituir_termo,
    )
except ImportError:
    # Fallback caso o import falhe
    simplificar_texto = None
    calcular_metricas = None
    limpar_texto = None
    dividir_frases = None
    simplificar_termos = None
    substituir_termo = None

try:
    from resumos_automaticos import (  # noqa: E402
        atualizar_resumo_interacoes,
        formatar_resumo_interacoes,
        gerar_resumo_interacoes,
        gerar_resumo_relatorio,
        identificar_temas,
    )
except ImportError:
    # Fallback caso o import falhe
    gerar_resumo_relatorio = None
    gerar_resumo_interacoes = None
    formatar_resumo_interacoes = None
    atualizar_resumo_interacoes = None
    identificar_temas = None

__all__ = [
    # Simplificação
    "simplificar_texto",
    "calcular_metricas",
    "limpar_texto",
    "dividir_frases",
    "simplificar_termos",
    "substituir_termo",
    # Resumos
    "gerar_resumo_relatorio",
    "gerar_resumo_interacoes",
    "formatar_resumo_interacoes",
    "atualizar_resumo_interacoes",
    "identificar_temas",
]
