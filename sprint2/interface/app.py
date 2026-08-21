"""
app.py — Interface Principal do Genera AI
Integrante 4 · Sprint 2 · FIAP · Dasa

Responsabilidade:
    - Orquestrar a experiência conversacional completa
    - Conectar buscar_contexto() (Integrante 2) → responder_com_llm() (Integrante 4)
    - Exibir histórico, fontes, guardrails e disclaimers de forma clara e acessível

Execução:
    streamlit run sprint2/interface/app.py
    (a partir da raiz do repositório)
"""

import os
import sys
import json
import html
import subprocess
import shutil
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# ── Caminhos do repositório ───────────────────────────────────────────────────

# RAIZ aponta para a pasta raiz do repositório independentemente de onde o
# Streamlit é iniciado
RAIZ = Path(__file__).resolve().parents[2]

# Carrega variáveis do .env (se existir) antes de qualquer importação que dependa delas
_env_path = RAIZ / "sprint2" / "interface" / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)

# Adiciona sprint2/agente ao sys.path para que agente_especialista.py
# consiga importar 'prompts' e 'guardrails' sem prefixo de pacote (contrato do Integrante 3)
sys.path.insert(0, str(RAIZ / "sprint2" / "agente"))
sys.path.insert(0, str(RAIZ))

# Pasta de uploads temporários criada automaticamente se não existir
PASTA_UPLOADS = RAIZ / "sprint2" / "interface" / "uploads"
PASTA_UPLOADS.mkdir(parents=True, exist_ok=True)

# JSON de demonstração fornecido pelo Integrante 1
JSON_DEMO = RAIZ / "dados_estruturados.json"

# ── Configuração da página (deve ser o primeiro comando Streamlit) ────────────

st.set_page_config(
    page_title="Genera — Seu DNA Explicado",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS — tema escuro genômico ────────────────────────────────────────────────

st.markdown(
    """
    <style>
    /* === Variáveis de cor === */
    :root {
        --bg-principal:   #0d1117;
        --bg-card:        #161b22;
        --accent-roxo:    #7c3aed;
        --accent-verde:   #10b981;
        --texto-principal: #e6edf3;
        --texto-sec:      #8b949e;
        --borda:          #30363d;
    }

    /* === Fundo principal === */
    .stApp {
        background-color: var(--bg-principal) !important;
        color: var(--texto-principal) !important;
    }

    /* === Sidebar === */
    [data-testid="stSidebar"] {
        background-color: var(--bg-card) !important;
        border-right: 1px solid var(--borda);
    }
    [data-testid="stSidebar"] * {
        color: var(--texto-principal) !important;
    }

    /* === Cabeçalho da sidebar === */
    .sidebar-header {
        text-align: center;
        padding: 16px 0 8px 0;
        border-bottom: 1px solid var(--borda);
        margin-bottom: 16px;
    }
    .sidebar-header h2 {
        color: var(--accent-roxo) !important;
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .sidebar-header p {
        color: var(--texto-sec) !important;
        font-size: 0.78rem;
        margin: 4px 0 0 0;
    }

    /* === Bubble de chat — usuário === */
    .chat-user {
        background: #7c3aed18;
        border-left: 3px solid var(--accent-roxo);
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        color: var(--texto-principal);
        line-height: 1.6;
    }

    /* === Bubble de chat — assistente === */
    .chat-assistant {
        background: #10b98112;
        border-left: 3px solid var(--accent-verde);
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        color: var(--texto-principal);
        line-height: 1.6;
    }

    /* === Chat bloqueado (guardrail) === */
    .chat-blocked {
        background: #f59e0b12;
        border-left: 3px solid #f59e0b;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        color: var(--texto-principal);
        line-height: 1.6;
    }

    /* === Chat sem contexto === */
    .chat-no-context {
        background: #3b82f612;
        border-left: 3px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        color: var(--texto-principal);
        line-height: 1.6;
    }

    /* === Card de fonte === */
    .fonte-card {
        background: var(--bg-card);
        border: 1px solid var(--borda);
        font-size: 12px;
        padding: 8px 12px;
        border-radius: 6px;
        margin: 6px 0;
        color: var(--texto-principal);
    }

    /* === Banner de disclaimer === */
    .disclaimer-banner {
        background: #7c3aed12;
        border: 1px solid #7c3aed50;
        padding: 10px 16px;
        border-radius: 6px;
        margin-bottom: 16px;
        color: var(--texto-sec);
        font-size: 0.82rem;
        line-height: 1.5;
    }

    /* === Badge de modo (pill) === */
    .modo-badge-paciente {
        display: inline-block;
        background: #10b98120;
        color: #10b981;
        border: 1px solid #10b98150;
        border-radius: 20px;
        padding: 1px 8px;
        font-size: 0.70rem;
        font-weight: 600;
        margin-left: 6px;
        vertical-align: middle;
    }
    .modo-badge-tecnico {
        display: inline-block;
        background: #7c3aed20;
        color: #a78bfa;
        border: 1px solid #7c3aed50;
        border-radius: 20px;
        padding: 1px 8px;
        font-size: 0.70rem;
        font-weight: 600;
        margin-left: 6px;
        vertical-align: middle;
    }

    /* === Tag de seção nas fontes === */
    .secao-tag {
        display: inline-block;
        background: #7c3aed20;
        color: #a78bfa;
        border-radius: 4px;
        padding: 1px 6px;
        font-size: 11px;
        font-weight: 600;
        margin-bottom: 4px;
    }

    /* === Rodapé da sidebar === */
    .sidebar-footer {
        font-size: 0.68rem;
        color: var(--texto-sec) !important;
        text-align: center;
        padding: 12px 8px 4px 8px;
        border-top: 1px solid var(--borda);
        margin-top: 12px;
        line-height: 1.5;
    }

    /* === Área de chat com scroll === */
    .chat-area {
        max-height: 60vh;
        overflow-y: auto;
        padding-right: 4px;
    }

    /* === Inputs e botões — harmonizar com tema === */
    .stTextInput input, .stTextArea textarea {
        background: var(--bg-card) !important;
        border: 1px solid var(--borda) !important;
        color: var(--texto-principal) !important;
        border-radius: 6px !important;
    }
    .stButton > button {
        background: var(--bg-card) !important;
        color: var(--texto-principal) !important;
        border: 1px solid var(--borda) !important;
        border-radius: 6px !important;
        transition: border-color 0.2s, background 0.2s;
        width: 100%;
        text-align: left;
        padding: 6px 12px;
    }
    .stButton > button:hover {
        border-color: var(--accent-roxo) !important;
        background: #7c3aed12 !important;
    }

    /* === Radio buttons === */
    .stRadio > label {
        color: var(--texto-principal) !important;
    }

    /* Oculta marca d'água do Streamlit */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Estado da sessão — inicialização ─────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []          # histórico completo do chat
if "base_pronta" not in st.session_state:
    st.session_state.base_pronta = False    # base vetorial ChromaDB disponível?
if "nome_paciente" not in st.session_state:
    st.session_state.nome_paciente = None   # nome extraído do JSON
if "modo" not in st.session_state:
    st.session_state.modo = "paciente"      # modo de resposta padrão
if "api_key_input" not in st.session_state:
    st.session_state.api_key_input = ""     # chave digitada pelo usuário

# ── Funções auxiliares ────────────────────────────────────────────────────────

def extrair_nome_paciente(caminho_json: Path) -> str:
    """
    Tenta extrair o nome do paciente do JSON do relatório genético.
    Retorna 'Paciente' como fallback se o campo não for encontrado.
    """
    try:
        with open(caminho_json, encoding="utf-8") as f:
            dados = json.load(f)
        # Tenta diferentes caminhos comuns no JSON do Integrante 1
        nome = (
            dados.get("paciente", {}).get("nome")
            or dados.get("nome_paciente")
            or dados.get("identificacao", {}).get("nome")
            or dados.get("nome")
        )
        return str(nome) if nome else "Paciente"
    except Exception:
        return "Paciente"


def executar_pipeline(caminho_json: Path) -> bool:
    """
    Executa o pipeline_completo.py do Integrante 1 via subprocess para
    gerar embeddings e indexar o JSON na base vetorial ChromaDB.

    Args:
        caminho_json: caminho absoluto para o JSON a ser indexado.

    Returns:
        bool: True se o pipeline terminou com código 0, False caso contrário.
    """
    resultado = subprocess.run(
        [sys.executable, str(RAIZ / "sprint2" / "pipeline" / "pipeline_completo.py"),
         str(caminho_json)],
        capture_output=True,
        text=True,
        cwd=str(RAIZ),
    )
    return resultado.returncode == 0


def buscar_contexto_seguro(pergunta: str) -> dict:
    """
    Importa e chama buscar_contexto() do Integrante 2.
    Captura FileNotFoundError (base vetorial ausente) e retorna dict de erro.
    """
    try:
        # Importação tardia para evitar erro na inicialização quando a base
        # vetorial ainda não existe
        from sprint2.vetorial.buscar import buscar_contexto
        return buscar_contexto(pergunta, top_k=3, similaridade_minima=0.50)
    except FileNotFoundError as e:
        raise FileNotFoundError(str(e)) from e
    except Exception as e:
        raise RuntimeError(f"Erro na busca semântica: {e}") from e


def get_api_key_ui() -> str | None:
    """
    Obtém a API key disponível (env ou sidebar), retorna None se ausente.
    Não levanta exceção — deixa o app.py tratar o caso de ausência.
    """
    try:
        from llm_connector import get_api_key
        return get_api_key(st.session_state.api_key_input or None)
    except ValueError:
        return None


# ── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:

    # --- Seção 1: Cabeçalho ---
    st.markdown(
        """
        <div class="sidebar-header">
            <h2>🧬 Genera AI</h2>
            <p>Seu relatório genético explicado</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Seção 2: API Key ---
    st.markdown("#### 🔑 Configuração da API")
    chave_no_env = bool(os.environ.get("OPENAI_API_KEY", "").strip())

    if chave_no_env:
        st.success("✅ API Key configurada via variável de ambiente")
    else:
        api_key_digitada = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Obtenha em https://platform.openai.com/api-keys",
            key="api_key_input",
        )

    st.divider()

    # --- Seção 3: Relatório ---
    st.markdown("#### 📁 Relatório Genético")

    if not st.session_state.base_pronta:
        st.caption("Carregue seu relatório para começar")

        arquivo_upload = st.file_uploader(
            "Selecione o arquivo",
            type=["json", "pdf"],
            help="Formatos aceitos: JSON (indexação completa) ou PDF (apenas visualização)",
            label_visibility="collapsed",
        )

        col_demo, _ = st.columns([3, 1])
        with col_demo:
            if st.button("▶ Usar relatório de demonstração", use_container_width=True):
                if not JSON_DEMO.exists():
                    st.error("⚙️ Arquivo dados_estruturados.json não encontrado na raiz do projeto.")
                else:
                    with st.spinner("🧬 Indexando relatório de demonstração... (~15 segundos)"):
                        sucesso = executar_pipeline(JSON_DEMO)
                    if sucesso:
                        st.session_state.base_pronta = True
                        st.session_state.nome_paciente = extrair_nome_paciente(JSON_DEMO)
                        st.rerun()
                    else:
                        st.error("❌ Falha ao executar o pipeline. Verifique as dependências.")

        if arquivo_upload is not None:
            nome_seguro = Path(arquivo_upload.name).name  # descarta qualquer componente de diretório
            extensao = Path(nome_seguro).suffix.lower()
            destino = (PASTA_UPLOADS / nome_seguro).resolve()

            # Garante que o caminho resolvido continua dentro de PASTA_UPLOADS (evita path traversal)
            if not destino.is_relative_to(PASTA_UPLOADS.resolve()):
                st.error("❌ Nome de arquivo inválido.")
                st.stop()

            # Salva o arquivo temporariamente
            with open(destino, "wb") as f:
                f.write(arquivo_upload.getbuffer())

            if extensao == ".pdf":
                st.warning(
                    "📄 PDF recebido. Para indexação completa, converta para JSON com o "
                    "pipeline do Integrante 1 e carregue o arquivo .json resultante."
                )
            elif extensao == ".json":
                with st.spinner("🧬 Indexando seu relatório... (~15 segundos)"):
                    sucesso = executar_pipeline(destino)
                if sucesso:
                    st.session_state.base_pronta = True
                    st.session_state.nome_paciente = extrair_nome_paciente(destino)
                    # Remove arquivo temporário após indexação (privacidade)
                    try:
                        destino.unlink()
                    except Exception:
                        pass
                    st.rerun()
                else:
                    st.error("❌ Falha ao processar o JSON. Verifique o formato do arquivo.")

    else:
        # Base vetorial já está pronta
        st.success(
            f"✅ Relatório de **{st.session_state.nome_paciente}** carregado\n\n"
            "   25 trechos indexados"
        )
        if st.button("🔄 Trocar relatório", use_container_width=True):
            st.session_state.base_pronta = False
            st.session_state.messages = []
            st.session_state.nome_paciente = None
            st.rerun()

    st.divider()

    # --- Seção 4: Modo de resposta ---
    st.markdown("#### ⚙️ Modo de Explicação")
    modo_selecionado = st.radio(
        "Modo",
        options=["paciente", "tecnico"],
        format_func=lambda x: (
            "👤 Paciente (linguagem simples)"
            if x == "paciente"
            else "🔬 Técnico (detalhes clínicos)"
        ),
        index=0 if st.session_state.modo == "paciente" else 1,
        label_visibility="collapsed",
    )
    st.session_state.modo = modo_selecionado

    st.divider()

    # --- Seção 5: Perguntas frequentes ---
    st.markdown("#### 💡 Perguntas Frequentes")

    PERGUNTAS_RAPIDAS = [
        "🌍 De onde vêm meus ancestrais?",
        "❤️ Tenho risco cardiovascular?",
        "🧬 O que é haplogrupo e qual é o meu?",
        "🥗 Quais são minhas recomendações alimentares?",
        "⚠️ Quais são minhas condições de alto risco?",
    ]

    for pergunta_faq in PERGUNTAS_RAPIDAS:
        if st.button(pergunta_faq, use_container_width=True, key=f"faq_{pergunta_faq[:20]}"):
            st.session_state.pergunta_rapida = pergunta_faq

    st.divider()

    # --- Seção 6: Ações ---
    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # --- Rodapé da sidebar ---
    st.markdown(
        """
        <div class="sidebar-footer">
            🔒 Seus dados são processados localmente.<br>
            Nenhuma informação genética é armazenada<br>
            além desta sessão. | LGPD Art. 11
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── ÁREA PRINCIPAL ────────────────────────────────────────────────────────────

# Título principal
st.markdown(
    """
    <h1 style="color: #e6edf3; font-weight: 800; margin-bottom: 0;">
        🧬 Genera AI
    </h1>
    <p style="color: #8b949e; margin-top: 4px; margin-bottom: 16px;">
        Interpretação inteligente do seu relatório genético · Powered by GPT-4.1 Mini
    </p>
    """,
    unsafe_allow_html=True,
)

# Banner de disclaimer — sempre visível
st.markdown(
    """
    <div class="disclaimer-banner">
        ⚠️&nbsp; <strong>Este assistente é informativo e não substitui avaliação médica.</strong><br>
        As respostas são baseadas exclusivamente no seu relatório genético.
        Consulte sempre um médico geneticista para orientação personalizada.
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Renderização do histórico de chat ─────────────────────────────────────────

def badge_modo(modo: str) -> str:
    """Retorna HTML da pill colorida indicando o modo de resposta."""
    if modo == "tecnico":
        return '<span class="modo-badge-tecnico">🔬 técnico</span>'
    return '<span class="modo-badge-paciente">👤 paciente</span>'


for msg in st.session_state.messages:
    role = msg["role"]

    if role == "user":
        st.markdown(
            f"""
            <div class="chat-user">
                <b>👤 Você</b><br>
                {html.escape(msg["content"])}
            </div>
            """,
            unsafe_allow_html=True,
        )

    elif role == "assistant":
        status = msg.get("status", "respondido")
        modo_msg = msg.get("modo", "paciente")
        fontes_msg = msg.get("fontes", [])

        # Escolhe a classe CSS conforme o status do guardrail
        if status == "bloqueado":
            classe_css = "chat-blocked"
            icone = "🚫"
        elif status == "sem_contexto":
            classe_css = "chat-no-context"
            icone = "ℹ️"
        else:
            classe_css = "chat-assistant"
            icone = "🧬"

        st.markdown(
            f"""
            <div class="{classe_css}">
                <b>{icone} Genera AI</b> {badge_modo(modo_msg)}<br><br>
                {html.escape(msg["content"]).replace(chr(10), "<br>")}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Expander de fontes — apenas para respostas normais com fontes disponíveis
        if status == "respondido" and fontes_msg:
            n_fontes = len(fontes_msg)
            with st.expander(f"📄 Fontes utilizadas ({n_fontes} trecho{'s' if n_fontes > 1 else ''} do relatório)"):
                for fonte in fontes_msg:
                    # Garante compatibilidade: fonte pode ser str (legado) ou dict (atual)
                    if isinstance(fonte, dict):
                        conteudo   = fonte.get("conteudo", str(fonte))
                        secao      = fonte.get("secao", "—")
                        origem     = fonte.get("fonte", "—")
                        similaridade = fonte.get("similaridade", 0.0)
                    else:
                        conteudo   = str(fonte)
                        secao      = "—"
                        origem     = "—"
                        similaridade = 0.0

                    # Trunca o conteúdo em 200 caracteres
                    trecho_exibido = conteudo[:200] + "..." if len(conteudo) > 200 else conteudo

                    st.markdown(
                        f"""
                        <div class="fonte-card">
                            <span class="secao-tag">{secao}</span><br>
                            {trecho_exibido}<br>
                            <small style="color:#8b949e;">📌 {origem}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    # Barra de relevância (similaridade cosseno)
                    st.progress(
                        float(similaridade),
                        text=f"Relevância: {similaridade:.0%}",
                    )

# ── Input de chat e lógica de envio ──────────────────────────────────────────

pergunta_input = st.chat_input("Pergunte sobre seu relatório genético...")

# Substitui o input pelo botão de pergunta rápida, se clicado
if "pergunta_rapida" in st.session_state:
    pergunta_input = st.session_state.pop("pergunta_rapida")

if pergunta_input:
    pergunta_input = pergunta_input.strip()

    # Guarda 1: base vetorial não está pronta
    if not st.session_state.base_pronta:
        st.warning("📂 Carregue seu relatório primeiro (sidebar esquerda).")
        st.stop()

    # Guarda 2: API key ausente
    api_key = get_api_key_ui()
    if not api_key:
        st.error("🔑 Insira sua OpenAI API Key na sidebar para continuar.")
        st.stop()

    # Adiciona mensagem do usuário ao histórico
    st.session_state.messages.append({
        "role":    "user",
        "content": pergunta_input,
    })

    with st.spinner("🧬 Analisando seu relatório..."):
        try:
            # Etapa a: busca semântica (Integrante 2)
            resultado_busca = buscar_contexto_seguro(pergunta_input)

            # Etapa b: extrai lista de strings de conteúdo para o agente
            trechos_texto = [t["conteudo"] for t in resultado_busca["trechos"]]

            # Etapa c: agente + LLM real (Integrante 3 + Integrante 4)
            from llm_connector import responder_com_llm
            resultado_llm = responder_com_llm(
                pergunta=pergunta_input,
                trechos=trechos_texto,
                modo=st.session_state.modo,
                api_key=api_key,
            )

            # Adiciona resposta ao histórico com metadados completos para renderização
            st.session_state.messages.append({
                "role":      "assistant",
                "content":   resultado_llm["resposta"],
                "status":    resultado_llm["status"],
                "categoria": resultado_llm["categoria"],
                # fontes: dicts completos (conteudo, secao, fonte, similaridade)
                "fontes":    resultado_busca["trechos"],
                "modo":      st.session_state.modo,
            })

        except FileNotFoundError:
            st.error(
                "⚙️ Base vetorial não encontrada. Execute o pipeline primeiro "
                "ou carregue um relatório pela sidebar."
            )
            # Remove a mensagem do usuário que foi adicionada antes do erro
            st.session_state.messages.pop()

        except PermissionError:
            st.error("🔑 Chave OpenAI inválida. Verifique e tente novamente.")
            st.session_state.messages.pop()

        except RuntimeError as e:
            msg_err = str(e)
            if "quota" in msg_err.lower() or "limit" in msg_err.lower():
                st.error("💳 Limite de uso da API atingido. Verifique seu plano OpenAI.")
            else:
                st.error(f"❌ Ocorreu um erro inesperado. Tente novamente.\n\n`{msg_err}`")
            st.session_state.messages.pop()

        except Exception as e:
            st.error(f"❌ Ocorreu um erro inesperado. Tente novamente.\n\n`{e}`")
            st.session_state.messages.pop()

    # Recarrega a página para exibir o novo par de mensagens no histórico
    st.rerun()
