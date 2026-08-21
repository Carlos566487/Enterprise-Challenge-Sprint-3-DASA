"""
Pipeline Completo — Sprint 2 / Genera / Dasa
Une extração de chunks, geração de embeddings e indexação vetorial.
Aceita um arquivo JSON como argumento para reindexação automática.

Uso:
    python sprint2/pipeline/pipeline_completo.py
    python sprint2/pipeline/pipeline_completo.py caminho/para/novo_relatorio.json
"""

import sys
import time
import importlib.util
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def _importar(caminho_relativo: str):
    caminho = RAIZ / caminho_relativo
    spec = importlib.util.spec_from_file_location("modulo", caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def executar_pipeline(caminho_json: Path):
    inicio = time.time()

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETO — Sprint 2 / Genera / Dasa")
    print("=" * 60)
    print(f"Arquivo de entrada: {caminho_json}\n")

    # Etapa 1: Gerar embeddings
    print(">>> ETAPA 1: Geração de Embeddings")
    mod_emb = _importar("sprint2/embeddings/gerar_embeddings.py")
    chunks = mod_emb.main(caminho_json)

    # Etapa 2: Indexar na base vetorial
    print("\n>>> ETAPA 2: Indexação Vetorial")
    mod_idx = _importar("sprint2/vetorial/indexar.py")
    mod_idx.main()

    duracao = time.time() - inicio
    print(f"\n{'=' * 60}")
    print(f"PIPELINE CONCLUÍDO em {duracao:.1f}s")
    print(f"  Chunks gerados: {len(chunks)}")
    print(f"  Base vetorial: sprint2/vetorial/base_vetorial/")
    print(f"  Pronto para busca semântica.")
    print("=" * 60)


if __name__ == "__main__":
    JSON_PADRAO = RAIZ / "dados_estruturados.json"
    caminho = Path(sys.argv[1]) if len(sys.argv) > 1 else JSON_PADRAO
    executar_pipeline(caminho)
