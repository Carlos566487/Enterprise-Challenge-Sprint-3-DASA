"""
Extração PDF → JSON — Sprint 1 / Genera AI / Dasa

Superfície pública do extrator.

    import sys; sys.path.insert(0, "<raiz do repo>")
    from sprint1.extracao import extrair_relatorio

    resultado = extrair_relatorio("sprint1/relatorio_genera_simulado.pdf")
    resultado["dados"]   # dict no schema do projeto
    resultado["avisos"]  # campos não extraídos, com motivo

O PDF de entrada não é versionado (política de privacidade) — ver
sprint1/README_dados_simulados.md para regenerá-lo.
"""

import sys
from pathlib import Path

_DIR_PACOTE = Path(__file__).resolve().parent
if str(_DIR_PACOTE) not in sys.path:
    sys.path.insert(0, str(_DIR_PACOTE))

from extrair_pdf import ErroExtracao, extrair_relatorio   # noqa: E402
from secoes import reparar_codepoints                     # noqa: E402

__all__ = ["extrair_relatorio", "ErroExtracao", "reparar_codepoints"]
