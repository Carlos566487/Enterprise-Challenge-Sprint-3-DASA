"""
Avaliação da camada de geração (Parte B) — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

EXIGE a chave da OpenAI. Sem chave, o script para — não existe modo
degradado: medir a resposta simulada seria medir um placeholder fixo.

Caminho medido (produção, sem atalhos):
    responder_com_linguagem_simples()          sprint3/integracao
      → responder_personalizado()              sprint3/rag_personalizacao
        → buscar_contexto()                    sprint2/vetorial (real)
        → responder_com_llm() → chamar_openai  sprint2/interface (real)
O SDK é envolvido pelo instrumento_custo (somente leitura): cada registro
guarda id, model e usage devolvidos pela OpenAI e os parâmetros enviados.

Modos:
    --preflight        uma chamada real mínima; valida o llm_connector com o
                       SDK instalado e prova que a resposta veio do modelo.
    --piloto K         K chamadas reais (1 repetição), para medir tokens por
                       chamada antes da bateria completa.
    (sem flag)         bateria completa: cada pergunta × 3 perfis × N
                       (N=3; N=5 nas críticas de perguntas.json).
    --rotulo NOME      prefixo do diretório de saída (ex.: pos_ajuste).

Isolamento das repetições: cada (pergunta, perfil, repetição) usa um
HistoricoMemoria novo. Sem isso, a 2ª repetição ganharia a diretiva de
continuidade e o prompt mudaria — a variação medida não seria só do modelo.

Cache em disco (execucoes/cache_geracao/): a chave inclui pergunta, perfil,
repetição e o hash de prompts.py, config_llm.py e llm_connector.py. Reexecutar
a análise não repete chamadas; mudar qualquer um desses arquivos invalida o
cache automaticamente, então o "depois" nunca reaproveita resposta do "antes".
"""

import argparse
import hashlib
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]
for _c in (RAIZ, RAIZ / "sprint2" / "agente", RAIZ / "sprint2" / "interface", DIR):
    if str(_c) not in sys.path:
        sys.path.insert(0, str(_c))

ARQUIVOS_VERSIONADOS = (
    RAIZ / "sprint2" / "agente" / "prompts.py",
    RAIZ / "sprint2" / "agente" / "config_llm.py",
    RAIZ / "sprint2" / "interface" / "llm_connector.py",
)
DIR_CACHE = DIR / "execucoes" / "cache_geracao"
N_PADRAO, N_CRITICA = 3, 5
PERFIS = ("leigo_ansioso", "leigo_curioso", "medico")


class SemChave(RuntimeError):
    pass


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def carregar_chave() -> str:
    """Carrega .env como o app faz e exige a chave. Nunca devolve vazio."""
    from dotenv import load_dotenv

    for env in (RAIZ / "sprint3" / "interface" / ".env", RAIZ / "sprint2" / "interface" / ".env"):
        if env.exists():
            load_dotenv(env, override=False)
    chave = os.environ.get("OPENAI_API_KEY", "").strip()
    if not chave:
        raise SemChave(
            "OPENAI_API_KEY ausente (ambiente, sprint2/interface/.env, sprint3/interface/.env). "
            "A Parte B não roda sem chave — não há modo degradado."
        )
    return chave


def versao_codigo() -> dict:
    return {str(p.relative_to(RAIZ)).replace("\\", "/"):
            hashlib.sha256(p.read_bytes()).hexdigest()[:16] for p in ARQUIVOS_VERSIONADOS}


def chave_cache(pergunta_id: str, perfil: str, repeticao: int, versao: dict) -> str:
    bruto = json.dumps([pergunta_id, perfil, repeticao, versao], sort_keys=True)
    return hashlib.sha256(bruto.encode("utf-8")).hexdigest()[:24]


def executar_uma(pergunta: dict, perfil: str, repeticao: int, api_key: str) -> dict:
    """Uma execução real pelo caminho de produção, instrumentada."""
    import llm_connector
    from instrumento_custo import capturar_chamadas
    from sprint3.integracao import responder_com_linguagem_simples
    from sprint3.rag_personalizacao import HistoricoMemoria

    inicio = _agora()
    with capturar_chamadas(llm_connector) as registro:
        r = responder_com_linguagem_simples(
            pergunta=pergunta["pergunta"], perfil=perfil,
            usuario_id=f"aval-{pergunta['id']}-{perfil}-{repeticao}",
            api_key=api_key, historico=HistoricoMemoria(),
        )
    return {
        "id": pergunta["id"], "categoria": pergunta["categoria"],
        "pergunta": pergunta["pergunta"], "perfil": perfil, "repeticao": repeticao,
        "timestamp_utc": inicio,
        "status": r["status"], "categoria_resposta": r["categoria"],
        "resposta": r["resposta"],
        "resposta_simplificada": r["resposta_simplificada"],
        "fontes": r["fontes"],
        "ancoragem": r["ancoragem"],
        "simplificacao": r["simplificacao"],
        "chamadas_sdk": registro.chamadas,
        "chamou_llm": len(registro.chamadas) > 0,
    }


def preflight(api_key: str, destino: Path) -> int:
    """Uma chamada real mínima pelo responder_com_llm, com prova de origem."""
    import llm_connector
    from agente_especialista import gerar_resposta_simulada
    from instrumento_custo import capturar_chamadas

    relatorio = {"gerado_em_utc": _agora(), "versao_codigo": versao_codigo(),
                 "sdk_openai": _versao_sdk()}
    trechos = ["Composição ancestral do paciente: Europa Ibérica (Península Ibérica): 42.3%."]
    try:
        with capturar_chamadas(llm_connector) as registro:
            r = llm_connector.responder_com_llm(
                pergunta="Qual é a minha ancestralidade?", trechos=trechos,
                modo="paciente", api_key=api_key,
            )
        chamada = registro.chamadas[0] if registro.chamadas else None
        simulada = gerar_resposta_simulada("").strip()
        provas = {
            "status_respondido": r["status"] == "respondido",
            "houve_chamada_sdk": chamada is not None,
            "id_resposta_presente": bool(chamada and chamada["id_resposta"]),
            "usage_presente": bool(chamada and chamada["usage"]["total_tokens"]),
            "modelo_respondido": chamada and chamada["modelo_respondido"],
            "difere_da_resposta_simulada": r["resposta"].strip() != simulada,
        }
        relatorio.update({"resultado": "ok" if all(provas.values()) else "suspeito",
                          "provas": provas, "chamada": chamada, "resposta": r["resposta"]})
    except Exception as erro:  # registra o erro exato, sem tentar consertar
        relatorio.update({"resultado": "falhou", "erro": f"{type(erro).__name__}: {erro}",
                          "traceback": traceback.format_exc()})
    destino.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: relatorio.get(k) for k in ("resultado", "provas", "erro")},
                     ensure_ascii=False, indent=2))
    print(f"[preflight] {destino.relative_to(RAIZ)}")
    return 0 if relatorio["resultado"] == "ok" else 1


def _versao_sdk():
    try:
        from importlib.metadata import version
        return version("openai")
    except Exception:
        return None


def plano(perguntas: list, piloto: int = None) -> list:
    itens = []
    for p in perguntas:
        n = 1 if piloto else (N_CRITICA if p["critica_n5"] else N_PADRAO)
        for perfil in PERFIS:
            for rep in range(1, n + 1):
                itens.append((p, perfil, rep))
    return itens


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--piloto", type=int, default=None)
    parser.add_argument("--rotulo", default="geracao")
    args = parser.parse_args(argv)

    try:
        api_key = carregar_chave()
    except SemChave as erro:
        print(f"[PARADO] {erro}")
        return 2

    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.preflight:
        return preflight(api_key, DIR / "execucoes" / f"preflight_{carimbo}.json")

    conjunto = json.loads((DIR / "perguntas.json").read_text(encoding="utf-8"))
    versao = versao_codigo()
    DIR_CACHE.mkdir(parents=True, exist_ok=True)

    rotulo = f"piloto{args.piloto}" if args.piloto else args.rotulo
    destino = DIR / "execucoes" / f"{rotulo}_{carimbo}.jsonl"

    feitas_llm, reaproveitadas = 0, 0
    with open(destino, "w", encoding="utf-8") as saida:
        for pergunta, perfil, rep in plano(conjunto["perguntas"], args.piloto):
            if args.piloto and feitas_llm >= args.piloto:
                break
            arquivo_cache = DIR_CACHE / f"{chave_cache(pergunta['id'], perfil, rep, versao)}.json"
            if arquivo_cache.exists():
                linha = json.loads(arquivo_cache.read_text(encoding="utf-8"))
                reaproveitadas += 1
            else:
                linha = executar_uma(pergunta, perfil, rep, api_key)
                linha["versao_codigo"] = versao
                arquivo_cache.write_text(json.dumps(linha, ensure_ascii=False), encoding="utf-8")
            feitas_llm += 1 if linha["chamou_llm"] else 0
            saida.write(json.dumps(linha, ensure_ascii=False) + "\n")
            uso = linha["chamadas_sdk"][0]["usage"] if linha["chamadas_sdk"] else {}
            print(f"{linha['id']:3} {perfil:13} r{rep} {linha['status']:13} "
                  f"llm={linha['chamou_llm']} tokens={uso.get('total_tokens')}", flush=True)

    print(f"[geracao] {destino.relative_to(RAIZ)}  chamadas_llm={feitas_llm} "
          f"reaproveitadas_do_cache={reaproveitadas}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
