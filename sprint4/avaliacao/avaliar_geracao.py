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
    --limiar X         limiar de similaridade da busca (omitido = produção, 0,50).
                       A Parte B roda duas vezes: sem a flag e com o ótimo da
                       varredura (varrer_limiar.py).

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
import time
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
# Configuração do AMBIENTE DE AVALIAÇÃO (fora de produção, ignorada pelo git):
#   OPENAI_BASE_URL   — lido pelo próprio SDK; redireciona o cliente do conector
#   OPENAI_API_KEY    — o Ollama ignora, mas o SDK exige não vazia
#   AVALIACAO_MODELO  — nome trocado na fronteira pelo instrumento_custo
ENV_AVALIACAO = DIR / ".env.avaliacao"
N_PADRAO, N_CRITICA = 3, 5
PERFIS = ("leigo_ansioso", "leigo_curioso", "medico")


class SemChave(RuntimeError):
    pass


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def carregar_chave() -> str:
    """Carrega .env como o app faz e exige a chave. Nunca devolve vazio."""
    from dotenv import load_dotenv

    # O arquivo de avaliação tem prioridade; os .env de produção só preenchem
    # o que ele não definir. Sem ele, o comportamento é o de produção.
    if ENV_AVALIACAO.exists():
        load_dotenv(ENV_AVALIACAO, override=True)
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


def ambiente() -> dict:
    """Para onde a avaliação está apontada — gravado em toda saída e no cache."""
    return {"base_url": os.environ.get("OPENAI_BASE_URL") or "padrão do SDK (api.openai.com)",
            "modelo_substituto": os.environ.get("AVALIACAO_MODELO") or None}


def versao_codigo() -> dict:
    return {str(p.relative_to(RAIZ)).replace("\\", "/"):
            hashlib.sha256(p.read_bytes()).hexdigest()[:16] for p in ARQUIVOS_VERSIONADOS}


def chave_cache(pergunta_id: str, perfil: str, repeticao: int, versao: dict,
                limiar: float = None, amb: dict = None) -> str:
    bruto = json.dumps([pergunta_id, perfil, repeticao, versao, limiar, amb], sort_keys=True)
    return hashlib.sha256(bruto.encode("utf-8")).hexdigest()[:24]


def executar_uma(pergunta: dict, perfil: str, repeticao: int, api_key: str,
                 limiar: float = None) -> dict:
    """
    Uma execução real pelo caminho de produção, instrumentada.

    limiar=None usa a busca padrão do contrato (limiar de produção 0,50, sem
    injeção). Com limiar, a busca real é injetada via fn_buscar chamando
    buscar_contexto(similaridade_minima=limiar) — parâmetro já existente em
    buscar.py; nenhum arquivo de produção muda.
    """
    import llm_connector
    from instrumento_custo import capturar_chamadas
    from sprint3.integracao import responder_com_linguagem_simples
    from sprint3.rag_personalizacao import HistoricoMemoria

    extra = {}
    if limiar is not None:
        from sprint2.vetorial.buscar import buscar_contexto

        extra["fn_buscar"] = lambda texto, top_k: buscar_contexto(
            texto, top_k=top_k, similaridade_minima=limiar)

    inicio = _agora()
    t0 = time.perf_counter()
    with capturar_chamadas(llm_connector, ambiente()["modelo_substituto"]) as registro:
        r = responder_com_linguagem_simples(
            pergunta=pergunta["pergunta"], perfil=perfil,
            usuario_id=f"aval-{pergunta['id']}-{perfil}-{repeticao}",
            api_key=api_key, historico=HistoricoMemoria(), **extra,
        )
    primeira = registro.chamadas[0] if registro.chamadas else {}
    return {
        "id": pergunta["id"], "categoria": pergunta["categoria"],
        "pergunta": pergunta["pergunta"], "perfil": perfil, "repeticao": repeticao,
        "modelo_respondido": primeira.get("modelo_respondido"),
        "endpoint": primeira.get("endpoint"),
        "duracao_total_s": round(time.perf_counter() - t0, 2),
        "limiar_busca": limiar if limiar is not None else "producao",
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
                 "sdk_openai": _versao_sdk(), "ambiente": ambiente()}
    substituto = ambiente()["modelo_substituto"]
    trechos = ["Composição ancestral do paciente: Europa Ibérica (Península Ibérica): 42.3%."]
    registro = None
    try:
        with capturar_chamadas(llm_connector, substituto) as registro:
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
            "nao_truncada": bool(chamada) and chamada.get("finish_reason") != "length",
        }
        if substituto:
            # o modelo que a API diz ter respondido tem de ser o substituto
            provas["modelo_respondido_e_o_substituto"] = bool(
                chamada and (chamada["modelo_respondido"] or "").startswith(substituto.split(":")[0]))
        relatorio.update({"resultado": "ok" if all(provas.values()) else "suspeito",
                          "provas": provas, "chamada": chamada, "resposta": r["resposta"]})
    except Exception as erro:  # registra o erro exato, sem tentar consertar
        # O envoltório registra a chamada mesmo quando o SDK levanta erro: guarda
        # os parâmetros que o conector chegou a enviar (prova do lado do cliente).
        relatorio.update({"resultado": "falhou", "erro": f"{type(erro).__name__}: {erro}",
                          "chamada": registro.chamadas[0] if registro and registro.chamadas else None,
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


def plano(perguntas: list, piloto: int = None, ids: list = None,
          perfis: list = None, n_fixo: int = None) -> list:
    itens = []
    for p in perguntas:
        if ids and p["id"] not in ids:
            continue
        n = 1 if piloto else (n_fixo or (N_CRITICA if p["critica_n5"] else N_PADRAO))
        for perfil in (perfis or PERFIS):
            for rep in range(1, n + 1):
                itens.append((p, perfil, rep))
    return itens


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--piloto", type=int, default=None)
    parser.add_argument("--rotulo", default="geracao")
    parser.add_argument("--limiar", type=float, default=None,
                        help="limiar de similaridade da busca; omitido = produção (0,50)")
    parser.add_argument("--perguntas", default=None,
                        help="ids separados por vírgula (recorte reduzido); omitido = todas")
    parser.add_argument("--perfis", default=None, help="perfis separados por vírgula")
    parser.add_argument("--n", type=int, default=None, help="repetições fixas por pergunta")
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
    if args.limiar is not None:
        rotulo += f"_limiar{args.limiar:.2f}".replace(".", "")
    destino = DIR / "execucoes" / f"{rotulo}_{carimbo}.jsonl"

    amb = ambiente()
    print(f"[ambiente] {amb}", flush=True)
    ids = args.perguntas.split(",") if args.perguntas else None
    perfis = args.perfis.split(",") if args.perfis else None
    inicio_total = time.perf_counter()
    feitas_llm, reaproveitadas = 0, 0
    with open(destino, "w", encoding="utf-8") as saida:
        for pergunta, perfil, rep in plano(conjunto["perguntas"], args.piloto, ids, perfis, args.n):
            if args.piloto and feitas_llm >= args.piloto:
                break
            arquivo_cache = DIR_CACHE / f"{chave_cache(pergunta['id'], perfil, rep, versao, args.limiar, amb)}.json"
            if arquivo_cache.exists():
                linha = json.loads(arquivo_cache.read_text(encoding="utf-8"))
                reaproveitadas += 1
            else:
                linha = executar_uma(pergunta, perfil, rep, api_key, args.limiar)
                linha["versao_codigo"] = versao
                linha["ambiente"] = amb
                arquivo_cache.write_text(json.dumps(linha, ensure_ascii=False), encoding="utf-8")
            feitas_llm += 1 if linha["chamou_llm"] else 0
            saida.write(json.dumps(linha, ensure_ascii=False) + "\n")
            uso = linha["chamadas_sdk"][0]["usage"] if linha["chamadas_sdk"] else {}
            print(f"{linha['id']:3} {perfil:13} r{rep} {linha['status']:13} "
                  f"llm={linha['chamou_llm']} modelo={linha.get('modelo_respondido')} "
                  f"tokens={uso.get('total_tokens')} t={linha.get('duracao_total_s')}s", flush=True)

    print(f"[geracao] {destino.relative_to(RAIZ)}  chamadas_llm={feitas_llm} "
          f"reaproveitadas_do_cache={reaproveitadas} "
          f"tempo_total={round(time.perf_counter() - inicio_total, 1)}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
