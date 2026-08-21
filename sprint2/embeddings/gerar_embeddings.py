"""
Gerador de Embeddings — Sprint 2 / Genera / Dasa
Lê o dados_estruturados.json do Sprint 1, divide em chunks e gera embeddings.
"""

import json
import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer

# ── Caminhos ──────────────────────────────────────────────────────────────────
RAIZ = Path(__file__).resolve().parents[2]
JSON_ENTRADA = RAIZ / "dados_estruturados.json"
JSON_SAIDA = Path(__file__).parent / "chunks.json"

MODELO_NOME = "all-MiniLM-L6-v2"


def carregar_relatorio(caminho: Path) -> dict:
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def gerar_chunks(relatorio: dict) -> list[dict]:
    """Divide o relatório em chunks semânticos com metadados."""
    chunks = []
    idx = 0

    # ── Paciente ──────────────────────────────────────────────────────────────
    p = relatorio.get("paciente", {})
    chunks.append({
        "id": f"chunk_{idx:03d}",
        "secao": "paciente",
        "fonte": "dados_estruturados.json > paciente",
        "conteudo": (
            f"Paciente: {p.get('nome', '')}. "
            f"Data de nascimento: {p.get('data_nascimento', '')}. "
            f"ID do relatório: {p.get('id_relatorio', '')}. "
            f"Data do exame: {p.get('data_exame', '')}. "
            f"Médico solicitante: {p.get('medico_solicitante', '')}."
        )
    })
    idx += 1

    # ── Sumário ───────────────────────────────────────────────────────────────
    s = relatorio.get("sumario", {})
    chunks.append({
        "id": f"chunk_{idx:03d}",
        "secao": "sumario",
        "fonte": "dados_estruturados.json > sumario",
        "conteudo": (
            f"Resumo do relatório genético: {s.get('resumo_executivo_paciente', '')} "
            f"Total de condições analisadas: {s.get('total_condicoes_analisadas', '')}. "
            f"Condições de risco alto: {s.get('condicoes_alto_risco', '')}. "
            f"Condições de risco médio: {s.get('condicoes_medio_risco', '')}. "
            f"Condições de risco baixo: {s.get('condicoes_baixo_risco', '')}. "
            f"Recomendações prioritárias: {'; '.join(s.get('recomendacoes_prioritarias', []))}."
        )
    })
    idx += 1

    # ── Resultados — um chunk por condição ────────────────────────────────────
    for resultado in relatorio.get("resultados", []):
        doenca = resultado.get("doenca", "")
        risco = resultado.get("risco", "")
        categoria = resultado.get("categoria", "")

        # Chunk de descrição simples + impacto (para paciente)
        chunks.append({
            "id": f"chunk_{idx:03d}",
            "secao": f"resultado_{resultado.get('id', '')}",
            "fonte": f"dados_estruturados.json > resultados > {doenca}",
            "conteudo": (
                f"Condição: {doenca}. Categoria: {categoria}. Nível de risco: {risco}. "
                f"{resultado.get('descricao_simples', '')} "
                f"{resultado.get('impacto_pratico', '')}"
            )
        })
        idx += 1

        # Chunk de recomendação + urgência
        chunks.append({
            "id": f"chunk_{idx:03d}",
            "secao": f"recomendacao_{resultado.get('id', '')}",
            "fonte": f"dados_estruturados.json > resultados > {doenca} > recomendacao",
            "conteudo": (
                f"Recomendação para {doenca} (risco {risco}): "
                f"{resultado.get('recomendacao', '')} "
                f"Urgência: {resultado.get('urgencia_medica', '')}."
            )
        })
        idx += 1

        # Chunk técnico com marcadores (para médico / busca detalhada)
        marcadores = resultado.get("marcadores_geneticos", [])
        marcadores_txt = "; ".join(
            f"{m.get('id_snp','')} ({m.get('gene','')}) alelo {m.get('alelo','')} — {m.get('observacao','')}"
            for m in marcadores
        )
        if marcadores_txt:
            chunks.append({
                "id": f"chunk_{idx:03d}",
                "secao": f"marcadores_{resultado.get('id', '')}",
                "fonte": f"dados_estruturados.json > resultados > {doenca} > marcadores_geneticos",
                "conteudo": (
                    f"Marcadores genéticos para {doenca}: {marcadores_txt}. "
                    f"Descrição técnica: {resultado.get('descricao_tecnica', '')}"
                )
            })
            idx += 1

    # ── Ancestralidade ────────────────────────────────────────────────────────
    anc_lista = relatorio.get("ancestralidade", [])
    if anc_lista:
        anc_txt = "; ".join(
            f"{a.get('regiao', '')}: {a.get('percentual', '')}%"
            for a in anc_lista
        )
        chunks.append({
            "id": f"chunk_{idx:03d}",
            "secao": "ancestralidade",
            "fonte": "dados_estruturados.json > ancestralidade",
            "conteudo": f"Composição ancestral do paciente: {anc_txt}."
        })
        idx += 1

    # ── Metadados ─────────────────────────────────────────────────────────────
    meta = relatorio.get("metadata", {})
    chunks.append({
        "id": f"chunk_{idx:03d}",
        "secao": "metadata",
        "fonte": "dados_estruturados.json > metadata",
        "conteudo": (
            f"Relatório emitido pelo laboratório {meta.get('laboratorio', '')}. "
            f"Responsável técnico: {meta.get('responsavel_tecnico', '')} ({meta.get('crm_responsavel', '')}). "
            f"Versão do relatório: {meta.get('versao_relatorio', '')}. "
            f"Data de processamento: {meta.get('data_processamento', '')}."
        )
    })

    return chunks


def gerar_embeddings(chunks: list[dict], modelo: SentenceTransformer) -> list[dict]:
    print(f"  Gerando embeddings para {len(chunks)} chunks...")
    textos = [c["conteudo"] for c in chunks]
    vetores_raw = modelo.encode(textos, show_progress_bar=True)
    vetores = [v.tolist() for v in vetores_raw]
    for chunk, vetor in zip(chunks, vetores):
        chunk["embedding"] = vetor
    return chunks


def main(caminho_json: Path = JSON_ENTRADA):
    print("=" * 60)
    print("GERADOR DE EMBEDDINGS — Sprint 2 / Genera")
    print("=" * 60)

    if not caminho_json.exists():
        print(f"[ERRO] Arquivo não encontrado: {caminho_json}")
        sys.exit(1)

    print(f"\n[1/4] Carregando relatório: {caminho_json}")
    relatorio = carregar_relatorio(caminho_json)

    print("[2/4] Dividindo em chunks semânticos...")
    chunks = gerar_chunks(relatorio)
    print(f"      {len(chunks)} chunks gerados.")

    print(f"[3/4] Carregando modelo de embeddings: {MODELO_NOME}")
    modelo = SentenceTransformer(MODELO_NOME)

    print("[4/4] Gerando embeddings...")
    chunks_com_embeddings = gerar_embeddings(chunks, modelo)

    JSON_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_SAIDA, "w", encoding="utf-8") as f:
        json.dump(chunks_com_embeddings, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] chunks.json salvo em: {JSON_SAIDA}")
    print(f"     Total de chunks: {len(chunks_com_embeddings)}")
    print(
        f"     Dimensão dos embeddings: {len(chunks_com_embeddings[0]['embedding'])}")
    return chunks_com_embeddings


if __name__ == "__main__":
    entrada = Path(sys.argv[1]) if len(sys.argv) > 1 else JSON_ENTRADA
    main(entrada)
