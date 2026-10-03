"""
Re-medição do adaptador de simplificação sobre respostas JÁ GRAVADAS
Sprint 4 / Genera AI / Dasa — Engenheiro de IA & PLN

Reexecuta responder_com_linguagem_simples() com o código ATUAL de
sprint3/integracao/adaptador_nlp.py (e o simplificador real da Tayná, não
alterado), alimentando a busca com os trechos gravados e o "LLM" com a
resposta gravada. Assim só a etapa de simplificação muda; nenhuma chamada
nova ao modelo. Compara com o que foi gravado na hora da geração.

Mede: simplificação aplicada, motivos, marcações de quebra de ancoragem e
preservação da formatação (quebras de linha) no texto exibido.

Uso:
    python sprint4/avaliacao/readaptar.py
"""

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from sprint3.integracao import responder_com_linguagem_simples  # noqa: E402
from sprint3.rag_personalizacao import HistoricoMemoria  # noqa: E402

BATERIAS = {
    "0,43": "execucoes/geracao_limiar043_20261002_215449.jsonl",
    "0,50": "execucoes/geracao_20261003_133602.jsonl",
}


def _formatacao_perdida(original: str, exibido: str) -> bool:
    return "\n" in original and "\n" not in exibido


def _palavra_trocada(original: str, exibido: str) -> bool:
    return " ".join(original.split()) != " ".join(exibido.split())


def resumir(linhas, campo_simpl, campo_exibido):
    elegiveis = [l for l in linhas if l["status"] == "respondido" and l["perfil"] != "medico"]
    aplicadas = [l for l in elegiveis if l[campo_simpl]["aplicada"]]
    return {
        "elegiveis": len(elegiveis),
        "aplicada": len(aplicadas),
        "motivos": dict(Counter(l[campo_simpl]["motivo"] for l in elegiveis)),
        "quebrou_ancoragem": sum(1 for l in elegiveis if l[campo_simpl]["motivo"] == "quebrou_ancoragem"),
        "exibidas_sem_formatacao": sum(1 for l in elegiveis if _formatacao_perdida(l["resposta"], l[campo_exibido])),
        "exibidas_com_palavra_trocada": sum(1 for l in elegiveis if _palavra_trocada(l["resposta"], l[campo_exibido])),
    }


def main() -> int:
    saida = {"gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "adaptador": "sprint3/integracao/adaptador_nlp.py (versão atual)", "baterias": {}}
    for nome, arq in BATERIAS.items():
        linhas = [json.loads(x) for x in (DIR / arq).read_text(encoding="utf-8").splitlines() if x.strip()]
        for l in linhas:
            if l["status"] != "respondido":
                continue
            fontes = l["fontes"]
            r = responder_com_linguagem_simples(
                pergunta=l["pergunta"], perfil=l["perfil"], usuario_id="readaptar",
                api_key="nao-usada", historico=HistoricoMemoria(),
                fn_buscar=lambda p, k, f=fontes: {"trechos": f},
                fn_llm=lambda p, t, m, a, resp=l["resposta"]: {
                    "status": "respondido", "resposta": resp, "categoria": "resposta_rag"},
            )
            l["simplificacao_nova"] = r["simplificacao"]
            l["exibido_novo"] = r["resposta_simplificada"]
        resp = [l for l in linhas if l["status"] == "respondido"]
        saida["baterias"][nome] = {
            "arquivo": arq,
            "antes": resumir(resp, "simplificacao", "resposta_simplificada"),
            "depois": resumir(resp, "simplificacao_nova", "exibido_novo"),
            "quebras_depois": [{"id": l["id"], "perfil": l["perfil"], "repeticao": l["repeticao"],
                                "termos_introduzidos": l["simplificacao_nova"].get("termos_nao_ancorados")}
                               for l in resp if l["perfil"] != "medico"
                               and l["simplificacao_nova"]["motivo"] == "quebrou_ancoragem"],
        }
    destino = DIR / "execucoes" / f"readaptacao_{datetime.now():%Y%m%d_%H%M%S}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    for nome, b in saida["baterias"].items():
        print(f"== {nome}\n antes : {b['antes']}\n depois: {b['depois']}\n quebras: {b['quebras_depois']}")
    print(f"[readaptacao] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
