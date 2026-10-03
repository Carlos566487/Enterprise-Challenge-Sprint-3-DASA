"""
Tamanho dos prompts da Parte B — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Reconstrói, sem chave e sem LLM, o prompt EXATO que cada chamada da Parte B
enviaria: pergunta personalizada (personalizador.montar_pergunta_personalizada)
+ contexto (agente_especialista.montar_contexto) + template
(agente_especialista.construir_prompt_final) — as mesmas funções que
llm_connector.responder_com_llm() usa. Os trechos vêm da execução bruta de
recuperação, não de uma busca nova.

Mede caracteres. Tokens ficam NÃO MEDIDOS: o tokenizador (tiktoken) não está
instalado neste ambiente, e o valor faturado vem do campo usage da API, que
o instrumento de custo registrará no piloto.

Uso:
    python sprint4/avaliacao/medir_prompts.py execucoes/recuperacao_<ts>.json
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]
for _c in (RAIZ, RAIZ / "sprint2" / "agente"):
    if str(_c) not in sys.path:
        sys.path.insert(0, str(_c))

from agente_especialista import construir_prompt_final, montar_contexto  # noqa: E402
from sprint3.rag_personalizacao import montar_pergunta_personalizada, obter_perfil  # noqa: E402


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    caminho = Path(argv[0])
    if not caminho.is_absolute():
        caminho = DIR / caminho
    bruto = json.loads(caminho.read_text(encoding="utf-8"))
    textos = {}
    for r in bruto["resultados"]:
        for perfil, dados in r["perfis"].items():
            textos[(r["id"], perfil)] = dados

    import chromadb
    col = chromadb.PersistentClient(
        path=str(RAIZ / "sprint2" / "vetorial" / "base_vetorial")
    ).get_collection("genera_relatorio")
    docs = col.get(include=["documents", "metadatas"])
    conteudo = {m["secao"]: d for m, d in zip(docs["metadatas"], docs["documents"])}

    conjunto = json.loads((DIR / "perguntas.json").read_text(encoding="utf-8"))
    linhas = []
    for p in conjunto["perguntas"]:
        for perfil in ("leigo_ansioso", "leigo_curioso", "medico"):
            dados = textos.get((p["id"], perfil))
            if not dados or not dados["trechos"]:
                continue
            trechos = [conteudo[s] for s, _ in dados["trechos"]]
            perfil_obj = obter_perfil(perfil)
            for continuidade in (False, True):
                pergunta = montar_pergunta_personalizada(
                    p["pergunta"], perfil_obj,
                    {"total_interacoes": 1} if continuidade else None,
                )
                prompt = construir_prompt_final(pergunta, montar_contexto(trechos), perfil_obj.modo)
                linhas.append({"id": p["id"], "perfil": perfil, "continuidade": continuidade,
                               "n_trechos": len(trechos), "caracteres": len(prompt)})

    tamanhos = [l["caracteres"] for l in linhas]
    saida = {
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fonte_trechos": str(caminho.relative_to(RAIZ)).replace("\\", "/"),
        "tokens": "NÃO MEDIDO — tiktoken ausente; o piloto mede via usage da API",
        "caracteres": {"min": min(tamanhos), "max": max(tamanhos),
                       "media": round(sum(tamanhos) / len(tamanhos), 1)},
        "prompts": linhas,
    }
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = DIR / "execucoes" / f"tamanho_prompts_{carimbo}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(saida["caracteres"], f"({len(linhas)} variações)")
    print(f"[prompts] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
