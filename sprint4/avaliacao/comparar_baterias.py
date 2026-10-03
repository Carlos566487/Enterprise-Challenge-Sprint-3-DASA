"""
Comparativo de baterias de geração — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Lê duas análises produzidas por analisar_geracao.py (ex.: limiar 0,50 e
limiar 0,43) e gera a tabela lado a lado, por métrica e por pergunta. Não faz
chamada nenhuma: só lê arquivos de execuções/.

Uso:
    python sprint4/avaliacao/comparar_baterias.py \
        execucoes/analise_geracao_<ts>.json execucoes/analise_geracao_limiar043_<ts>.json
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]


def _ler(caminho):
    p = Path(caminho)
    if not p.is_absolute():
        p = DIR / p
    return json.loads(p.read_text(encoding="utf-8")), p


def por_pergunta(analise):
    tabela = defaultdict(lambda: {"execucoes": 0, "respondidas": 0, "ancoradas": 0,
                                  "sem_contexto": 0, "bloqueadas": 0,
                                  "valores_fora_da_base": 0, "scores": []})
    for r in analise["por_resposta"]:
        t = tabela[r["id"]]
        t["execucoes"] += 1
        if r["status"] == "respondido":
            t["respondidas"] += 1
            t["ancoradas"] += 1 if r["ancorado"] else 0
            t["scores"].append(r["score_sobreposicao"])
        elif r["status"] == "sem_contexto":
            t["sem_contexto"] += 1
        elif r["status"] == "bloqueado":
            t["bloqueadas"] += 1
        t["valores_fora_da_base"] += 1 if r["valores_fora_da_base_na_resposta"] else 0
    for t in tabela.values():
        s = t.pop("scores")
        t["score_medio"] = round(sum(s) / len(s), 4) if s else None
    return dict(tabela)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    (a, pa), (b, pb) = _ler(argv[0]), _ler(argv[1])
    metricas = ("execucoes", "chamadas_llm", "evitadas_guardrail", "evitadas_sem_contexto",
                "roteamento_correto")
    lado_a_lado = {m: {pa.name: a[m], pb.name: b[m]} for m in metricas}
    lado_a_lado["ancoragem"] = {pa.name: a["ancoragem"], pb.name: b["ancoragem"]}
    lado_a_lado["simplificacao"] = {pa.name: a["simplificacao"], pb.name: b["simplificacao"]}
    lado_a_lado["custo"] = {pa.name: {k: a["custo"][k] for k in ("tokens_entrada", "tokens_saida", "modelos_respondidos")},
                           pb.name: {k: b["custo"][k] for k in ("tokens_entrada", "tokens_saida", "modelos_respondidos")}}
    pp_a, pp_b = por_pergunta(a), por_pergunta(b)
    perguntas = sorted(set(pp_a) | set(pp_b))
    saida = {
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fontes": [str(pa.relative_to(RAIZ)).replace("\\", "/"), str(pb.relative_to(RAIZ)).replace("\\", "/")],
        "lado_a_lado": lado_a_lado,
        "por_pergunta": {pid: {pa.name: pp_a.get(pid), pb.name: pp_b.get(pid)} for pid in perguntas},
    }
    destino = DIR / "execucoes" / f"comparativo_baterias_{datetime.now():%Y%m%d_%H%M%S}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(lado_a_lado, ensure_ascii=False, indent=1))
    for pid in perguntas:
        print(pid, "|", pp_a.get(pid), "|", pp_b.get(pid))
    print(f"[comparativo] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
