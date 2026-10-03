"""
Passagem manual — acréscimos qualitativos — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Classe procurada: INFORMAÇÃO ACRESCENTADA que não está nos trechos recuperados
e que não envolve número, gene ou SNP. Ex. real do pré-voo: "países como
Espanha e Portugal" numa resposta sobre ancestralidade ibérica. ancoragem.py
não vê essa classe por construção (só compara números, SNPs e siglas de gene).

Dois passos:

  exportar   Gera um Markdown legível com, para cada resposta respondida, os
             trechos que a recuperação entregou e o texto da resposta — o
             material que a pessoa revisora lê.

  validar    Lê o arquivo de achados (revisao_manual_achados.json), escrito
             pela pessoa revisora, e CONFERE MECANICAMENTE cada citação: o
             trecho citado precisa existir literalmente na resposta gravada, e
             precisa NÃO existir nos trechos recuperados. Citação que falhar é
             rejeitada. Isso impede atribuir ao modelo algo que ele não
             escreveu, ou chamar de acréscimo algo que estava no contexto.

O julgamento ("isto é acréscimo e não paráfrase") é humano; a existência da
citação e a ausência nos trechos são verificadas por código.

Uso:
    python sprint4/avaliacao/revisao_manual.py exportar execucoes/<bateria>.jsonl
    python sprint4/avaliacao/revisao_manual.py validar revisao_manual_achados.json
"""

import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]


def _norm(texto: str) -> str:
    base = unicodedata.normalize("NFC", texto or "").lower()
    return re.sub(r"\s+", " ", base).strip()


def _carregar(caminho: str) -> list:
    p = Path(caminho)
    if not p.is_absolute():
        p = DIR / p
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()], p


def exportar(caminho: str) -> int:
    linhas, p = _carregar(caminho)
    partes = [f"# Revisão manual — {p.name}\n",
              "Para cada resposta: trechos entregues ao modelo e a resposta. Procurar "
              "informação acrescentada que não esteja nos trechos e que não seja número/gene/SNP.\n"]
    por_pergunta = defaultdict(list)
    for l in linhas:
        if l["status"] == "respondido":
            por_pergunta[l["id"]].append(l)
    for pid in sorted(por_pergunta):
        itens = por_pergunta[pid]
        partes.append(f"\n## {pid} — {itens[0]['pergunta']}\n")
        vistos = set()
        for l in itens:
            chave = tuple(f["secao"] for f in l["fontes"])
            if chave not in vistos:
                vistos.add(chave)
                partes.append(f"**Trechos ({l['perfil']}):**\n")
                for f in l["fontes"]:
                    partes.append(f"- `{f['secao']}`: {f['conteudo']}\n")
            partes.append(f"\n### {pid} · {l['perfil']} · r{l['repeticao']} · modelo={l.get('modelo_respondido')}\n")
            partes.append("```\n" + (l["resposta"] or "") + "\n```\n")
    destino = DIR / "execucoes" / f"revisao_material_{p.stem}.md"
    destino.write_text("".join(partes), encoding="utf-8")
    print(f"[exportar] {destino.relative_to(RAIZ)}  respostas={sum(len(v) for v in por_pergunta.values())}")
    return 0


def validar(caminho_achados: str) -> int:
    p = Path(caminho_achados)
    if not p.is_absolute():
        p = DIR / p
    doc = json.loads(p.read_text(encoding="utf-8"))
    cache_baterias = {}
    aceitos, rejeitados = [], []
    for a in doc["achados"]:
        if a["arquivo"] not in cache_baterias:
            cache_baterias[a["arquivo"]] = _carregar(a["arquivo"])[0]
        linha = next((l for l in cache_baterias[a["arquivo"]]
                      if l["id"] == a["id"] and l["perfil"] == a["perfil"]
                      and l["repeticao"] == a["repeticao"]), None)
        motivo = None
        if linha is None:
            motivo = "resposta não encontrada no arquivo"
        elif _norm(a["citacao"]) not in _norm(linha["resposta"]):
            motivo = "citação não existe literalmente na resposta gravada"
        elif any(_norm(a["citacao"]) in _norm(f["conteudo"]) for f in linha["fontes"]):
            motivo = "citação aparece nos trechos recuperados — não é acréscimo"
        registro = {**a, "secoes_recuperadas": [f["secao"] for f in linha["fontes"]] if linha else None}
        (rejeitados if motivo else aceitos).append({**registro, "motivo_rejeicao": motivo} if motivo else registro)

    respondidas = sum(1 for linhas in cache_baterias.values() for l in linhas if l["status"] == "respondido")
    resumo = {
        "respostas_respondidas_revisadas": respondidas,
        "achados_aceitos": len(aceitos),
        "achados_rejeitados_pela_verificacao": len(rejeitados),
        "respostas_com_acrescimo": len({(a["arquivo"], a["id"], a["perfil"], a["repeticao"]) for a in aceitos}),
        "por_pergunta": dict(Counter(a["id"] for a in aceitos)),
        "por_tipo": dict(Counter(a["tipo"] for a in aceitos)),
    }
    saida = {"gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "fonte_achados": p.name, "revisor": doc.get("revisor"), "criterio": doc.get("criterio"),
             "resumo": resumo, "aceitos": aceitos, "rejeitados": rejeitados}
    destino = DIR / "execucoes" / f"revisao_manual_validada_{datetime.now():%Y%m%d_%H%M%S}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=1))
    for r in rejeitados:
        print("REJEITADO:", r["id"], r["perfil"], r["repeticao"], "|", r["motivo_rejeicao"], "|", r["citacao"][:80])
    print(f"[validar] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("exportar", "validar"):
        print(__doc__)
        sys.exit(2)
    sys.exit(exportar(sys.argv[2]) if sys.argv[1] == "exportar" else validar(sys.argv[2]))
