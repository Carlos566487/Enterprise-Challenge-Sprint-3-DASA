"""
Coleta de rankings de similaridade — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Para as 20 perguntas de perguntas.json, grava o ranking real devolvido pela
busca com top_k=25 (base inteira) e com top_k=10, limiar 0 — a matéria-prima
da curva de limiar (curva_limiar.py), que aplica os cortes analiticamente.

Dois modos:

  --modelo producao
      Busca de produção sem alteração: sprint2/vetorial/buscar.py::buscar_trechos
      sobre sprint2/vetorial/base_vetorial (all-MiniLM-L6-v2).

  --modelo multilingue --base-dir <diretório FORA do repositório>
      Experimento da causa raiz. Monta uma base ChromaDB PARALELA no diretório
      indicado, com os MESMOS 25 documentos e metadados da base de produção
      (lidos dela, não regenerados) codificados por
      paraphrase-multilingual-MiniLM-L12-v2, e consulta com a MESMA lógica de
      buscar_trechos (coleção cosine; similaridade = round(1 - distância, 4)).
      A base de produção e gerar_embeddings.py não são tocados.

Uso:
    python sprint4/avaliacao/coletar_rankings.py --modelo producao
    python sprint4/avaliacao/coletar_rankings.py --modelo multilingue --base-dir <tmp>
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

BASE_PRODUCAO = RAIZ / "sprint2" / "vetorial" / "base_vetorial"
COLECAO = "genera_relatorio"
MODELO_MULTILINGUE = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_KS = (25, 10)


def documentos_de_producao() -> dict:
    """Lê ids, documentos e metadados da base de produção (somente leitura)."""
    import chromadb

    col = chromadb.PersistentClient(path=str(BASE_PRODUCAO)).get_collection(COLECAO)
    dados = col.get(include=["documents", "metadatas", "embeddings"])
    return {"ids": dados["ids"], "documentos": dados["documents"],
            "metadados": dados["metadatas"], "dimensao": len(dados["embeddings"][0])}


def buscador_producao():
    from sprint2.vetorial.buscar import MODELO_NOME, buscar_trechos

    def buscar(pergunta, top_k):
        return buscar_trechos(pergunta, top_k=top_k, similaridade_minima=0.0)

    return buscar, {"modelo": MODELO_NOME, "base": "sprint2/vetorial/base_vetorial (produção)"}


def buscador_multilingue(base_dir: Path):
    import chromadb
    from sentence_transformers import SentenceTransformer

    base_dir = base_dir.resolve()
    if RAIZ.resolve() in base_dir.parents or base_dir == RAIZ.resolve():
        raise SystemExit(f"[PARADO] a base paralela precisa ficar FORA do repositório: {base_dir}")

    modelo = SentenceTransformer(MODELO_MULTILINGUE)
    dimensao = modelo.get_sentence_embedding_dimension()
    origem = documentos_de_producao()

    cliente = chromadb.PersistentClient(path=str(base_dir))
    try:
        cliente.delete_collection(COLECAO)
    except Exception:
        pass
    colecao = cliente.create_collection(name=COLECAO, metadata={"hnsw:space": "cosine"})
    vetores = modelo.encode(origem["documentos"]).tolist()
    colecao.add(ids=origem["ids"], embeddings=vetores,
                documents=origem["documentos"], metadatas=origem["metadados"])

    def buscar(pergunta, top_k):
        consulta = modelo.encode(pergunta).tolist()
        r = colecao.query(query_embeddings=[consulta], n_results=top_k,
                          include=["documents", "metadatas", "distances"])
        return [{"secao": m.get("secao", ""), "similaridade": round(1 - d, 4)}
                for m, d in zip(r["metadatas"][0], r["distances"][0])]

    info = {"modelo": MODELO_MULTILINGUE, "dimensao": dimensao,
            "dimensao_producao": origem["dimensao"],
            "base": f"paralela, fora do repositório: {base_dir}",
            "documentos_indexados": colecao.count()}
    return buscar, info


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--modelo", choices=("producao", "multilingue"), required=True)
    parser.add_argument("--base-dir", type=Path, default=None)
    args = parser.parse_args(argv)

    if args.modelo == "producao":
        buscar, info = buscador_producao()
    else:
        if args.base_dir is None:
            raise SystemExit("[PARADO] --base-dir é obrigatório no modo multilingue")
        buscar, info = buscador_multilingue(args.base_dir)
    print(json.dumps(info, ensure_ascii=False), flush=True)

    perguntas = json.loads((DIR / "perguntas.json").read_text(encoding="utf-8"))["perguntas"]
    inicio = datetime.now(timezone.utc).isoformat(timespec="seconds")
    resultados = []
    for p in perguntas:
        linha = {"id": p["id"], "categoria": p["categoria"], "pergunta": p["pergunta"]}
        for k in TOP_KS:
            t0 = time.perf_counter()
            ranking = buscar(p["pergunta"], k)
            linha[f"top{k}"] = [(t["secao"], t["similaridade"]) for t in ranking]
            linha[f"latencia_top{k}_s"] = round(time.perf_counter() - t0, 3)
        linha["top10_e_prefixo_do_top25"] = linha["top10"] == linha["top25"][:len(linha["top10"])]
        resultados.append(linha)
        print(f"{p['id']:3} max={linha['top25'][0][1]} top3={[s for s, _ in linha['top25'][:3]]} "
              f"prefixo_ok={linha['top10_e_prefixo_do_top25']}", flush=True)

    saida = {"gerado_em_utc": inicio, "modo": args.modelo, **info,
             "perguntas_fonte": "sprint4/avaliacao/perguntas.json", "resultados": resultados}
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = DIR / "execucoes" / f"rankings_{args.modelo}_{carimbo}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[rankings] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
