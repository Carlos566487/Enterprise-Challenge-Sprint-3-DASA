"""
Comparação de modelos locais (Ollama) — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Escolha do modelo substituto para a Parte B, por teste e não por suposição.
Cada candidato recebe o MESMO prompt real do sistema, pelo MESMO caminho de
produção (llm_connector.responder_com_llm → chamar_openai), com os mesmos
hiperparâmetros do conector; só o nome do modelo é trocado na fronteira pelo
instrumento_custo. Os trechos são os textos reais dos chunks, lidos da base
de produção, na composição que o limiar 0,43 entrega (rankings gravados).

Perguntas:
  R1  "Qual é o meu nível de risco para diabetes tipo 2?" — resposta direta;
      testa português e fidelidade.
  X2  "O meu relatório fala sobre risco de Parkinson?" com os trechos de
      Alzheimer — testa se o modelo admite que a informação não está lá.

Mede por chamada: latência, tokens (usage), finish_reason (truncamento),
RAM livre da máquina antes/depois e memória do processo do Ollama.

Uso (com OPENAI_BASE_URL e OPENAI_API_KEY apontando para o Ollama):
    python sprint4/avaliacao/comparar_modelos_locais.py qwen2.5:7b qwen2.5:3b ...
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]
for _c in (RAIZ, RAIZ / "sprint2" / "agente", RAIZ / "sprint2" / "interface", DIR):
    if str(_c) not in sys.path:
        sys.path.insert(0, str(_c))

CASOS = {
    "R1": {"pergunta": "Qual é o meu nível de risco para diabetes tipo 2?",
           "secoes": ["resultado_2.1", "recomendacao_2.1", "sumario"]},
    "X2": {"pergunta": "O meu relatório fala sobre risco de Parkinson?",
           "secoes": ["recomendacao_2.4", "resultado_2.4", "paciente"]},
}


def ram_livre_gb():
    import psutil
    return round(psutil.virtual_memory().available / 1e9, 2)


def ram_ollama_gb():
    """
    Memória privada dos processos instalados na pasta do Ollama (servidor e
    llama-server.exe, que executa o modelo). No Windows o RSS desses processos
    aparece perto de zero porque os pesos ficam mapeados ou na GPU; a memória
    privada é a medida que reflete o que eles retêm. A métrica que decide
    (RAM livre da máquina) é medida à parte.
    """
    import psutil
    total = 0
    for p in psutil.process_iter(["exe"]):
        if "ollama" in (p.info["exe"] or "").lower():
            try:
                total += p.memory_full_info().private
            except (psutil.Error, AttributeError):
                pass
    return round(total / 1e9, 2)


def ollama_ps() -> str:
    import subprocess
    exe = Path(os.environ["LOCALAPPDATA"]) / "Programs" / "Ollama" / "ollama.exe"
    return subprocess.run([str(exe), "ps"], capture_output=True, text=True).stdout.strip()


def main(argv=None) -> int:
    from dotenv import load_dotenv
    load_dotenv(DIR / ".env.avaliacao", override=True)
    if "11434" not in os.environ.get("OPENAI_BASE_URL", ""):
        raise SystemExit("[PARADO] OPENAI_BASE_URL não aponta para o Ollama (.env.avaliacao)")

    import chromadb
    import llm_connector
    from instrumento_custo import capturar_chamadas

    col = chromadb.PersistentClient(
        path=str(RAIZ / "sprint2" / "vetorial" / "base_vetorial")).get_collection("genera_relatorio")
    docs = col.get(include=["documents", "metadatas"])
    conteudo = {m["secao"]: d for m, d in zip(docs["metadatas"], docs["documents"])}

    modelos = (sys.argv[1:] if argv is None else argv)
    resultados = []
    for modelo in modelos:
        for cid, caso in CASOS.items():
            trechos = [conteudo[s] for s in caso["secoes"]]
            antes = ram_livre_gb()
            t0 = time.perf_counter()
            with capturar_chamadas(llm_connector, modelo) as registro:
                r = llm_connector.responder_com_llm(
                    pergunta=caso["pergunta"], trechos=trechos, modo="paciente",
                    api_key=os.environ["OPENAI_API_KEY"])
            dur = round(time.perf_counter() - t0, 2)
            chamada = registro.chamadas[0] if registro.chamadas else {}
            linha = {
                "modelo_pedido": modelo, "caso": cid, "pergunta": caso["pergunta"],
                "secoes": caso["secoes"], "status": r["status"],
                "modelo_respondido": chamada.get("modelo_respondido"),
                "endpoint": chamada.get("endpoint"),
                "modelo_pedido_pelo_conector": chamada.get("modelo_pedido_pelo_conector"),
                "parametros_enviados": chamada.get("parametros_enviados"),
                "finish_reason": chamada.get("finish_reason"),
                "usage": chamada.get("usage"), "latencia_s": dur,
                "ram_livre_antes_gb": antes, "ram_livre_depois_gb": ram_livre_gb(),
                "ram_processos_ollama_gb": ram_ollama_gb(), "ollama_ps": ollama_ps(),
                "resposta": r["resposta"],
            }
            resultados.append(linha)
            print(f"\n===== {modelo} · {cid} · {dur}s · finish={linha['finish_reason']} "
                  f"· tokens={(linha['usage'] or {}).get('completion_tokens')} "
                  f"· RAM livre {antes}→{linha['ram_livre_depois_gb']} GB · ollama {linha['ram_processos_ollama_gb']} GB",
                  flush=True)
            print(linha["ollama_ps"].splitlines()[-1] if linha["ollama_ps"] else "")
            print(r["resposta"], flush=True)

    saida = {"gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "nota": "comparação de candidatos; prompt e caminho de produção, modelo trocado na fronteira",
             "resultados": resultados}
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = DIR / "execucoes" / f"candidatos_ollama_{carimbo}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[candidatos] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
