"""
Testes do instrumento de custo contra um DUPLO do SDK OpenAI.

Nenhum teste faz chamada de rede nem precisa de chave. O duplo imita a forma
do SDK (OpenAI().chat.completions.create e as classes de exceção que
llm_connector.chamar_openai() referencia), e os testes passam pelo caminho de
produção responder_com_llm() → chamar_openai().
"""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_DIR = Path(__file__).resolve().parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

from instrumento_custo import capturar_chamadas, estimar_custo  # noqa: E402

import llm_connector  # noqa: E402  (sys.path configurado por instrumento_custo)


# ─────────────────────────────────────────────────────────────────────────────
# DUPLO DO SDK
# ─────────────────────────────────────────────────────────────────────────────

class _ErroOpenAI(Exception):
    pass


class _ErroAutenticacao(_ErroOpenAI):
    pass


class _ErroQuota(_ErroOpenAI):
    pass


class _ErroConexao(_ErroOpenAI):
    pass


def _modulo_duplo(resposta=None, erro=None, chamadas_recebidas=None):
    """Monta um módulo falso com a forma do SDK openai >= 1.x."""
    recebidas = chamadas_recebidas if chamadas_recebidas is not None else []

    class _Completions:
        def create(self, **kwargs):
            recebidas.append(kwargs)
            if erro is not None:
                raise erro
            return resposta

    class _Cliente:
        def __init__(self, api_key=None):
            self.api_key = api_key
            self.chat = SimpleNamespace(completions=_Completions())

    return SimpleNamespace(
        OpenAI=_Cliente,
        OpenAIError=_ErroOpenAI,
        AuthenticationError=_ErroAutenticacao,
        RateLimitError=_ErroQuota,
        APIConnectionError=_ErroConexao,
    )


def _resposta_dupla(texto="Resumo:\nTexto do duplo.", usage=True):
    return SimpleNamespace(
        id="chatcmpl-duplo-001",
        model="gpt-4.1-mini-duplo",
        usage=(SimpleNamespace(prompt_tokens=812, completion_tokens=143,
                               total_tokens=955) if usage else None),
        choices=[SimpleNamespace(message=SimpleNamespace(content=texto))],
    )


TRECHOS = ["Condição: Diabetes Mellitus Tipo 2. Nível de risco: Alto."]


@pytest.fixture
def sdk_duplo(monkeypatch):
    """Substitui o SDK real do conector pelo duplo durante o teste."""
    def instalar(**kwargs):
        modulo = _modulo_duplo(**kwargs)
        monkeypatch.setattr(llm_connector, "_openai_module", modulo)
        return modulo
    return instalar


# ─────────────────────────────────────────────────────────────────────────────
# TESTES
# ─────────────────────────────────────────────────────────────────────────────

def test_registra_id_modelo_usage_e_parametros_enviados(sdk_duplo):
    sdk_duplo(resposta=_resposta_dupla())

    with capturar_chamadas(llm_connector) as registro:
        resultado = llm_connector.responder_com_llm(
            pergunta="O que meu relatório diz sobre diabetes?",
            trechos=TRECHOS, modo="paciente", api_key="sk-duplo",
        )

    assert resultado["status"] == "respondido"
    assert len(registro.chamadas) == 1
    chamada = registro.chamadas[0]
    assert chamada["id_resposta"] == "chatcmpl-duplo-001"
    assert chamada["modelo_respondido"] == "gpt-4.1-mini-duplo"
    assert chamada["usage"] == {"prompt_tokens": 812, "completion_tokens": 143,
                                "total_tokens": 955}
    assert chamada["erro"] is None
    assert chamada["latencia_s"] is not None


def test_parametros_registrados_sao_os_que_o_conector_enviou(sdk_duplo):
    recebidas = []
    sdk_duplo(resposta=_resposta_dupla(), chamadas_recebidas=recebidas)

    with capturar_chamadas(llm_connector) as registro:
        llm_connector.responder_com_llm(
            pergunta="Qual é minha ancestralidade?",
            trechos=TRECHOS, modo="paciente", api_key="sk-duplo",
        )

    enviados = registro.chamadas[0]["parametros_enviados"]
    assert enviados == {
        "model": recebidas[0]["model"],
        "temperature": recebidas[0]["temperature"],
        "top_p": recebidas[0]["top_p"],
        "max_tokens": recebidas[0]["max_tokens"],
    }
    # E batem com o que o conector tem carregado neste processo.
    assert enviados["model"] == llm_connector.MODELO
    assert enviados["max_tokens"] == llm_connector.MAX_TOKENS


def test_resposta_do_sdk_chega_intacta_ao_conector(sdk_duplo):
    texto = "Resumo:\nResposta exata que o duplo devolveu."
    sdk_duplo(resposta=_resposta_dupla(texto=texto))

    with capturar_chamadas(llm_connector):
        resultado = llm_connector.responder_com_llm(
            pergunta="Explique meu resultado de diabetes.",
            trechos=TRECHOS, modo="paciente", api_key="sk-duplo",
        )

    assert resultado["resposta"] == texto.strip()


def test_pergunta_bloqueada_nao_gera_chamada(sdk_duplo):
    """Custo zero do guardrail, provado pelo registro vazio."""
    recebidas = []
    sdk_duplo(resposta=_resposta_dupla(), chamadas_recebidas=recebidas)

    with capturar_chamadas(llm_connector) as registro:
        resultado = llm_connector.responder_com_llm(
            pergunta="Qual remédio devo tomar?",
            trechos=TRECHOS, modo="paciente", api_key="sk-duplo",
        )

    assert resultado["status"] == "bloqueado"
    assert registro.chamadas == []
    assert recebidas == []


def test_sem_contexto_nao_gera_chamada(sdk_duplo):
    sdk_duplo(resposta=_resposta_dupla())

    with capturar_chamadas(llm_connector) as registro:
        resultado = llm_connector.responder_com_llm(
            pergunta="Qual é minha ancestralidade?",
            trechos=[], modo="paciente", api_key="sk-duplo",
        )

    assert resultado["status"] == "sem_contexto"
    assert registro.chamadas == []


def test_erro_do_sdk_e_registrado_e_propagado(sdk_duplo):
    sdk_duplo(erro=_ErroAutenticacao("chave inválida (duplo)"))

    with capturar_chamadas(llm_connector) as registro:
        with pytest.raises(PermissionError):
            llm_connector.responder_com_llm(
                pergunta="O que meu relatório diz sobre diabetes?",
                trechos=TRECHOS, modo="paciente", api_key="sk-duplo",
            )

    assert len(registro.chamadas) == 1
    assert registro.chamadas[0]["erro"].startswith("_ErroAutenticacao")
    assert registro.chamadas[0]["usage"]["total_tokens"] is None


def test_modulo_original_restaurado_mesmo_com_excecao(sdk_duplo):
    modulo = sdk_duplo(resposta=_resposta_dupla())

    with pytest.raises(ValueError):
        with capturar_chamadas(llm_connector):
            assert llm_connector._openai_module is not modulo
            raise ValueError("falha dentro do bloco")

    assert llm_connector._openai_module is modulo


def test_usage_ausente_fica_none_e_fora_dos_totais(sdk_duplo):
    sdk_duplo(resposta=_resposta_dupla(usage=False))

    with capturar_chamadas(llm_connector) as registro:
        llm_connector.responder_com_llm(
            pergunta="O que meu relatório diz sobre diabetes?",
            trechos=TRECHOS, modo="paciente", api_key="sk-duplo",
        )

    assert registro.chamadas[0]["usage"]["total_tokens"] is None
    totais = registro.totais()
    assert totais["chamadas"] == 1
    assert totais["chamadas_com_usage"] == 0
    assert totais["total_tokens"] == 0


def test_totais_somam_tokens_medidos(sdk_duplo):
    sdk_duplo(resposta=_resposta_dupla())

    with capturar_chamadas(llm_connector) as registro:
        for _ in range(3):
            llm_connector.responder_com_llm(
                pergunta="O que meu relatório diz sobre diabetes?",
                trechos=TRECHOS, modo="paciente", api_key="sk-duplo",
            )

    assert registro.totais() == {
        "chamadas": 3, "chamadas_com_usage": 3,
        "prompt_tokens": 3 * 812, "completion_tokens": 3 * 143,
        "total_tokens": 3 * 955,
    }


def test_sem_sdk_instalado_falha_explicitamente(monkeypatch):
    monkeypatch.setattr(llm_connector, "_openai_module", None)
    with pytest.raises(RuntimeError):
        with capturar_chamadas(llm_connector):
            pass


def test_estimativa_exige_preco_explicito():
    assert estimar_custo(1000, 200, None, None) is None
    assert estimar_custo(1_000_000, 1_000_000, 0.5, 2.0) == 2.5
