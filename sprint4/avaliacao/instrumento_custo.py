"""
Instrumento de custo e proveniência — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Envoltório SOMENTE DE LEITURA em volta do SDK OpenAI usado por
sprint2/interface/llm_connector.py. Não altera o arquivo do conector nem o
caminho de produção: durante o bloco `capturar_chamadas()`, o atributo
`llm_connector._openai_module` é trocado por um proxy que delega tudo ao SDK
real e apenas registra, para cada chamada a chat.completions.create:

    • o que a OpenAI devolveu:  id, model, usage (tokens de prompt/resposta)
    • o que o conector enviou:  model, temperature, top_p, max_tokens
    • latência e, se houver, a exceção levantada

Por que registrar os parâmetros ENVIADOS e não os de config_llm.py
──────────────────────────────────────────────────────────────────────────────
llm_connector.py tem um fallback silencioso (linhas 35–42): se o import de
config_llm falhar, usa valores fixos sem avisar. Ler config_llm.py diria o que
DEVERIA ter sido usado; este instrumento registra o que DE FATO foi enviado.

A resposta devolvida ao conector é o objeto original do SDK, sem cópia nem
modificação. Ao sair do bloco, o módulo original é restaurado — inclusive se
houver exceção.

Uso:
    from instrumento_custo import capturar_chamadas
    with capturar_chamadas() as registro:
        resultado = responder_com_llm(pergunta, trechos, modo, api_key)
    registro.chamadas   # lista de dicts, uma por chamada real
"""

import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

for _caminho in (RAIZ / "sprint2" / "agente", RAIZ / "sprint2" / "interface"):
    if str(_caminho) not in sys.path:
        sys.path.insert(0, str(_caminho))


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _ler(objeto, nome, padrao=None):
    """Lê atributo de objeto do SDK ou chave de dict, sem assumir o formato."""
    if objeto is None:
        return padrao
    if isinstance(objeto, dict):
        return objeto.get(nome, padrao)
    return getattr(objeto, nome, padrao)


def _extrair_usage(resposta) -> dict:
    usage = _ler(resposta, "usage")
    return {
        "prompt_tokens": _ler(usage, "prompt_tokens"),
        "completion_tokens": _ler(usage, "completion_tokens"),
        "total_tokens": _ler(usage, "total_tokens"),
    }


@dataclass
class RegistroChamadas:
    """Acumula uma entrada por chamada a chat.completions.create."""

    chamadas: list = field(default_factory=list)

    def totais(self) -> dict:
        """Soma de tokens das chamadas bem-sucedidas que informaram usage."""
        validas = [c for c in self.chamadas
                   if c["erro"] is None and c["usage"]["total_tokens"] is not None]
        return {
            "chamadas": len(self.chamadas),
            "chamadas_com_usage": len(validas),
            "prompt_tokens": sum(c["usage"]["prompt_tokens"] or 0 for c in validas),
            "completion_tokens": sum(c["usage"]["completion_tokens"] or 0 for c in validas),
            "total_tokens": sum(c["usage"]["total_tokens"] or 0 for c in validas),
        }


class _CompletionsInstrumentado:
    def __init__(self, completions_real, registro: RegistroChamadas,
                 modelo_substituto: str = None, endpoint: str = None):
        self._real = completions_real
        self._registro = registro
        self._modelo_substituto = modelo_substituto
        self._endpoint = endpoint

    def create(self, *args, **kwargs):
        modelo_pedido = kwargs.get("model")
        if self._modelo_substituto:
            # Troca na FRONTEIRA: o conector continua pedindo o modelo de
            # produção; só a requisição que sai deste envoltório muda.
            kwargs["model"] = self._modelo_substituto
        entrada = {
            "timestamp_utc": _agora(),
            "endpoint": self._endpoint,
            "modelo_pedido_pelo_conector": modelo_pedido,
            "parametros_enviados": {
                chave: kwargs.get(chave)
                for chave in ("model", "temperature", "top_p", "max_tokens")
            },
            "id_resposta": None,
            "modelo_respondido": None,
            "finish_reason": None,
            "usage": {"prompt_tokens": None, "completion_tokens": None,
                      "total_tokens": None},
            "latencia_s": None,
            "erro": None,
        }
        inicio = time.perf_counter()
        try:
            resposta = self._real.create(*args, **kwargs)
        except Exception as erro:
            entrada["latencia_s"] = round(time.perf_counter() - inicio, 3)
            entrada["erro"] = f"{type(erro).__name__}: {erro}"
            self._registro.chamadas.append(entrada)
            raise

        entrada["latencia_s"] = round(time.perf_counter() - inicio, 3)
        entrada["id_resposta"] = _ler(resposta, "id")
        entrada["modelo_respondido"] = _ler(resposta, "model")
        escolhas = _ler(resposta, "choices") or []
        entrada["finish_reason"] = _ler(escolhas[0], "finish_reason") if escolhas else None
        entrada["usage"] = _extrair_usage(resposta)
        self._registro.chamadas.append(entrada)
        return resposta

    def __getattr__(self, nome):
        return getattr(self._real, nome)


class _ChatInstrumentado:
    def __init__(self, chat_real, registro, modelo_substituto=None, endpoint=None):
        self.completions = _CompletionsInstrumentado(chat_real.completions, registro,
                                                     modelo_substituto, endpoint)
        self._real = chat_real

    def __getattr__(self, nome):
        return getattr(self._real, nome)


class _ClienteInstrumentado:
    def __init__(self, cliente_real, registro, modelo_substituto=None):
        endpoint = str(getattr(cliente_real, "base_url", "") or "") or None
        self.chat = _ChatInstrumentado(cliente_real.chat, registro, modelo_substituto, endpoint)
        self._real = cliente_real

    def __getattr__(self, nome):
        return getattr(self._real, nome)


class _ModuloOpenAIInstrumentado:
    """
    Proxy do módulo `openai`. Só `OpenAI(...)` é interceptado; todo o resto
    (AuthenticationError, RateLimitError, ...) é o objeto real do SDK, então o
    tratamento de erro de chamar_openai() continua funcionando igual.
    """

    def __init__(self, modulo_real, registro, modelo_substituto=None):
        self._real = modulo_real
        self._registro = registro
        self._modelo_substituto = modelo_substituto

    def OpenAI(self, *args, **kwargs):  # noqa: N802 — espelha o nome do SDK
        return _ClienteInstrumentado(self._real.OpenAI(*args, **kwargs), self._registro,
                                     self._modelo_substituto)

    def __getattr__(self, nome):
        return getattr(self._real, nome)


@contextmanager
def capturar_chamadas(conector=None, modelo_substituto: str = None):
    """
    Instrumenta o SDK usado pelo conector durante o bloco `with`.

    Args:
        conector: o módulo llm_connector. Default: importado do projeto.
        modelo_substituto: se informado, troca o `model` da requisição na
            fronteira (ex.: modelo local do Ollama). O conector continua
            pedindo o modelo de produção; o registro guarda os dois, mais o
            modelo que a API diz ter respondido.

    Yields:
        RegistroChamadas — preenchido à medida que as chamadas acontecem.

    Raises:
        RuntimeError: se o SDK openai não estiver disponível no conector
                      (nesse caso não há o que instrumentar).
    """
    if conector is None:
        import llm_connector as conector

    original = conector._openai_module
    if original is None:
        raise RuntimeError(
            "llm_connector._openai_module é None — SDK openai não instalado."
        )

    registro = RegistroChamadas()
    conector._openai_module = _ModuloOpenAIInstrumentado(original, registro, modelo_substituto)
    try:
        yield registro
    finally:
        conector._openai_module = original


def estimar_custo(tokens_prompt: int, tokens_resposta: int,
                  preco_prompt_por_milhao, preco_resposta_por_milhao):
    """
    Custo em USD a partir de tokens MEDIDOS e preços informados explicitamente.

    Os preços não têm valor padrão de propósito: devem ser conferidos na
    página de preços da OpenAI na data da execução e passados por quem roda.
    Sem preço, devolve None — nunca um valor presumido.
    """
    if preco_prompt_por_milhao is None or preco_resposta_por_milhao is None:
        return None
    return round(
        tokens_prompt / 1e6 * preco_prompt_por_milhao
        + tokens_resposta / 1e6 * preco_resposta_por_milhao,
        6,
    )
