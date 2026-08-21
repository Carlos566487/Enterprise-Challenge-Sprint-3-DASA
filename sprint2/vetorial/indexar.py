"""
Indexador Vetorial — Sprint 2 / Genera / Dasa
Lê chunks.json e indexa na base vetorial ChromaDB.
"""

import json
import sys
from pathlib import Path
import chromadb

# ── Caminhos ──────────────────────────────────────────────────────────────────
RAIZ = Path(__file__).resolve().parents[2]
CHUNKS_JSON = RAIZ / "sprint2" / "embeddings" / "chunks.json"
BASE_VETORIAL = Path(__file__).parent / "base_vetorial"
COLECAO_NOME = "genera_relatorio"


def carregar_chunks(caminho: Path) -> list[dict]:
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def indexar(chunks: list[dict], base_path: Path) -> chromadb.Collection:
    base_path.mkdir(parents=True, exist_ok=True)

    cliente = chromadb.PersistentClient(path=str(base_path))

    # Remove coleção anterior se existir (reindexação limpa)
    try:
        cliente.delete_collection(COLECAO_NOME)
        print(
            f"  Coleção anterior '{COLECAO_NOME}' removida para reindexação.")
    except Exception:
        pass

    colecao = cliente.create_collection(
        name=COLECAO_NOME,
        metadata={"hnsw:space": "cosine"}
    )

    ids = [c["id"] for c in chunks]
    embeddings = [c["embedding"] for c in chunks]
    documentos = [c["conteudo"] for c in chunks]
    metadados = [{"secao": c["secao"], "fonte": c["fonte"]} for c in chunks]

    colecao.add(
        ids=ids,
        embeddings=embeddings,
        documents=documentos,
        metadatas=metadados
    )

    print(f"  {colecao.count()} documentos indexados na coleção '{COLECAO_NOME}'.")
    return colecao


def main(chunks_path: Path = CHUNKS_JSON):
    print("=" * 60)
    print("INDEXADOR VETORIAL — Sprint 2 / Genera")
    print("=" * 60)

    if not chunks_path.exists():
        print(f"[ERRO] chunks.json não encontrado: {chunks_path}")
        print("       Execute primeiro: python sprint2/embeddings/gerar_embeddings.py")
        sys.exit(1)

    print(f"\n[1/3] Carregando chunks: {chunks_path}")
    chunks = carregar_chunks(chunks_path)
    print(f"      {len(chunks)} chunks carregados.")

    print(f"[2/3] Indexando no ChromaDB em: {BASE_VETORIAL}")
    colecao = indexar(chunks, BASE_VETORIAL)

    print(f"[3/3] Verificando indexação...")
    total = colecao.count()
    print(f"\n[OK] Base vetorial criada com {total} documentos.")
    print(f"     Localização: {BASE_VETORIAL}")
    return colecao


if __name__ == "__main__":
    entrada = Path(sys.argv[1]) if len(sys.argv) > 1 else CHUNKS_JSON
    main(entrada)
