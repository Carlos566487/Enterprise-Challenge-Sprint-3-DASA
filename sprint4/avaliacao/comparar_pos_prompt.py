"""
Antes × depois do ajuste de prompts.py (commit 75b2cfb) — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Compara, NO MESMO RECORTE (mesma pergunta, perfil e repetição, limiar 0,43),
os achados da revisão manual de antes (revisao_manual_achados.json, só os da
bateria geracao_limiar043_*) e de depois (revisao_manual_achados_pos_prompt.json),
agrupados nas 13 classes do catálogo (§12) + a classe nova encontrada depois.
Junta contagens mecânicas (busca de texto) que não dependem da leitura humana.
Não faz chamada nenhuma: só lê arquivos.

Uso:
    python sprint4/avaliacao/comparar_pos_prompt.py

Duas tabelas: (1) antes × v1 nas 36 respostas re-medidas; (2) antes × v1 × v2 nas
5 células re-medidas depois de mover a instrução de "Baseado em" (vazamento do
formato e contradição interna).
"""

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
EXEC = DIR / "execucoes"

ANTES = "execucoes/geracao_limiar043_20261002_215449.jsonl"
DEPOIS = [
    "execucoes/pos_prompt_a_limiar043_20261003_183841.jsonl",
    "execucoes/pos_prompt_b_limiar043_20261003_182820.jsonl",
    "execucoes/pos_prompt_c_limiar043_20261003_183154.jsonl",
]

# (tipo, subtipo) -> classe do catálogo §12. Subtipo None = qualquer subtipo.
CLASSES = [
    ("01 gene inventado", None),  # mecânica: HNF1A/KCNJ11
    ("02 contexto parcial tomado como todo", [("contagem_errada", "contexto_tomado_como_todo")]),
    ("03 inversão de sentido", [("inversao_de_sentido", None)]),
    ("04 nível de risco trocado", [("mistura_de_condicoes", "nivel_de_risco_trocado")]),
    ("05 recomendação de outra condição", [("mistura_de_condicoes", "recomendacao_de_outra_condicao")]),
    ("06 recomendação alterada", [("recomendacao_alterada", None)]),
    ("07 termo clínico trocado", [("termo_tecnico_trocado", "termo_clinico")]),
    ("08 SNP chamado de gene", [("termo_tecnico_trocado", "snp_chamado_de_gene")]),
    ("09 acréscimo incorreto", [("acrescimo", "incorreto")]),
    ("10 falsa tranquilização / inferência indevida", [("acrescimo", "inferencia_indevida")]),
    ("11 acréscimo de conhecimento geral", [("acrescimo", s) for s in (
        "conhecimento_geral", "exemplo_acrescentado", "recomendacao_acrescentada",
        "extrapolacao", "justificativa_inventada")]),
    ("12 contradição interna", [("contradicao_interna", None)]),
    ("13 ausência atribuída ao relatório", [("ausencia_atribuida_ao_relatorio", None)]),
    ("14 (nova) vazamento do formato do prompt", [("vazamento_de_formato", None)]),
]

RE_VAZAMENTO = re.compile(r"^\s*Resumo:\s*\n\s*\.\.\.", re.MULTILINE)


def _jsonl(rel):
    return [json.loads(l) for l in (DIR / rel).read_text(encoding="utf-8").splitlines() if l.strip()]


def _classe(achado):
    for nome, regras in CLASSES:
        for tipo, sub in regras or []:
            if achado["tipo"] == tipo and (sub is None or achado.get("subtipo") == sub):
                return nome
    return "outros (fora das 13 classes)"


def mecanicas(linhas):
    resp = [r for r in linhas if r.get("status") == "respondido"]
    texto = lambda r: r.get("resposta") or ""
    return {
        "respondidas": len(resp),
        "bloqueadas_ou_sem_contexto": len(linhas) - len(resp),
        "genes_HNF1A_KCNJ11": sum(1 for r in resp if re.search(r"HNF1A|KCNJ11", texto(r))),
        "hipoglicemica": sum(1 for r in resp if "hipoglicêmica" in texto(r).lower()),
        "vazamento_formato": sum(1 for r in resp if RE_VAZAMENTO.search(texto(r))),
        # "ancorado" gravado no jsonl NÃO entra: o antes foi pontuado pelo detector
        # antigo e o depois pelo corrigido (commit 7134677) — não é comparável.
    }


V2 = [
    "execucoes/pos_prompt_d_limiar043_20261003_185005.jsonl",
    "execucoes/pos_prompt_e_limiar043_20261003_185220.jsonl",
]
ACHADOS = {
    "antes": ("revisao_manual_achados.json", [ANTES]),
    "v1": ("revisao_manual_achados_pos_prompt.json", DEPOIS),
    "v2": ("revisao_manual_achados_pos_prompt_v2.json", V2),
}


def _chave(r):
    return (r["id"], r["perfil"], r["repeticao"])


def contar(versao, recorte):
    """Conta achados por classe da versão, restritos ao recorte, mais as mecânicas."""
    arq_achados, arquivos = ACHADOS[versao]
    linhas = [r for f in arquivos for r in _jsonl(f) if _chave(r) in recorte]
    assert len(linhas) == len(recorte), (versao, len(linhas), len(recorte))
    achados = [a for a in json.loads((DIR / arq_achados).read_text(encoding="utf-8"))["achados"]
               if a["arquivo"] in arquivos and _chave(a) in recorte]
    c = Counter(map(_classe, achados))
    m = mecanicas(linhas)
    c["01 gene inventado"] = m["genes_HNF1A_KCNJ11"]
    return c, m, len(achados)


def tabela(versoes, recorte):
    contagens = {v: contar(v, recorte) for v in versoes}
    linhas = []
    for nome in [c[0] for c in CLASSES] + ["outros (fora das 13 classes)"]:
        valores = {v: contagens[v][0].get(nome, 0) for v in versoes}
        a, d = valores[versoes[0]], valores[versoes[-1]]
        veredito = "igual" if a == d else ("melhorou" if d < a else "PIOROU")
        linhas.append({"classe": nome, **valores, "veredito_primeira_x_ultima": veredito})
    return {"respostas": len(recorte), "chaves": sorted(map(list, recorte)),
            "por_classe": linhas,
            "mecanicas": {v: contagens[v][1] for v in versoes},
            "achados_no_recorte": {v: contagens[v][2] for v in versoes}}


def _imprimir(titulo, t, versoes):
    print(f"\n{titulo}: {t['respostas']} respostas (mesma pergunta/perfil/repetição, limiar 0,43)")
    print(f"{'classe':50s} " + " ".join(f"{v:>6s}" for v in versoes))
    for l in t["por_classe"]:
        print(f"{l['classe']:50s} " + " ".join(f"{l[v]:6d}" for v in versoes)
              + f"  {l['veredito_primeira_x_ultima']}")
    for v in versoes:
        print(f"mecânicas {v}:", t["mecanicas"][v])


def main():
    recorte_v1 = {_chave(r) for f in DEPOIS for r in _jsonl(f)}
    recorte_v2 = {_chave(r) for f in V2 for r in _jsonl(f)}
    t1 = tabela(["antes", "v1"], recorte_v1)
    t2 = tabela(["antes", "v1", "v2"], recorte_v2)

    saida = {
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(),
        "versoes": {
            "antes": "prompts.py antes do fechamento (bateria geracao_limiar043)",
            "v1": "commit 75b2cfb — três ajustes; instrução de 'Baseado em' depois do bloco de formato",
            "v2": "instrução de 'Baseado em' movida para o item 4 da ordem, antes do bloco de formato",
        },
        "fontes": {v: [a] + arqs for v, (a, arqs) in ACHADOS.items()},
        "recorte_v1": t1,
        "recorte_v2": t2,
    }
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = EXEC / f"comparativo_pos_prompt_{ts}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")

    _imprimir("Recorte v1", t1, ["antes", "v1"])
    _imprimir("Recorte v2 (células re-medidas após mover a instrução)", t2, ["antes", "v1", "v2"])
    print(f"[comparar_pos_prompt] {destino.relative_to(DIR.parents[1])}")


if __name__ == "__main__":
    main()
