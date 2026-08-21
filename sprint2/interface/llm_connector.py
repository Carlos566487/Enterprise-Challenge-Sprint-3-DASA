"""
LLM Connector — Integrante 4
Integra o agente_especialista.py com a API OpenAI real.
Substitui gerar_resposta_simulada() sem modificar os arquivos dos outros integrantes.

Responsabilidade:
    - Autenticar com a API OpenAI usando chave do usuário ou variável de ambiente
    - Enviar o prompt montado pelo agente_especialista ao GPT-4.1 Mini
    - Respeitar os hiperparâmetros definidos pelo Integrante 3 em config_llm.py
    - Retornar resposta real ou encaminhar decisões de guardrail sem chamar o LLM
"""

import os
import sys
from pathlib import Path

try:
    import openai as _openai_module
except ImportError:
    _openai_module = None

# ── Configuração de caminhos para importar módulos dos outros integrantes ─────

RAIZ = Path(__file__).resolve().parents[2]

# Adiciona sprint2/agente ao path para que agente_especialista.py
# consiga importar 'prompts' e 'guardrails' sem prefixo de pacote
sys.path.insert(0, str(RAIZ / "sprint2" / "agente"))

# Importa o agente do Integrante 3 e as funções de construção de prompt
from agente_especialista import responder, construir_prompt_final, montar_contexto  # noqa: E402

# Importa configurações do modelo definidas pelo Integrante 3
sys.path.insert(0, str(RAIZ / "sprint2" / "agente"))
try:
    from config_llm import MODELO, TEMPERATURA, TOP_P, MAX_TOKENS  # noqa: E402
except ImportError:
    # Fallback com os valores padrão caso o módulo não seja encontrado
    MODELO = "gpt-4.1-mini"
    TEMPERATURA = 0.2
    TOP_P = 0.8
    MAX_TOKENS = 700


# ── Gerenciamento de API Key ──────────────────────────────────────────────────

def get_api_key(key_from_ui: str = None) -> str:
    """
    Tenta obter a API key na seguinte ordem de prioridade:
        1. Parâmetro key_from_ui (digitada pelo usuário na sidebar do Streamlit)
        2. Variável de ambiente OPENAI_API_KEY (definida no .env ou no sistema)

    Levanta ValueError se nenhuma das duas fontes estiver disponível.

    Args:
        key_from_ui: chave digitada pelo usuário na interface; pode ser None ou string vazia.

    Returns:
        str: API key válida (não vazia).

    Raises:
        ValueError: quando nenhuma chave é encontrada.
    """
    # Prioridade 1: chave fornecida diretamente pelo usuário na interface
    if key_from_ui and key_from_ui.strip():
        return key_from_ui.strip()

    # Prioridade 2: variável de ambiente
    chave_env = os.environ.get("OPENAI_API_KEY", "").strip()
    if chave_env:
        return chave_env

    raise ValueError(
        "API Key da OpenAI não encontrada. "
        "Insira-a na sidebar da interface ou defina a variável OPENAI_API_KEY no ambiente."
    )


# ── Chamada à API OpenAI ──────────────────────────────────────────────────────

def chamar_openai(
    prompt_final: str,
    api_key: str,
    modelo: str = MODELO,
    temperatura: float = TEMPERATURA,
    top_p: float = TOP_P,
    max_tokens: int = MAX_TOKENS,
) -> str:
    """
    Chama a API OpenAI com o prompt montado pelo agente_especialista.

    Utiliza os hiperparâmetros definidos pelo Integrante 3 em config_llm.py
    como valores padrão, mas permite sobrescritas para testes.

    Args:
        prompt_final: string completa com SYSTEM_PROMPT + contexto + pergunta.
        api_key:      chave de autenticação OpenAI.
        modelo:       identificador do modelo (padrão: gpt-4.1-mini).
        temperatura:  criatividade da geração (padrão: 0.2 — determinístico).
        top_p:        nucleus sampling (padrão: 0.8).
        max_tokens:   limite de tokens na resposta (padrão: 700).

    Returns:
        str: texto da resposta gerada pelo modelo.

    Raises:
        PermissionError: quando a API key é inválida (status 401).
        RuntimeError:    quando o limite de quota é atingido (status 429).
        ConnectionError: quando há falha de rede ou timeout.
        Exception:       para outros erros da API OpenAI.
    """
    # Verifica se a biblioteca openai está instalada
    if _openai_module is None:
        raise ImportError(
            "Biblioteca 'openai' não instalada. "
            "Execute: pip install openai>=1.0.0"
        )

    # Usa alias para evitar conflito com variáveis locais
    openai = _openai_module

    try:
        cliente = openai.OpenAI(api_key=api_key)

        resposta = cliente.chat.completions.create(
            model=modelo,
            messages=[
                # Envia o prompt completo como uma única mensagem do tipo 'user'
                # O SYSTEM_PROMPT já está embutido no prompt_final pelo agente_especialista
                {"role": "user", "content": prompt_final}
            ],
            temperature=temperatura,
            top_p=top_p,
            max_tokens=max_tokens,
        )

        # Extrai o texto da primeira escolha retornada pelo modelo
        return resposta.choices[0].message.content.strip()

    except openai.AuthenticationError as erro:
        raise PermissionError(
            f"Chave OpenAI inválida. Verifique e tente novamente. Detalhe: {erro}"
        ) from erro

    except openai.RateLimitError as erro:
        raise RuntimeError(
            f"Limite de uso da API atingido. Verifique seu plano OpenAI. Detalhe: {erro}"
        ) from erro

    except openai.APIConnectionError as erro:
        raise ConnectionError(
            f"Falha de conexão com a API OpenAI. Verifique sua internet. Detalhe: {erro}"
        ) from erro

    except openai.OpenAIError as erro:
        # Captura genérica para outros erros da SDK OpenAI
        raise Exception(f"Erro inesperado na API OpenAI: {erro}") from erro


# ── Função principal de integração ────────────────────────────────────────────

def responder_com_llm(
    pergunta: str,
    trechos: list,
    modo: str,
    api_key: str,
) -> dict:
    """
    Função principal usada pelo app.py para gerar respostas reais via LLM.

    Fluxo de execução:
        1. Chama responder() do agente_especialista (Integrante 3) com os trechos
           — o agente executa os guardrails e monta o prompt
        2. Se status for "bloqueado" ou "sem_contexto":
           retorna diretamente sem chamar o LLM (guardrail já decidiu)
        3. Se status for "respondido":
           reconstrói o prompt_final usando as funções do agente_especialista
           e chama chamar_openai() para obter resposta real (não simulada)

    Nota de design:
        Não duplicamos a lógica de construção do prompt — importamos
        construir_prompt_final e montar_contexto diretamente do agente_especialista,
        respeitando a divisão de responsabilidades entre integrantes.

    Args:
        pergunta: pergunta do usuário em linguagem natural.
        trechos:  lista de strings com o conteúdo dos trechos recuperados pelo RAG.
        modo:     "paciente" (linguagem simples) ou "tecnico" (detalhes clínicos).
        api_key:  chave OpenAI válida obtida via get_api_key().

    Returns:
        dict com as chaves:
            - status    (str):  "respondido" | "bloqueado" | "sem_contexto"
            - resposta  (str):  texto da resposta (real ou mensagem de guardrail)
            - fontes    (list): trechos usados na resposta
            - categoria (str):  "resposta_rag" | "diagnostico" | "prescricao" | etc.
    """
    # Etapa 1: delega ao agente_especialista (Integrante 3) para rodar guardrails
    # e verificar se o contexto é suficiente para responder
    resultado_agente = responder(
        pergunta=pergunta,
        trechos_recuperados=trechos,
        modo=modo,
    )

    # Etapa 2: guardrail ativado — retorna diretamente sem chamar o LLM
    if resultado_agente["status"] in ("bloqueado", "sem_contexto"):
        return {
            "status":    resultado_agente["status"],
            "resposta":  resultado_agente["resposta"],
            "fontes":    resultado_agente["fontes"],
            "categoria": resultado_agente["categoria"],
        }

    # Etapa 3: status == "respondido" — substitui a resposta simulada pela resposta real

    # Reconstrói o prompt exatamente como o agente o montaria
    # (sem duplicar lógica — usamos as funções do Integrante 3)
    contexto_montado = montar_contexto(trechos)
    prompt_final = construir_prompt_final(
        pergunta=pergunta,
        contexto=contexto_montado,
        modo=modo,
    )

    # Chama o LLM real substituindo gerar_resposta_simulada()
    resposta_real = chamar_openai(
        prompt_final=prompt_final,
        api_key=api_key,
    )

    return {
        "status":    "respondido",
        "resposta":  resposta_real,
        "fontes":    resultado_agente["fontes"],
        "categoria": resultado_agente["categoria"],
    }


# ── Execução de testes via terminal ──────────────────────────────────────────

if __name__ == "__main__":
    """
    Testa as três camadas do llm_connector sem depender da interface Streamlit.

    Cenários cobertos:
        1. Validação de imports (sempre executado)
        2. Guardrail bloqueado — sem chamar a API OpenAI
        3. Resposta com LLM real — exige OPENAI_API_KEY no ambiente ou .env
    """

    import textwrap
    import io
    import sys as _sys
    from dotenv import load_dotenv

    # Força UTF-8 no stdout para suportar caracteres especiais no Windows
    if hasattr(_sys.stdout, "reconfigure"):
        _sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # Carrega variáveis do .env localizado na mesma pasta deste arquivo
    _env_file = Path(__file__).parent / ".env"
    if _env_file.exists():
        load_dotenv(dotenv_path=_env_file)
        print(f"  [dotenv] .env carregado de: {_env_file}")

    SEP = "-" * 60

    print(f"\n{'=' * 60}")
    print("  LLM Connector - Testes de Validacao")
    print("  Genera AI - Sprint 2 - FIAP")
    print(f"{'=' * 60}\n")

    # ── Teste 1: Verificação de imports ───────────────────────────────────────
    print(f"[TESTE 1] Verificação de imports e sys.path")
    print(SEP)
    print(f"  RAIZ do repositório  : {RAIZ}")
    print(f"  Modelo configurado   : {MODELO}")
    print(f"  Temperatura          : {TEMPERATURA}")
    print(f"  Max tokens           : {MAX_TOKENS}")
    print(f"  ✅ Imports OK — agente_especialista, config_llm carregados\n")

    # ── Teste 2: Guardrail bloqueado (não chama a API) ────────────────────────
    print(f"[TESTE 2] Guardrail — pergunta de diagnóstico (deve ser bloqueada)")
    print(SEP)

    trechos_teste = [
        "O relatório indica predisposição genética leve ao diabetes tipo 2.",
        "A variante rs7903146 está associada a risco aumentado."
    ]

    try:
        # Passamos uma api_key fictícia — guardrail deve parar ANTES de chamar a API
        resultado_guardrail = responder_com_llm(
            pergunta="Eu tenho diabetes? Me diga meu diagnóstico.",
            trechos=trechos_teste,
            modo="paciente",
            api_key="sk-fake-key-guardrail-test",
        )
        status = resultado_guardrail["status"]
        categoria = resultado_guardrail["categoria"]
        resposta = resultado_guardrail["resposta"]

        if status == "bloqueado":
            print(f"  Status    : {status}")
            print(f"  Categoria : {categoria}")
            print(f"  Resposta  :\n{textwrap.indent(textwrap.fill(resposta, 55), '    ')}")
            print(f"  ✅ Guardrail funcionou — API OpenAI NÃO foi chamada\n")
        else:
            print(f"  ⚠️  Esperava status 'bloqueado', recebeu '{status}'\n")

    except Exception as e:
        print(f"  ❌ Erro inesperado no teste de guardrail: {e}\n")

    # ── Teste 3: Sem contexto (não chama a API) ───────────────────────────────
    print(f"[TESTE 3] Sem contexto — lista de trechos vazia (deve retornar sem_contexto)")
    print(SEP)

    try:
        resultado_sem_ctx = responder_com_llm(
            pergunta="Qual é a minha ancestralidade?",
            trechos=[],              # sem trechos — contexto vazio
            modo="paciente",
            api_key="sk-fake-key-no-context-test",
        )
        status_ctx = resultado_sem_ctx["status"]
        if status_ctx == "sem_contexto":
            print(f"  Status    : {status_ctx}")
            print(f"  Resposta  :\n{textwrap.indent(textwrap.fill(resultado_sem_ctx['resposta'], 55), '    ')}")
            print(f"  ✅ Contexto vazio tratado corretamente — API NÃO foi chamada\n")
        else:
            print(f"  ⚠️  Esperava 'sem_contexto', recebeu '{status_ctx}'\n")

    except Exception as e:
        print(f"  ❌ Erro inesperado no teste sem contexto: {e}\n")

    # ── Teste 4: LLM real (só executa se houver API key válida) ──────────────
    print(f"[TESTE 4] LLM Real — requer OPENAI_API_KEY no ambiente")
    print(SEP)

    try:
        api_key_real = get_api_key()   # lê do ambiente / .env
        print(f"  API Key   : {api_key_real[:8]}{'*' * (len(api_key_real) - 12)}{api_key_real[-4:]}")
        print(f"  Pergunta  : Qual é a minha ancestralidade?")
        print(f"  Enviando ao {MODELO}...")

        resultado_real = responder_com_llm(
            pergunta="Qual é a minha ancestralidade?",
            trechos=trechos_teste,
            modo="paciente",
            api_key=api_key_real,
        )
        status_real = resultado_real["status"]
        resposta_real = resultado_real["resposta"]

        print(f"\n  Status    : {status_real}")
        print(f"  Resposta  :\n")
        for linha in textwrap.wrap(resposta_real, width=58):
            print(f"    {linha}")
        print(f"\n  ✅ LLM real respondeu com sucesso\n")

    except ValueError:
        print(f"  ⏭️  OPENAI_API_KEY não configurada — teste 4 ignorado")
        print(f"     Configure no .env ou exporte a variável para testar o LLM real.\n")

    except PermissionError as e:
        print(f"  ❌ API Key inválida: {e}\n")

    except RuntimeError as e:
        print(f"  ❌ Limite de quota atingido: {e}\n")

    except Exception as e:
        print(f"  ❌ Erro inesperado: {e}\n")

    print(f"{'=' * 60}")
    print(f"  Testes concluídos.")
    print(f"{'=' * 60}\n")
