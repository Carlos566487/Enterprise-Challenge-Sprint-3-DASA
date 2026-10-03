"""
Testes de MECANISMO do avaliar_geracao.py contra um duplo do SDK.

Nenhum teste chama a OpenAI nem mede qualidade: verificam que, quando a chave
existir, o script (1) recusa rodar sem chave, (2) registra id/model/usage de
cada chamada, (3) isola as repetições e (4) invalida o cache quando os
arquivos de prompt/config/conector mudam.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_DIR = Path(__file__).resolve().parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

import avaliar_geracao  # noqa: E402
import llm_connector  # noqa: E402
import sprint3.rag_personalizacao  # noqa: E402,F401  (põe o diretório do pacote no sys.path)
import personalizador  # noqa: E402  (módulo plano de sprint3/rag_personalizacao)

PERGUNTA = {"id": "T1", "categoria": "fato_direto", "critica_n5": False,
            "pergunta": "Qual é o meu nível de risco para diabetes tipo 2?"}
TRECHO = {"conteudo": "Condição: Diabetes Mellitus Tipo 2. Nível de risco: Alto.",
          "secao": "resultado_2.1", "fonte": "dados_estruturados.json", "similaridade": 0.69}


def _sdk_duplo(prompts_recebidos):
    class _Completions:
        def create(self, **kwargs):
            prompts_recebidos.append(kwargs["messages"][0]["content"])
            return SimpleNamespace(
                id="chatcmpl-duplo", model="duplo",
                usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5, total_tokens=15),
                choices=[SimpleNamespace(message=SimpleNamespace(
                    content="Seu nível de risco para Diabetes Mellitus Tipo 2 é Alto."))],
            )

    class _Cliente:
        def __init__(self, api_key=None):
            self.chat = SimpleNamespace(completions=_Completions())

    erro = type("E", (Exception,), {})
    return SimpleNamespace(OpenAI=_Cliente, OpenAIError=erro, AuthenticationError=erro,
                           RateLimitError=erro, APIConnectionError=erro)


@pytest.fixture(autouse=True)
def sem_ambiente_de_avaliacao(monkeypatch, tmp_path):
    """Isola os testes do .env.avaliacao real e das variáveis que ele define."""
    monkeypatch.setattr(avaliar_geracao, "ENV_AVALIACAO", tmp_path / "inexistente.env")
    for var in ("OPENAI_BASE_URL", "AVALIACAO_MODELO"):
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def ambiente(monkeypatch):
    prompts = []
    monkeypatch.setattr(llm_connector, "_openai_module", _sdk_duplo(prompts))
    monkeypatch.setattr(personalizador, "_buscar_padrao",
                        lambda pergunta, top_k: {"trechos": [TRECHO]})
    return prompts


def test_sem_chave_para_sem_modo_degradado(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(avaliar_geracao, "RAIZ", tmp_path)  # nenhum .env encontrado
    with pytest.raises(avaliar_geracao.SemChave):
        avaliar_geracao.carregar_chave()
    assert avaliar_geracao.main(["--piloto", "1"]) == 2


def test_execucao_registra_proveniencia_e_contrato(ambiente):
    linha = avaliar_geracao.executar_uma(PERGUNTA, "leigo_ansioso", 1, "sk-duplo")
    assert linha["status"] == "respondido"
    assert linha["chamou_llm"] is True
    chamada = linha["chamadas_sdk"][0]
    assert chamada["id_resposta"] == "chatcmpl-duplo"
    assert chamada["usage"]["total_tokens"] == 15
    assert chamada["parametros_enviados"]["model"] == llm_connector.MODELO
    assert linha["fontes"] == [TRECHO]
    assert linha["ancoragem"]["ancorado"] is True
    assert "resposta_simplificada" in linha and "simplificacao" in linha


def test_repeticoes_isoladas_enviam_prompt_identico(ambiente):
    for rep in (1, 2, 3):
        avaliar_geracao.executar_uma(PERGUNTA, "leigo_ansioso", rep, "sk-duplo")
    assert len(ambiente) == 3
    assert ambiente[0] == ambiente[1] == ambiente[2]
    assert "[Continuidade]" not in ambiente[0]


def test_guardrail_nao_chama_llm(ambiente):
    bloqueada = dict(PERGUNTA, id="T2", pergunta="Qual remédio devo tomar?")
    linha = avaliar_geracao.executar_uma(bloqueada, "medico", 1, "sk-duplo")
    assert linha["status"] == "bloqueado"
    assert linha["chamou_llm"] is False
    assert ambiente == []


def test_cache_invalida_quando_codigo_muda():
    versao = avaliar_geracao.versao_codigo()
    alterada = dict(versao)
    primeira = next(iter(alterada))
    alterada[primeira] = "0" * 16
    assert (avaliar_geracao.chave_cache("F1", "medico", 1, versao)
            != avaliar_geracao.chave_cache("F1", "medico", 1, alterada))
    assert (avaliar_geracao.chave_cache("F1", "medico", 1, versao)
            == avaliar_geracao.chave_cache("F1", "medico", 1, dict(versao)))


def test_plano_respeita_n_por_criticidade():
    perguntas = [dict(PERGUNTA, id="A", critica_n5=False), dict(PERGUNTA, id="B", critica_n5=True)]
    itens = avaliar_geracao.plano(perguntas)
    assert sum(1 for p, _, _ in itens if p["id"] == "A") == 3 * 3
    assert sum(1 for p, _, _ in itens if p["id"] == "B") == 3 * 5
    assert len(avaliar_geracao.plano(perguntas, piloto=10)) == 2 * 3


# ─────────────────────────────────────────────────────────────────────────────
# analisar_geracao.py — mecanismo sobre linhas no formato de avaliar_geracao
# ─────────────────────────────────────────────────────────────────────────────

import analisar_geracao  # noqa: E402

PERGUNTAS_ANALISE = {
    "R2": {"comportamento_esperado": "respondido", "fatos_esperados": ["Médio"],
           "fatos_fora_da_base": ["escore_poligênico_percentil = 67"]},
    "X1": {"comportamento_esperado": "sem_contexto", "fatos_esperados": [],
           "fatos_fora_da_base": []},
}


def _linha(pid, rep, status, resposta, ancorado, termos):
    return {"id": pid, "perfil": "medico", "repeticao": rep, "status": status,
            "resposta": resposta,
            "ancoragem": {"ancorado": ancorado, "score_sobreposicao": 0.5,
                          "termos_nao_ancorados": termos},
            "simplificacao": {"aplicada": False, "motivo": "perfil_tecnico"},
            "chamou_llm": status == "respondido",
            "chamadas_sdk": ([{"usage": {"prompt_tokens": 100, "completion_tokens": 20,
                                         "total_tokens": 120},
                               "modelo_respondido": "duplo",
                               "parametros_enviados": {"model": "m"}}]
                             if status == "respondido" else [])}


def test_analise_pega_valor_fora_da_base_e_mede_consistencia():
    linhas = [
        _linha("R2", 1, "respondido", "Risco Médio; percentil não consta.", True, []),
        _linha("R2", 2, "respondido", "Seu percentil é 67, risco Médio.", False, ["67"]),
        _linha("X1", 1, "sem_contexto", "Não encontrei.", None, []),
    ]
    r = analisar_geracao.analisar(linhas, PERGUNTAS_ANALISE, modelo=None)
    assert r["chamadas_llm"] == 2 and r["evitadas_sem_contexto"] == 1
    assert r["roteamento_correto"] == 3
    assert {k: r["ancoragem"][k] for k in ("respondidas", "ancoradas", "taxa",
                                           "score_sobreposicao_medio", "falsos_positivos_citacao")} == {
        "respondidas": 2, "ancoradas": 1, "taxa": 0.5,
        "score_sobreposicao_medio": 0.5, "falsos_positivos_citacao": 0}
    assert r["ancoragem"]["nao_ancoradas_por_outro_motivo"] == [
        {"id": "R2", "perfil": "medico", "repeticao": 2, "termos": ["67"]}]
    fora = r["valores_fora_da_base_apresentados"]
    assert [(f["id"], f["repeticao"], f["valores_fora_da_base_na_resposta"]) for f in fora] == [("R2", 2, ["67"])]
    r2 = next(c for c in r["consistencia_geracao"] if c["id"] == "R2")
    assert r2["ancoragem_estavel"] is False
    assert r2["similaridade_media"] is None  # sem modelo: não medido, nunca inventado
    assert r["custo"]["tokens_entrada"] == 200 and r["custo"]["usd"] is None


# ─────────────────────────────────────────────────────────────────────────────
# --limiar: Parte B nos dois limiares
# ─────────────────────────────────────────────────────────────────────────────

def test_limiar_injetado_chega_a_busca_real(ambiente, monkeypatch):
    chamadas = []

    def buscar_contexto_falso(pergunta, top_k=3, similaridade_minima=0.50):
        chamadas.append((top_k, similaridade_minima))
        return {"trechos": [TRECHO]}

    modulo = SimpleNamespace(buscar_contexto=buscar_contexto_falso)
    monkeypatch.setitem(sys.modules, "sprint2.vetorial.buscar", modulo)

    linha = avaliar_geracao.executar_uma(PERGUNTA, "leigo_curioso", 1, "sk-duplo", limiar=0.40)
    assert chamadas == [(4, 0.40)]          # top_k do perfil, limiar pedido
    assert linha["limiar_busca"] == 0.40


def test_sem_limiar_usa_busca_padrao_do_contrato(ambiente):
    linha = avaliar_geracao.executar_uma(PERGUNTA, "leigo_ansioso", 1, "sk-duplo")
    assert linha["limiar_busca"] == "producao"
    assert linha["fontes"] == [TRECHO]       # veio de personalizador._buscar_padrao (fixture)


def test_cache_separa_limiares():
    v = avaliar_geracao.versao_codigo()
    assert (avaliar_geracao.chave_cache("F1", "medico", 1, v, None)
            != avaliar_geracao.chave_cache("F1", "medico", 1, v, 0.40))


# ─────────────────────────────────────────────────────────────────────────────
# Troca de modelo na FRONTEIRA (avaliação com modelo local)
# ─────────────────────────────────────────────────────────────────────────────

def test_modelo_trocado_na_fronteira_com_registro_duplo(ambiente, monkeypatch):
    monkeypatch.setenv("AVALIACAO_MODELO", "modelo-local:7b")
    linha = avaliar_geracao.executar_uma(PERGUNTA, "medico", 1, "ollama")
    chamada = linha["chamadas_sdk"][0]
    assert chamada["modelo_pedido_pelo_conector"] == llm_connector.MODELO   # produção intacta
    assert chamada["parametros_enviados"]["model"] == "modelo-local:7b"     # o que saiu
    assert chamada["modelo_respondido"] == "duplo"                          # o que a API disse
    assert linha["modelo_respondido"] == "duplo"
    assert "finish_reason" in chamada


def test_sem_variaveis_de_avaliacao_nada_e_trocado(ambiente):
    linha = avaliar_geracao.executar_uma(PERGUNTA, "medico", 1, "sk-duplo")
    chamada = linha["chamadas_sdk"][0]
    assert chamada["parametros_enviados"]["model"] == llm_connector.MODELO
    assert avaliar_geracao.ambiente() == {"base_url": "padrão do SDK (api.openai.com)",
                                          "modelo_substituto": None}


def test_cache_separa_ambientes():
    v = avaliar_geracao.versao_codigo()
    local = {"base_url": "http://localhost:11434/v1", "modelo_substituto": "qwen2.5:7b"}
    assert (avaliar_geracao.chave_cache("F1", "medico", 1, v, 0.43, local)
            != avaliar_geracao.chave_cache("F1", "medico", 1, v, 0.43, None))


def test_plano_recorte_reduzido():
    perguntas = [dict(PERGUNTA, id=i, critica_n5=(i == "B")) for i in ("A", "B", "C")]
    itens = avaliar_geracao.plano(perguntas, ids=["A", "B"], perfis=["leigo_ansioso"], n_fixo=2)
    assert [(p["id"], perfil, rep) for p, perfil, rep in itens] == [
        ("A", "leigo_ansioso", 1), ("A", "leigo_ansioso", 2),
        ("B", "leigo_ansioso", 1), ("B", "leigo_ansioso", 2)]


def test_falso_positivo_de_citacao_so_quando_o_numero_esta_so_na_citacao():
    f = analisar_geracao.orfao_so_em_citacao
    assert f("1", "Risco Alto.\n\nBaseado em: [Fonte 1] e [Fonte 2]") is True
    assert f("1", "Baseado: Fonte 1") is True
    assert f("1", "Faça 1 exame por ano. Baseado em [Fonte 1]") is False   # número real fora da citação
    assert f("67", "percentil 67 [Fonte 1]") is False
    assert f("KCNJ11", "[Fonte 1] gene KCNJ11") is False                   # não numérico


def test_citacao_nao_conta_numero_dentro_de_outro_numero():
    f = analisar_geracao.orfao_so_em_citacao
    texto = "Europa do Sul: 18.7%; Ameríndio: 11.4%; Ásia: 1.2%.\nBaseado: [Fonte 1]"
    assert f("1", texto) is True
    assert f("1", "Nascido em 1985. [Fonte 1]") is True
    assert f("1", "1 vez ao ano. [Fonte 1]") is False


def test_citacao_em_lista():
    f = analisar_geracao.orfao_so_em_citacao
    assert f("4", "Baseado: [Fonte 1, 2, 3, 4]") is True
    assert f("2", "Baseado: [Fonte 1, Fonte 2]") is True
    assert f("2", "Baseado: Fonte 1 e Fonte 2") is True
    assert f("4", "Faça 4 refeições. [Fonte 1, 2, 3, 4]") is False
