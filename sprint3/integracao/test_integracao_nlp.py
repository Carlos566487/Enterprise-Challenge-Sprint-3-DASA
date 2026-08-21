"""
Testes da Integração RAG Personalizado + NLP — Sprint 3 / Genera AI / Dasa

Executar:
    pytest sprint3/integracao/ -v

Não exigem OPENAI_API_KEY nem base vetorial: busca, LLM e simplificador são
injetáveis. O único teste que usa a função real da Tayná tem skip automático
se sprint3/nlp/ não estiver disponível.
"""

import sys
from pathlib import Path

import pytest

_DIR = Path(__file__).resolve().parent
RAIZ = _DIR.parents[1]

for _caminho in (RAIZ, _DIR):
    if str(_caminho) not in sys.path:
        sys.path.insert(0, str(_caminho))

from adaptador_nlp import (                                  # noqa: E402
    MOTIVO_ANCORAGEM,
    MOTIVO_INDISPONIVEL,
    MOTIVO_OK,
    MOTIVO_PERFIL_TECNICO,
    MOTIVO_STATUS,
    VERSAO_CONTRATO_INTEGRACAO,
    responder_com_linguagem_simples,
)
from sprint3.rag_personalizacao import HistoricoMemoria      # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# FAKES
# ─────────────────────────────────────────────────────────────────────────────

TRECHOS_FAKE = [
    {
        "conteudo": (
            "Condição: Diabetes Mellitus Tipo 2. Nível de risco: Alto. "
            "Seu DNA indica uma chance maior de desenvolver diabetes tipo 2."
        ),
        "secao": "resultado_2.1",
        "fonte": "dados_estruturados.json > resultados > Diabetes",
        "similaridade": 0.62,
    },
    {
        "conteudo": (
            "Marcadores genéticos: RS7903146 (TCF7L2) alelo T/T. "
            "Escore poligênico percentil 89."
        ),
        "secao": "marcadores_2.1",
        "fonte": "dados_estruturados.json > resultados > Diabetes > marcadores",
        "similaridade": 0.57,
    },
]

RESPOSTA_ANCORADA = (
    "Resumo:\nSeu relatório indica risco Alto para Diabetes Mellitus Tipo 2, "
    "com o marcador RS7903146 no gene TCF7L2 e percentil 89."
)


class BuscaFake:
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
    def __init__(self, resposta=None):
        self.resposta = RESPOSTA_ANCORADA if resposta is None else resposta
        self.chamadas = []

    def __call__(self, pergunta, trechos, modo, api_key):
        self.chamadas.append({"pergunta": pergunta, "modo": modo})
        return {
            "status": "respondido",
            "resposta": self.resposta,
            "fontes": trechos,
            "categoria": "resposta_rag",
        }


class SimplificadorFake:
    """Substitui a função pura da Tayná com saída controlada."""

    def __init__(self, texto_simplificado=None):
        self.texto = texto_simplificado
        self.chamadas = []

    def __call__(self, texto):
        self.chamadas.append(texto)
        simplificado = self.texto if self.texto is not None else (
            texto.replace("Diabetes Mellitus Tipo 2", "diabetes tipo 2")
        )
        return {
            "texto_original": texto,
            "texto_simplificado": simplificado,
            "metricas_original": {"palavras": len(texto.split())},
            "metricas_simplificado": {"palavras": len(simplificado.split())},
        }


def chamar(**kwargs):
    """Atalho com os fakes padrão, permitindo sobrescrever qualquer um."""
    base = {
        "pergunta": "Eu tenho risco de diabetes?",
        "perfil": "leigo_ansioso",
        "usuario_id": "u-teste",
        "api_key": "fake",
        "fn_buscar": BuscaFake(),
        "fn_llm": LLMFake(),
        "fn_simplificar": SimplificadorFake(),
    }
    base.update(kwargs)
    return responder_com_linguagem_simples(**base)


# ─────────────────────────────────────────────────────────────────────────────
# 1. OS TRÊS PERFIS
# ─────────────────────────────────────────────────────────────────────────────

def test_perfil_leigo_ansioso_simplifica():
    simplificador = SimplificadorFake()
    resultado = chamar(perfil="leigo_ansioso", fn_simplificar=simplificador)

    assert resultado["status"] == "respondido"
    assert resultado["modo_efetivo"] == "paciente"
    assert resultado["simplificacao"]["aplicada"] is True
    assert resultado["simplificacao"]["motivo"] == MOTIVO_OK
    assert simplificador.chamadas, "o simplificador deveria ter sido chamado"
    assert resultado["resposta_simplificada"] != resultado["resposta"]


def test_perfil_leigo_curioso_simplifica():
    resultado = chamar(perfil="leigo_curioso")
    assert resultado["modo_efetivo"] == "paciente"
    assert resultado["simplificacao"]["aplicada"] is True


def test_regra_2_perfil_medico_nunca_simplifica():
    """Trocar termos técnicos para um profissional destrói a precisão."""
    simplificador = SimplificadorFake()
    resultado = chamar(perfil="medico", fn_simplificar=simplificador)

    assert resultado["modo_efetivo"] == "tecnico"
    assert resultado["simplificacao"]["aplicada"] is False
    assert resultado["simplificacao"]["motivo"] == MOTIVO_PERFIL_TECNICO
    assert simplificador.chamadas == [], "não deveria chamar o simplificador"
    assert resultado["resposta_simplificada"] == resultado["resposta"]


# ─────────────────────────────────────────────────────────────────────────────
# 2. REGRA 1 — GUARDRAILS E AUSÊNCIA DE CONTEXTO
# ─────────────────────────────────────────────────────────────────────────────

def test_regra_1_pergunta_bloqueada_nao_e_simplificada():
    """Mensagem de recusa é texto aprovado por governança: não parafrasear."""
    simplificador = SimplificadorFake()
    llm = LLMFake()
    resultado = chamar(
        pergunta="Qual remédio devo tomar para isso?",
        fn_llm=llm,
        fn_simplificar=simplificador,
    )

    assert resultado["status"] == "bloqueado"
    assert resultado["categoria"] == "prescricao"
    assert resultado["simplificacao"]["aplicada"] is False
    assert resultado["simplificacao"]["motivo"] == MOTIVO_STATUS
    assert simplificador.chamadas == []
    assert llm.chamadas == []
    assert resultado["resposta_simplificada"] == resultado["resposta"]


def test_regra_1_pergunta_fora_de_escopo_nao_e_simplificada():
    simplificador = SimplificadorFake()
    resultado = chamar(
        pergunta="Qual dieta para emagrecer devo seguir?",
        fn_simplificar=simplificador,
    )
    assert resultado["status"] == "bloqueado"
    assert resultado["categoria"] == "fora_escopo"
    assert simplificador.chamadas == []


def test_sem_contexto_nao_e_simplificado():
    simplificador = SimplificadorFake()
    resultado = chamar(
        pergunta="O relatório fala sobre minha altura?",
        fn_buscar=BuscaFake(trechos=[]),
        fn_simplificar=simplificador,
    )
    assert resultado["status"] == "sem_contexto"
    assert resultado["simplificacao"]["motivo"] == MOTIVO_STATUS
    assert simplificador.chamadas == []


def test_status_nao_ancorado_nao_e_simplificado():
    """Com política 'bloquear', a resposta vira mensagem segura — não reescrever."""
    simplificador = SimplificadorFake()
    resultado = chamar(
        fn_llm=LLMFake(resposta="Percentil 42 e marcador RS9999999 encontrados."),
        politica_ancoragem="bloquear",
        fn_simplificar=simplificador,
    )
    assert resultado["status"] == "nao_ancorado"
    assert resultado["simplificacao"]["aplicada"] is False
    assert resultado["simplificacao"]["motivo"] == MOTIVO_STATUS
    assert simplificador.chamadas == []


# ─────────────────────────────────────────────────────────────────────────────
# 3. REGRA 3 — REVALIDAÇÃO DE ANCORAGEM APÓS SIMPLIFICAR
# ─────────────────────────────────────────────────────────────────────────────

def test_regra_3_simplificacao_que_inventa_fato_faz_fallback():
    """
    Ganho central deste adaptador: o texto exibido é revalidado.
    Se a reescrita introduzir um fato ausente do relatório, volta ao original.
    """
    simplificador = SimplificadorFake(
        texto_simplificado="Seu percentil é 42 e o marcador é RS9999999."
    )
    resultado = chamar(fn_simplificar=simplificador)

    assert resultado["status"] == "respondido"
    assert resultado["simplificacao"]["aplicada"] is False
    assert resultado["simplificacao"]["motivo"] == MOTIVO_ANCORAGEM
    assert resultado["simplificacao"]["termos_nao_ancorados"]
    assert resultado["resposta_simplificada"] == resultado["resposta"]
    assert "RS9999999" not in resultado["resposta_simplificada"]


def test_regra_3_simplificacao_que_preserva_fatos_e_aceita():
    simplificador = SimplificadorFake(
        texto_simplificado=(
            "Seu relatório mostra risco Alto para diabetes tipo 2, "
            "com o marcador RS7903146 no gene TCF7L2 e percentil 89."
        )
    )
    resultado = chamar(fn_simplificar=simplificador)
    assert resultado["simplificacao"]["aplicada"] is True
    assert "RS7903146" in resultado["resposta_simplificada"]


def test_simplificador_indisponivel_degrada_com_seguranca():
    """Sem sprint3/nlp/, a resposta continua sendo entregue — sem quebrar."""
    def sem_nlp(_texto):
        raise AssertionError("não deveria ser chamado")

    import adaptador_nlp

    original = adaptador_nlp._carregar_simplificador
    adaptador_nlp._carregar_simplificador = lambda: None
    try:
        resultado = responder_com_linguagem_simples(
            pergunta="Eu tenho risco de diabetes?",
            perfil="leigo_ansioso",
            usuario_id="u-sem-nlp",
            api_key="fake",
            fn_buscar=BuscaFake(),
            fn_llm=LLMFake(),
        )
    finally:
        adaptador_nlp._carregar_simplificador = original

    assert resultado["status"] == "respondido"
    assert resultado["simplificacao"]["motivo"] == MOTIVO_INDISPONIVEL
    assert resultado["resposta_simplificada"] == resultado["resposta"]


# ─────────────────────────────────────────────────────────────────────────────
# 4. CONTRATO
# ─────────────────────────────────────────────────────────────────────────────

CHAVES_V1 = {
    "versao_contrato", "pergunta", "perfil", "modo_efetivo", "status",
    "categoria", "resposta", "fontes", "ancoragem", "historico_resumo",
}
CHAVES_INTEGRACAO = {
    "versao_contrato_integracao", "resposta_simplificada", "simplificacao",
}


@pytest.mark.parametrize("pergunta,perfil", [
    ("Eu tenho risco de diabetes?", "leigo_ansioso"),
    ("Por que tenho essa predisposição?", "leigo_curioso"),
    ("Quais marcadores sustentam o escore?", "medico"),
    ("Qual remédio devo tomar?", "leigo_ansioso"),
    ("Qual dieta para emagrecer devo seguir?", "leigo_curioso"),
])
def test_contrato_estavel_em_todos_os_caminhos(pergunta, perfil):
    resultado = chamar(pergunta=pergunta, perfil=perfil)

    assert CHAVES_V1 <= set(resultado), "contrato v1.0 deve ser preservado"
    assert CHAVES_INTEGRACAO <= set(resultado)
    assert resultado["versao_contrato"] == "1.0"
    assert resultado["versao_contrato_integracao"] == VERSAO_CONTRATO_INTEGRACAO
    assert isinstance(resultado["resposta_simplificada"], str)
    assert isinstance(resultado["simplificacao"]["aplicada"], bool)


def test_resposta_simplificada_sempre_renderizavel():
    """
    O consumidor pode sempre renderizar resposta_simplificada sem checar nada:
    quando a simplificação não é aplicada, ela é igual a resposta.
    """
    for perfil in ("leigo_ansioso", "leigo_curioso", "medico"):
        resultado = chamar(perfil=perfil)
        assert resultado["resposta_simplificada"].strip()
        if not resultado["simplificacao"]["aplicada"]:
            assert resultado["resposta_simplificada"] == resultado["resposta"]


def test_historico_continua_funcionando_atraves_do_adaptador():
    historico = HistoricoMemoria()
    for _ in range(2):
        chamar(usuario_id="paciente-hist", historico=historico)
    assert historico.resumir("paciente-hist")["total_interacoes"] == 2


def test_perfil_invalido_propaga_erro():
    with pytest.raises(ValueError, match="Perfil desconhecido"):
        chamar(perfil="astrologo")


# ─────────────────────────────────────────────────────────────────────────────
# 5. INTEGRAÇÃO COM A FUNÇÃO REAL DA TAYNÁ (skip automático)
# ─────────────────────────────────────────────────────────────────────────────

NLP_REAL = RAIZ / "sprint3" / "nlp" / "nlp_simplificacao.py"


@pytest.mark.skipif(
    not NLP_REAL.exists(),
    reason="sprint3/nlp/nlp_simplificacao.py não encontrado",
)
def test_integracao_com_funcao_real_da_taina():
    """
    Usa a função pura real de sprint3/nlp/ — sem modificar nada naquele módulo.
    Confirma que a composição funciona ponta a ponta com o código dela.
    """
    resultado = responder_com_linguagem_simples(
        pergunta="Eu tenho risco de diabetes?",
        perfil="leigo_ansioso",
        usuario_id="u-nlp-real",
        api_key="fake",
        fn_buscar=BuscaFake(),
        fn_llm=LLMFake(
            resposta=(
                "O relatório indica predisposição genética para diabetes "
                "tipo 2, com marcadores genéticos identificados no seu DNA."
            )
        ),
    )
    assert resultado["status"] == "respondido"
    assert resultado["simplificacao"]["motivo"] in (MOTIVO_OK, MOTIVO_ANCORAGEM)
    assert resultado["resposta_simplificada"].strip()
    # A função real produz métricas de legibilidade em ambos os casos.
    assert resultado["simplificacao"]["metricas_original"]
