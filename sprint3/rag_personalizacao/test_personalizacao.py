"""
Testes da Camada de Personalização — Sprint 3 / Genera AI / Dasa
Cientista de IA — Personalização & RAG

Executar:
    pytest sprint3/rag_personalizacao/ -v

Estes testes NÃO exigem OPENAI_API_KEY nem a base vetorial construída:
a busca e o LLM são injetados por fakes (fn_buscar / fn_llm). O único teste
que usa a base vetorial real é marcado com skip automático quando ela não
existe, para não quebrar o CI.
"""

import sys
from pathlib import Path

import pytest

_DIR = Path(__file__).resolve().parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

from ancoragem import extrair_fatos, validar_ancoragem       # noqa: E402
from historico import HistoricoJSON, HistoricoMemoria        # noqa: E402
from perfis import PERFIS, obter_perfil, validar_diretivas   # noqa: E402
from personalizador import (                                 # noqa: E402
    VERSAO_CONTRATO,
    montar_pergunta_personalizada,
    responder_personalizado,
)

RAIZ = _DIR.parents[1]


# ─────────────────────────────────────────────────────────────────────────────
# FAKES
# ─────────────────────────────────────────────────────────────────────────────

TRECHOS_FAKE = [
    {
        "conteudo": (
            "Condição: Diabetes Mellitus Tipo 2. Categoria: Metabolismo. "
            "Nível de risco: Alto. Seu DNA indica uma chance maior de "
            "desenvolver diabetes tipo 2 ao longo da vida."
        ),
        "secao": "resultado_2.1",
        "fonte": "dados_estruturados.json > resultados > Diabetes",
        "similaridade": 0.62,
    },
    {
        "conteudo": (
            "Marcadores genéticos para Diabetes Mellitus Tipo 2: "
            "RS7903146 (TCF7L2) alelo T/T. Escore poligênico percentil 89."
        ),
        "secao": "marcadores_2.1",
        "fonte": "dados_estruturados.json > resultados > Diabetes > marcadores",
        "similaridade": 0.57,
    },
]


class BuscaFake:
    """Substitui buscar_contexto() registrando como foi chamada."""

    def __init__(self, trechos=None):
        self.trechos = TRECHOS_FAKE if trechos is None else trechos
        self.chamadas = []

    def __call__(self, pergunta, top_k):
        self.chamadas.append({"pergunta": pergunta, "top_k": top_k})
        return {
            "pergunta": pergunta,
            "encontrou_contexto": bool(self.trechos),
            "trechos": self.trechos[:top_k],
            "contexto": " ".join(t["conteudo"] for t in self.trechos[:top_k]),
        }


class LLMFake:
    """
    Substitui responder_com_llm() devolvendo uma resposta ancorada nos trechos.

    Registra as chamadas para permitir asserções sobre economia de tokens
    (guardrail deve impedir que o LLM seja chamado).
    """

    def __init__(self, resposta=None, status="respondido"):
        self.resposta = resposta
        self.status = status
        self.chamadas = []

    def __call__(self, pergunta, trechos, modo, api_key):
        self.chamadas.append({
            "pergunta": pergunta,
            "trechos": trechos,
            "modo": modo,
            "api_key": api_key,
        })
        resposta = self.resposta
        if resposta is None:
            resposta = (
                "Resumo:\nSeu relatório indica risco Alto para Diabetes "
                "Mellitus Tipo 2.\n\nBaseado em: relatório genético."
            )
        return {
            "status": self.status,
            "resposta": resposta,
            "fontes": trechos,
            "categoria": "resposta_rag" if self.status == "respondido" else "bloqueado",
        }


# ─────────────────────────────────────────────────────────────────────────────
# 1. PERFIS E REGRAS DE PERSONALIZAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def test_tres_perfis_suportados():
    assert set(PERFIS) == {"leigo_ansioso", "leigo_curioso", "medico"}


def test_mapeamento_perfil_para_modo_do_agente():
    assert obter_perfil("leigo_ansioso").modo == "paciente"
    assert obter_perfil("leigo_curioso").modo == "paciente"
    assert obter_perfil("medico").modo == "tecnico"


def test_perfil_desconhecido_falha_explicitamente():
    with pytest.raises(ValueError, match="Perfil desconhecido"):
        responder_personalizado(pergunta="Tenho risco?", perfil="astrologo")


def test_diretivas_nao_contem_termos_de_guardrail():
    """
    Regressão crítica: se uma diretiva contiver um termo de guardrail, toda
    pergunta personalizada passa a ser bloqueada por falso positivo.
    """
    resultado = validar_diretivas()
    assert resultado["valido"], f"Diretivas violando guardrails: {resultado['violacoes']}"


def test_personalizacao_nao_altera_veredito_do_guardrail():
    """A diretiva anexada não pode transformar pergunta legítima em bloqueada."""
    from guardrails import verificar_guardrails

    pergunta = "O que meu relatório diz sobre ancestralidade?"
    veredito_cru = verificar_guardrails(pergunta)

    for perfil_id in PERFIS:
        personalizada = montar_pergunta_personalizada(
            pergunta=pergunta,
            perfil=obter_perfil(perfil_id),
            resumo_historico={"total_interacoes": 3},
        )
        veredito = verificar_guardrails(personalizada)
        assert veredito["permitido"] == veredito_cru["permitido"] is True


# ─────────────────────────────────────────────────────────────────────────────
# 2. OS TRÊS PERFIS DE USUÁRIO
# ─────────────────────────────────────────────────────────────────────────────

def test_perfil_leigo_ansioso():
    busca, llm = BuscaFake(), LLMFake()
    resultado = responder_personalizado(
        pergunta="Eu tenho risco de diabetes?",
        perfil="leigo_ansioso",
        usuario_id="u1",
        api_key="fake",
        fn_buscar=busca,
        fn_llm=llm,
    )
    assert resultado["status"] == "respondido"
    assert resultado["perfil"] == "leigo_ansioso"
    assert resultado["modo_efetivo"] == "paciente"
    assert busca.chamadas[0]["top_k"] == 3
    assert "calmo e acolhedor" in llm.chamadas[0]["pergunta"]


def test_perfil_leigo_curioso():
    busca, llm = BuscaFake(), LLMFake()
    resultado = responder_personalizado(
        pergunta="Por que eu tenho essa predisposição?",
        perfil="leigo_curioso",
        usuario_id="u2",
        api_key="fake",
        fn_buscar=busca,
        fn_llm=llm,
    )
    assert resultado["modo_efetivo"] == "paciente"
    assert busca.chamadas[0]["top_k"] == 4
    assert "mecanismo biológico" in llm.chamadas[0]["pergunta"]


def test_perfil_medico():
    busca, llm = BuscaFake(), LLMFake()
    resultado = responder_personalizado(
        pergunta="Quais marcadores sustentam esse escore?",
        perfil="medico",
        usuario_id="u3",
        api_key="fake",
        fn_buscar=busca,
        fn_llm=llm,
    )
    assert resultado["modo_efetivo"] == "tecnico"
    assert busca.chamadas[0]["top_k"] == 5
    assert "linguagem técnica" in llm.chamadas[0]["pergunta"]


def test_perfis_recebem_os_mesmos_fatos():
    """
    Personalização muda a FORMA, nunca o CONTEÚDO: os três perfis devem
    receber exatamente os mesmos trechos factuais do relatório.
    """
    fatos_por_perfil = {}
    for perfil_id in PERFIS:
        busca, llm = BuscaFake(), LLMFake()
        responder_personalizado(
            pergunta="Eu tenho risco de diabetes?",
            perfil=perfil_id,
            usuario_id=f"u-{perfil_id}",
            api_key="fake",
            fn_buscar=busca,
            fn_llm=llm,
        )
        contexto = " ".join(llm.chamadas[0]["trechos"])
        fatos = extrair_fatos(contexto)
        fatos_por_perfil[perfil_id] = (
            fatos["snps"], fatos["genes"], fatos["numeros"],
        )

    valores = list(fatos_por_perfil.values())
    assert all(v == valores[0] for v in valores), fatos_por_perfil


# ─────────────────────────────────────────────────────────────────────────────
# 3. PERGUNTA FORA DO ESCOPO / GUARDRAILS
# ─────────────────────────────────────────────────────────────────────────────

def test_pergunta_fora_do_escopo_e_bloqueada_sem_gastar_token():
    busca, llm = BuscaFake(), LLMFake()
    resultado = responder_personalizado(
        pergunta="Qual dieta para emagrecer devo seguir?",
        perfil="leigo_curioso",
        usuario_id="u4",
        api_key=None,
        fn_buscar=busca,
        fn_llm=llm,
    )
    assert resultado["status"] == "bloqueado"
    assert resultado["categoria"] == "fora_escopo"
    assert resultado["fontes"] == []
    assert llm.chamadas == [], "LLM não deveria ser chamado em pergunta bloqueada"
    assert busca.chamadas == [], "Busca não deveria rodar em pergunta bloqueada"


def test_pergunta_de_prescricao_e_bloqueada():
    busca, llm = BuscaFake(), LLMFake()
    resultado = responder_personalizado(
        pergunta="Qual remédio devo tomar para isso?",
        perfil="leigo_ansioso",
        usuario_id="u5",
        api_key=None,
        fn_buscar=busca,
        fn_llm=llm,
    )
    assert resultado["status"] == "bloqueado"
    assert resultado["categoria"] == "prescricao"
    assert llm.chamadas == []


def test_sem_contexto_quando_busca_nao_retorna_trechos():
    busca, llm = BuscaFake(trechos=[]), LLMFake()
    resultado = responder_personalizado(
        pergunta="O relatório fala sobre minha altura?",
        perfil="leigo_curioso",
        usuario_id="u6",
        api_key="fake",
        fn_buscar=busca,
        fn_llm=llm,
    )
    assert resultado["status"] == "sem_contexto"
    assert llm.chamadas == []


# ─────────────────────────────────────────────────────────────────────────────
# 4. VALIDAÇÃO DE ANCORAGEM (requisito: não extrapolar o relatório)
# ─────────────────────────────────────────────────────────────────────────────

def test_ancoragem_aprova_resposta_fiel():
    trechos = [t["conteudo"] for t in TRECHOS_FAKE]
    resposta = (
        "Seu relatório indica risco Alto para Diabetes Mellitus Tipo 2, "
        "com o marcador RS7903146 no gene TCF7L2 e percentil 89."
    )
    checagem = validar_ancoragem(resposta, trechos)
    assert checagem["ancorado"] is True
    assert checagem["termos_nao_ancorados"] == []


def test_ancoragem_detecta_snp_inventado():
    trechos = [t["conteudo"] for t in TRECHOS_FAKE]
    resposta = "O relatório também aponta o marcador RS9999999 como relevante."
    checagem = validar_ancoragem(resposta, trechos)
    assert checagem["ancorado"] is False
    assert "RS9999999" in checagem["detalhes"]["snps"]


def test_ancoragem_detecta_numero_inventado():
    trechos = [t["conteudo"] for t in TRECHOS_FAKE]
    resposta = "Seu escore poligênico está no percentil 42."
    checagem = validar_ancoragem(resposta, trechos)
    assert checagem["ancorado"] is False
    assert "42" in checagem["detalhes"]["numeros"]


def test_ancoragem_detecta_gene_inventado():
    trechos = [t["conteudo"] for t in TRECHOS_FAKE]
    resposta = "Foi identificada uma alteração no gene BRCA2."
    checagem = validar_ancoragem(resposta, trechos)
    assert checagem["ancorado"] is False
    assert "BRCA2" in checagem["detalhes"]["genes"]


def test_ancoragem_ignora_marcadores_de_lista():
    """Numeração de tópicos não pode ser confundida com dado clínico."""
    trechos = ["Recomenda-se monitoramento periódico conforme o relatório."]
    resposta = "1. Manter acompanhamento.\n2. Revisar hábitos."
    checagem = validar_ancoragem(resposta, trechos)
    assert checagem["ancorado"] is True


def test_politica_sinalizar_devolve_resposta_marcada():
    busca = BuscaFake()
    llm = LLMFake(resposta="Percentil 42 e marcador RS9999999 identificados.")
    resultado = responder_personalizado(
        pergunta="Qual meu escore?",
        perfil="medico",
        usuario_id="u7",
        api_key="fake",
        politica_ancoragem="sinalizar",
        fn_buscar=busca,
        fn_llm=llm,
    )
    assert resultado["status"] == "respondido"
    assert resultado["ancoragem"]["ancorado"] is False
    assert resultado["ancoragem"]["termos_nao_ancorados"]


def test_politica_bloquear_substitui_resposta_nao_ancorada():
    busca = BuscaFake()
    llm = LLMFake(resposta="Percentil 42 e marcador RS9999999 identificados.")
    resultado = responder_personalizado(
        pergunta="Qual meu escore?",
        perfil="medico",
        usuario_id="u8",
        api_key="fake",
        politica_ancoragem="bloquear",
        fn_buscar=busca,
        fn_llm=llm,
    )
    assert resultado["status"] == "nao_ancorado"
    assert "RS9999999" not in resultado["resposta"]
    assert "não consegui confirmar" in resultado["resposta"].lower()


def test_politica_invalida_falha():
    with pytest.raises(ValueError, match="politica_ancoragem"):
        responder_personalizado(
            pergunta="Tenho risco?",
            perfil="medico",
            politica_ancoragem="ignorar",
        )


# ─────────────────────────────────────────────────────────────────────────────
# 5. HISTÓRICO (simulado — ponto de troca do Integrante 1)
# ─────────────────────────────────────────────────────────────────────────────

def test_historico_registra_interacoes():
    historico = HistoricoMemoria()
    for _ in range(2):
        responder_personalizado(
            pergunta="Eu tenho risco de diabetes?",
            perfil="leigo_ansioso",
            usuario_id="paciente-1",
            api_key="fake",
            historico=historico,
            fn_buscar=BuscaFake(),
            fn_llm=LLMFake(),
        )
    itens = historico.listar("paciente-1")
    assert len(itens) == 2
    assert itens[0]["secoes_citadas"] == ["resultado_2.1", "marcadores_2.1"]


def test_historico_nao_grava_texto_da_resposta():
    """Privacidade: o histórico guarda metadados, não conteúdo clínico gerado."""
    historico = HistoricoMemoria()
    responder_personalizado(
        pergunta="Eu tenho risco de diabetes?",
        perfil="leigo_ansioso",
        usuario_id="paciente-2",
        api_key="fake",
        historico=historico,
        fn_buscar=BuscaFake(),
        fn_llm=LLMFake(),
    )
    item = historico.listar("paciente-2")[0]
    assert "resposta" not in item
    assert set(item) == {
        "usuario_id", "pergunta", "perfil", "secoes_citadas", "timestamp",
    }


def test_historico_ativa_diretiva_de_continuidade():
    historico = HistoricoMemoria()
    llm_primeira = LLMFake()
    responder_personalizado(
        pergunta="Eu tenho risco de diabetes?",
        perfil="leigo_ansioso",
        usuario_id="paciente-3",
        api_key="fake",
        historico=historico,
        fn_buscar=BuscaFake(),
        fn_llm=llm_primeira,
    )
    assert "[Continuidade]" not in llm_primeira.chamadas[0]["pergunta"]

    llm_segunda = LLMFake()
    responder_personalizado(
        pergunta="E sobre minha ancestralidade?",
        perfil="leigo_ansioso",
        usuario_id="paciente-3",
        api_key="fake",
        historico=historico,
        fn_buscar=BuscaFake(),
        fn_llm=llm_segunda,
    )
    assert "[Continuidade]" in llm_segunda.chamadas[0]["pergunta"]


def test_historico_isolado_por_usuario():
    historico = HistoricoMemoria()
    responder_personalizado(
        pergunta="Eu tenho risco de diabetes?",
        perfil="medico",
        usuario_id="paciente-A",
        api_key="fake",
        historico=historico,
        fn_buscar=BuscaFake(),
        fn_llm=LLMFake(),
    )
    assert historico.listar("paciente-B") == []
    assert historico.resumir("paciente-B")["total_interacoes"] == 0


def test_historico_json_persiste_entre_instancias(tmp_path):
    caminho = tmp_path / "historico.json"
    primeiro = HistoricoJSON(caminho=caminho)
    primeiro.registrar("p1", "Tenho risco?", "medico", ["resultado_2.1"])

    segundo = HistoricoJSON(caminho=caminho)
    assert segundo.resumir("p1")["total_interacoes"] == 1
    assert segundo.resumir("p1")["secoes_recorrentes"] == ["resultado_2.1"]


def test_historico_json_tolera_arquivo_corrompido(tmp_path):
    caminho = tmp_path / "historico.json"
    caminho.write_text("{ isso não é json", encoding="utf-8")
    repo = HistoricoJSON(caminho=caminho)
    assert repo.resumir("p1")["total_interacoes"] == 0


# ─────────────────────────────────────────────────────────────────────────────
# 6. CONTRATO PÚBLICO
# ─────────────────────────────────────────────────────────────────────────────

CHAVES_CONTRATO = {
    "versao_contrato", "pergunta", "perfil", "modo_efetivo", "status",
    "categoria", "resposta", "fontes", "ancoragem", "historico_resumo",
}


@pytest.mark.parametrize("pergunta,perfil", [
    ("Eu tenho risco de diabetes?", "leigo_ansioso"),
    ("Qual dieta para emagrecer devo seguir?", "leigo_curioso"),
    ("Quais marcadores sustentam o escore?", "medico"),
])
def test_contrato_estavel_em_todos_os_caminhos(pergunta, perfil):
    resultado = responder_personalizado(
        pergunta=pergunta,
        perfil=perfil,
        usuario_id="contrato",
        api_key="fake",
        fn_buscar=BuscaFake(),
        fn_llm=LLMFake(),
    )
    assert set(resultado) == CHAVES_CONTRATO
    assert resultado["versao_contrato"] == VERSAO_CONTRATO
    assert resultado["status"] in {
        "respondido", "bloqueado", "sem_contexto", "nao_ancorado",
    }
    assert set(resultado["ancoragem"]) == {
        "ancorado", "termos_nao_ancorados", "score_sobreposicao", "politica",
    }


def test_contrato_nao_depende_do_formato_do_sprint3_nlp():
    """
    O contrato é independente do wrapper de sprint3/nlp/: nenhuma das chaves
    daquele módulo (resposta_final, metricas_*, resumo_interacoes) aparece aqui.
    """
    resultado = responder_personalizado(
        pergunta="Eu tenho risco de diabetes?",
        perfil="medico",
        usuario_id="contrato-2",
        api_key="fake",
        fn_buscar=BuscaFake(),
        fn_llm=LLMFake(),
    )
    for chave in ("resposta_final", "metricas_original", "metricas_final",
                  "resumo_interacoes", "historico"):
        assert chave not in resultado


def test_pergunta_vazia_falha():
    with pytest.raises(ValueError, match="não pode estar vazia"):
        responder_personalizado(pergunta="   ", perfil="medico")


# ─────────────────────────────────────────────────────────────────────────────
# 7. INTEGRAÇÃO COM A BASE VETORIAL REAL (skip automático)
# ─────────────────────────────────────────────────────────────────────────────

BASE_VETORIAL = RAIZ / "sprint2" / "vetorial" / "base_vetorial"


@pytest.mark.skipif(
    not BASE_VETORIAL.exists(),
    reason="Base vetorial não construída — rode sprint2/pipeline/pipeline_completo.py",
)
def test_busca_real_alimenta_a_personalizacao():
    """
    Usa a busca semântica real da Sprint 2 (sem chamar o LLM) para confirmar
    que a ponte trecho-dict → trecho-string funciona com dados reais.
    """
    llm = LLMFake()
    resultado = responder_personalizado(
        pergunta="Eu tenho risco de diabetes?",
        perfil="medico",
        usuario_id="integracao-real",
        api_key="fake",
        fn_llm=llm,
    )
    assert resultado["status"] == "respondido"
    assert resultado["fontes"], "A busca real deveria retornar trechos"
    assert all("secao" in f and "fonte" in f for f in resultado["fontes"])
    assert all(isinstance(t, str) for t in llm.chamadas[0]["trechos"])
