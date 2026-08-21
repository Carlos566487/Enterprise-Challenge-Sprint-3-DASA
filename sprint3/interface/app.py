"""
Genera AI — Interface da Sprint 3
FIAP · Enterprise Challenge DASA / Genera

Objetivos:
- evoluir a interface conversacional da Sprint 2;
- criar dashboard com riscos e ancestralidade;
- integrar RAG, NLP e resumos automáticos;
- oferecer linguagem acessível e responsável;
- funcionar bem em desktop e mobile.

Execução:
    streamlit run sprint3/interface/app.py
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv


# =============================================================================
# CAMINHOS DO PROJETO
# =============================================================================

RAIZ = Path(__file__).resolve().parents[2]

JSON_DEMO = RAIZ / "dados_estruturados.json"

PASTA_UPLOADS = (
    RAIZ
    / "sprint3"
    / "interface"
    / "uploads"
)

PASTA_UPLOADS.mkdir(
    parents=True,
    exist_ok=True,
)


# =============================================================================
# VARIÁVEIS DE AMBIENTE
# =============================================================================

for arquivo_env in (
    RAIZ / "sprint3" / "interface" / ".env",
    RAIZ / "sprint2" / "interface" / ".env",
):
    if arquivo_env.exists():
        load_dotenv(
            dotenv_path=arquivo_env,
            override=False,
        )


# =============================================================================
# IMPORTS DAS OUTRAS SPRINTS
# =============================================================================

sys.path.insert(
    0,
    str(RAIZ),
)

sys.path.insert(
    0,
    str(
        RAIZ
        / "sprint2"
        / "interface"
    ),
)

sys.path.insert(
    0,
    str(
        RAIZ
        / "sprint2"
        / "agente"
    ),
)

sys.path.insert(
    0,
    str(
        RAIZ
        / "sprint3"
        / "nlp"
    ),
)


try:
    from resumos_automaticos import (
        formatar_resumo_interacoes,
        gerar_resumo_interacoes,
        gerar_resumo_relatorio,
    )
except Exception:
    gerar_resumo_relatorio = None
    gerar_resumo_interacoes = None
    formatar_resumo_interacoes = None


try:
    from nlp_simplificacao import simplificar_texto
except Exception:
    simplificar_texto = None


# =============================================================================
# CONFIGURAÇÃO DO STREAMLIT
# =============================================================================

st.set_page_config(
    page_title="Genera AI — Seu DNA explicado",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="auto",
)


# =============================================================================
# DESIGN SYSTEM
# =============================================================================

st.markdown(
    """
    <style>

    :root {
        --bg: #f6f8fb;
        --surface: #ffffff;
        --surface-soft: #f1f4f8;

        --primary: #5b4dd8;
        --primary-hover: #493bc5;
        --primary-soft: #efedff;

        --text: #172033;
        --muted: #667085;
        --border: #e4e8ef;

        --success: #267a62;
        --success-soft: #eaf7f2;

        --attention: #9a6a17;
        --attention-soft: #fff7e7;

        --info: #3567a8;
        --info-soft: #eef5ff;

        --shadow:
            0 8px 24px rgba(
                20,
                30,
                55,
                0.06
            );
    }


    /* ==============================================================
       ESTRUTURA
       ============================================================== */

    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    [data-testid="stAppViewContainer"] {
        background: var(--bg);
    }

    [data-testid="stAppViewContainer"] > .main {
        background: var(--bg);
    }

    .block-container {
        max-width: 1240px;
        padding-top: 1.6rem;
        padding-bottom: 5rem;
    }


    /* ==============================================================
       SIDEBAR
       ============================================================== */

    [data-testid="stSidebar"] {
        background: var(--surface);
        border-right:
            1px solid
            var(--border);
    }

    [data-testid="stSidebar"] {
        color: var(--text);
    }

    [data-testid="stSidebar"]
    label {
        color: var(--text);
    }


    /* ==============================================================
       TEXTO
       ============================================================== */

    h1,
    h2,
    h3,
    h4,
    p,
    label {
        color: var(--text);
    }

    .eyebrow {
        color: var(--primary);

        text-transform: uppercase;

        letter-spacing: .08em;

        font-size: .72rem;

        font-weight: 800;

        margin-bottom: 4px;
    }

    .page-title {
        font-size:
            clamp(
                1.65rem,
                3vw,
                2.35rem
            );

        line-height: 1.12;

        font-weight: 800;

        letter-spacing: -.035em;

        margin: 0;
    }

    .page-subtitle {
        color: var(--muted);

        margin-top: 8px;

        margin-bottom: 22px;

        max-width: 760px;

        line-height: 1.55;
    }


    /* ==============================================================
       MARCA
       ============================================================== */

    .brand {
        display: flex;

        align-items: center;

        gap: 10px;

        padding:
            6px
            0
            18px;
    }

    .brand-mark {
        width: 42px;

        height: 42px;

        border-radius: 13px;

        background:
            var(--primary-soft);

        display: flex;

        align-items: center;

        justify-content: center;

        font-size: 22px;
    }

    .brand h2 {
        font-size: 1.15rem;

        margin: 0;

        line-height: 1.1;
    }

    .brand p {
        color: var(--muted);

        margin:
            3px
            0
            0;

        font-size: .76rem;
    }


    /* ==============================================================
       DISCLAIMER
       ============================================================== */

    .disclaimer {
        background: var(--info-soft);

        border:
            1px solid
            #d9e7fb;

        border-radius: 14px;

        padding:
            12px
            15px;

        color: #35577d;

        font-size: .84rem;

        line-height: 1.5;

        margin:
            0
            0
            20px;
    }


    /* ==============================================================
       CARDS
       ============================================================== */

    .metric-card,
    .content-card,
    .result-card,
    .summary-card,
    .empty-card {
        background:
            var(--surface);

        border:
            1px solid
            var(--border);

        box-shadow:
            var(--shadow);

        border-radius: 18px;
    }


    /* Métricas */

    .metric-card {
        padding:
            18px
            18px
            16px;

        min-height: 126px;

        margin-bottom: 10px;
    }

    .metric-label {
        color: var(--muted);

        font-size: .77rem;

        font-weight: 700;

        text-transform: uppercase;

        letter-spacing: .04em;
    }

    .metric-value {
        font-size: 2rem;

        font-weight: 800;

        line-height: 1.05;

        margin:
            8px
            0
            5px;

        color: var(--text);
    }

    .metric-help {
        color: var(--muted);

        font-size: .79rem;

        line-height: 1.35;
    }


    /* Títulos de seção */

    .section-title {
        display: flex;

        align-items: baseline;

        justify-content:
            space-between;

        gap: 12px;

        margin:
            28px
            0
            12px;
    }

    .section-title h3 {
        margin: 0;

        font-size: 1.05rem;
    }

    .section-title span {
        color: var(--muted);

        font-size: .78rem;
    }


    /* Resultado genético */

    .result-card {
        padding: 18px;

        min-height: 248px;

        margin-bottom: 14px;
    }

    .result-top {
        display: flex;

        justify-content:
            space-between;

        align-items:
            flex-start;

        gap: 10px;
    }

    .result-card h4 {
        margin: 0;

        font-size: 1rem;

        line-height: 1.35;
    }

    .result-category {
        color: var(--muted);

        font-size: .75rem;

        margin:
            5px
            0
            12px;
    }

    .result-description {
        color: #465269;

        font-size: .86rem;

        line-height: 1.55;

        margin:
            12px
            0;
    }

    .result-note {
        background:
            var(--surface-soft);

        color: #58647a;

        padding:
            10px
            11px;

        border-radius: 10px;

        font-size: .76rem;

        line-height: 1.45;
    }


    /* Pills de atenção */

    .risk-pill {
        display: inline-flex;

        border-radius: 999px;

        padding:
            5px
            9px;

        font-size: .7rem;

        font-weight: 800;

        white-space: nowrap;
    }

    .risk-high {
        background:
            var(--attention-soft);

        color:
            var(--attention);

        border:
            1px solid
            #f2dfb7;
    }

    .risk-medium {
        background:
            var(--info-soft);

        color:
            var(--info);

        border:
            1px solid
            #d7e5f8;
    }

    .risk-low {
        background:
            var(--success-soft);

        color:
            var(--success);

        border:
            1px solid
            #cfeade;
    }


    /* ==============================================================
       ANCESTRALIDADE
       ============================================================== */

    .ancestry-row {
        margin-bottom: 15px;
    }

    .ancestry-meta {
        display: flex;

        justify-content:
            space-between;

        gap: 10px;

        margin-bottom: 6px;

        font-size: .83rem;
    }

    .ancestry-region {
        font-weight: 700;
    }

    .ancestry-value {
        color: var(--muted);

        font-weight: 700;
    }

    .ancestry-track {
        width: 100%;

        height: 9px;

        border-radius: 999px;

        background: #e9edf3;

        overflow: hidden;
    }

    .ancestry-fill {
        height: 100%;

        border-radius: 999px;

        background:
            linear-gradient(
                90deg,
                #7265e8,
                #9a91ef
            );
    }


    /* ==============================================================
       RESUMO
       ============================================================== */

    .content-card,
    .summary-card {
        padding: 20px;
    }

    .summary-lead {
        font-size: 1rem;

        line-height: 1.6;

        color: #39445a;

        margin-bottom: 14px;
    }

    .mini-list {
        margin: 0;

        padding-left: 1.1rem;

        color: #4c5870;

        font-size: .86rem;

        line-height: 1.65;
    }


    /* ==============================================================
       CHAT
       ============================================================== */

    .chat-user,
    .chat-assistant,
    .chat-blocked,
    .chat-no-context {
        padding:
            14px
            16px;

        border-radius: 14px;

        margin:
            10px
            0;

        line-height: 1.55;

        font-size: .9rem;

        border:
            1px solid
            var(--border);
    }

    .chat-user {
        margin-left: 8%;

        background:
            var(--primary-soft);

        border-color:
            #ddd8ff;
    }

    .chat-assistant {
        margin-right: 8%;

        background:
            var(--surface);
    }

    .chat-blocked {
        background:
            var(--attention-soft);

        border-color:
            #f1ddb1;
    }

    .chat-no-context {
        background:
            var(--info-soft);

        border-color:
            #d8e6f8;
    }

    .chat-name {
        font-size: .75rem;

        font-weight: 800;

        color: var(--muted);

        margin-bottom: 5px;
    }


    /* Fontes */

    .source-card {
        background:
            var(--surface-soft);

        border:
            1px solid
            var(--border);

        border-radius: 12px;

        padding:
            10px
            12px;

        margin:
            7px
            0;

        font-size: .78rem;

        line-height: 1.45;

        color: #4e596d;
    }


    /* ==============================================================
       ESTADO VAZIO
       ============================================================== */

    .empty-card {
        padding:
            34px
            24px;

        text-align: center;

        color: var(--muted);
    }

    .empty-card .icon {
        font-size: 2rem;

        margin-bottom: 8px;
    }


    /* ==============================================================
       PRIVACIDADE
       ============================================================== */

    .privacy-note {
        color: var(--muted);

        font-size: .72rem;

        line-height: 1.45;

        border-top:
            1px solid
            var(--border);

        margin-top: 18px;

        padding-top: 14px;
    }


    /* ==============================================================
       BOTÕES
       ============================================================== */

    .stButton > button {
        border-radius: 11px;

        border:
            1px solid
            var(--border);

        background:
            var(--surface);

        color: var(--text);

        font-weight: 650;

        min-height: 40px;
    }

    .stButton > button:hover {
        border-color:
            #bbb4fa;

        color:
            var(--primary);

        background:
            #faf9ff;
    }


    /* ==============================================================
       INPUTS
       ============================================================== */

    .stTextInput input,
    .stTextArea textarea {
        border-radius:
            11px !important;

        border-color:
            var(--border) !important;

        background:
            #ffffff !important;

        color:
            var(--text) !important;
    }

    [data-testid="stSidebar"]
    [data-baseweb="select"] > div,

    [data-baseweb="select"] > div {
        border-radius:
            11px !important;

        border-color:
            #d8dee8 !important;

        background:
            #ffffff !important;

        color:
            #172033 !important;
    }

    [data-baseweb="select"] span,
    [data-baseweb="select"] input {
        color:
            #172033 !important;
    }


    /* File uploader */

    [data-testid="stFileUploaderDropzone"] {
        background:
            #ffffff !important;

        border:
            1px dashed
            #d8dee8 !important;

        border-radius:
            12px !important;
    }

    [data-testid="stFileUploaderDropzone"] * {
        color:
            #172033 !important;
    }

    [data-testid="stFileUploaderDropzone"] button {
        background:
            #f6f8fb !important;

        color:
            #172033 !important;

        border:
            1px solid
            #d8dee8 !important;
    }


    /* ==============================================================
       CHAT INPUT
       ============================================================== */

    [data-testid="stChatInput"] {
        background:
            #ffffff !important;

        border:
            1px solid
            var(--border) !important;

        border-radius:
            14px !important;
    }

    [data-testid="stChatInput"] textarea {
        color:
            var(--text) !important;
    }


    /* ==============================================================
       MENU MOBILE PRÓPRIO
       ============================================================== */

    .st-key-mobile_nav {
        display: none;
    }


    /* ==============================================================
       HEADER
       ============================================================== */

    header {
        background:
            transparent !important;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

/* ==============================================================
   BOTÕES DE ABRIR E FECHAR A SIDEBAR
   ============================================================== */

/* Botão para FECHAR a sidebar quando ela está aberta */
[data-testid="stSidebarCollapseButton"] {
    opacity: 1 !important;
    visibility: visible !important;
}

/* Botão para ABRIR a sidebar quando ela está fechada */
[data-testid="stExpandSidebarButton"] {
    opacity: 1 !important;
    visibility: visible !important;
}


/* Fundo dos dois botões */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapseButton"],
[data-testid="stExpandSidebarButton"] button,
[data-testid="stExpandSidebarButton"] {
    background: #172033 !important;
    border: 1px solid #172033 !important;
    border-radius: 10px !important;

    box-shadow:
        0 4px 14px
        rgba(20, 30, 55, 0.22) !important;
}


/* Ícones dos dois botões */
[data-testid="stSidebarCollapseButton"] *,
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapseButton"] svg path,
[data-testid="stSidebarCollapseButton"] span,

[data-testid="stExpandSidebarButton"] *,
[data-testid="stExpandSidebarButton"] svg,
[data-testid="stExpandSidebarButton"] svg path,
[data-testid="stExpandSidebarButton"] span {
    color: #ffffff !important;
    fill: #ffffff !important;
    stroke: #ffffff !important;
    opacity: 1 !important;
}


/* Hover */
[data-testid="stSidebarCollapseButton"]:hover,
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stExpandSidebarButton"]:hover,
[data-testid="stExpandSidebarButton"] button:hover {
    background: #5b4dd8 !important;
    border-color: #5b4dd8 !important;
}

    /* ==============================================================
       RESPONSIVIDADE
       ============================================================== */

    @media (
        max-width: 768px
    ) {

        .block-container {
            padding-top: .7rem;

            padding-left: 1rem;

            padding-right: 1rem;
        }

        .st-key-mobile_nav {
            display: block !important;

            position: sticky;

            top: 0;

            z-index: 1000;

            margin-bottom: 12px;

            background:
                rgba(
                    246,
                    248,
                    251,
                    0.96
                );

            backdrop-filter:
                blur(10px);

            padding:
                4px
                0
                8px;
        }

        .st-key-mobile_nav button {
            background:
                #172033 !important;

            color:
                #ffffff !important;

            border:
                1px solid
                #172033 !important;

            border-radius:
                12px !important;

            min-height:
                44px !important;

            font-weight:
                700 !important;

            box-shadow:
                0 4px 14px
                rgba(
                    20,
                    30,
                    55,
                    .16
                ) !important;
        }

        .st-key-mobile_nav button p,
        .st-key-mobile_nav button span,
        .st-key-mobile_nav button svg {
            color:
                #ffffff !important;

            fill:
                #ffffff !important;

            stroke:
                #ffffff !important;
        }

        .metric-card {
            min-height: auto;
        }

        .result-card {
            min-height: auto;
        }

        .chat-user {
            margin-left: 2%;
        }

        .chat-assistant {
            margin-right: 2%;
        }

        .section-title {
            align-items:
                flex-start;

            flex-direction:
                column;

            gap: 4px;
        }

        .result-top {
            gap: 8px;
        }

        .risk-pill {
            font-size: .64rem;

            padding:
                4px
                7px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# ESTADO DA SESSÃO
# =============================================================================

VALORES_PADRAO = {
    "pagina": "Visão geral",
    "dados": None,
    "arquivo_relatorio": None,
    "relatorio_hash": None,
    "messages": [],
    "assistente_preparado": False,
    "modo_resposta": "Paciente",
    "resumo_relatorio": None,
    "erro_relatorio": None,
    "api_key_session": os.getenv(
        "OPENAI_API_KEY",
        "",
    ),
}


for chave, valor in VALORES_PADRAO.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor


PAGINAS = [
    "Visão geral",
    "Meus resultados",
    "Assistente",
    "Histórico",
]


# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

def escapar(
    valor: Any,
) -> str:
    if valor is None:
        return ""

    return html.escape(
        str(valor)
    )


def carregar_json(
    caminho: Path,
) -> dict[str, Any]:

    with caminho.open(
        "r",
        encoding="utf-8",
    ) as arquivo:
        dados = json.load(
            arquivo
        )

    if not isinstance(
        dados,
        dict,
    ):
        raise ValueError(
            "O relatório deve conter "
            "um objeto JSON na raiz."
        )

    return dados


def hash_bytes(
    conteudo: bytes,
) -> str:

    return hashlib.sha256(
        conteudo
    ).hexdigest()[:16]


def salvar_upload(
    nome: str,
    conteudo: bytes,
) -> Path:

    extensao = (
        Path(nome)
        .suffix
        .lower()
    )

    if extensao != ".json":
        raise ValueError(
            "O relatório deve estar "
            "em formato JSON."
        )

    identificador = hash_bytes(
        conteudo
    )

    destino = (
        PASTA_UPLOADS
        / f"relatorio_{identificador}.json"
    )

    if not destino.exists():
        destino.write_bytes(
            conteudo
        )

    return destino


def processar_upload(
    upload: Any,
) -> None:

    if upload is None:
        return

    conteudo = upload.getvalue()

    identificador = hash_bytes(
        conteudo
    )

    # Evita reprocessar o mesmo arquivo
    # em todo rerun do Streamlit.
    if (
        identificador
        == st.session_state.relatorio_hash
    ):
        return

    caminho = salvar_upload(
        upload.name,
        conteudo,
    )

    dados_upload = carregar_json(
        caminho
    )

    st.session_state.dados = (
        dados_upload
    )

    st.session_state.arquivo_relatorio = (
        str(caminho)
    )

    st.session_state.relatorio_hash = (
        identificador
    )

    st.session_state.resumo_relatorio = None

    st.session_state.messages = []

    st.session_state.assistente_preparado = False

    st.session_state.erro_relatorio = None


def obter_primeiro(
    dados: dict[str, Any],
    *chaves: str,
    padrao: Any = None,
) -> Any:

    for chave in chaves:
        if (
            chave in dados
            and dados[chave]
            not in (
                None,
                "",
                [],
                {},
            )
        ):
            return dados[chave]

    return padrao


def obter_nome_paciente(
    dados: dict[str, Any],
) -> str:

    paciente = dados.get(
        "paciente",
        {},
    )

    if isinstance(
        paciente,
        dict,
    ):
        nome = obter_primeiro(
            paciente,
            "nome",
            "nome_completo",
            "name",
            padrao="Paciente",
        )

    else:
        nome = "Paciente"

    primeiro_nome = (
        str(nome)
        .strip()
        .split(" ")[0]
    )

    return (
        primeiro_nome
        or "Paciente"
    )


def obter_resultados(
    dados: dict[str, Any],
) -> list[dict[str, Any]]:

    resultados = dados.get(
        "resultados",
        [],
    )

    if isinstance(
        resultados,
        list,
    ):
        return [
            item
            for item
            in resultados
            if isinstance(
                item,
                dict,
            )
        ]

    return []


def obter_ancestralidade(
    dados: dict[str, Any],
) -> list[dict[str, Any]]:

    ancestralidade = dados.get(
        "ancestralidade",
        [],
    )

    if isinstance(
        ancestralidade,
        list,
    ):
        return [
            item
            for item
            in ancestralidade
            if isinstance(
                item,
                dict,
            )
        ]

    if isinstance(
        ancestralidade,
        dict,
    ):

        for chave in (
            "regioes",
            "resultados",
            "composicao",
        ):

            valor = ancestralidade.get(
                chave
            )

            if isinstance(
                valor,
                list,
            ):
                return [
                    item
                    for item
                    in valor
                    if isinstance(
                        item,
                        dict,
                    )
                ]

    return []


def normalizar_risco(
    valor: Any,
) -> str:

    texto = (
        str(
            valor
            or ""
        )
        .strip()
        .lower()
    )

    termos_alto = (
        "alto",
        "alta",
        "elevado",
        "elevada",
        "high",
        "aumentado",
        "aumentada",
        "maior",
    )

    termos_medio = (
        "medio",
        "médio",
        "media",
        "média",
        "moderado",
        "moderada",
        "medium",
        "intermediario",
        "intermediário",
        "intermediaria",
        "intermediária",
    )

    termos_baixo = (
        "baixo",
        "baixa",
        "reduzido",
        "reduzida",
        "low",
        "menor",
    )

    if any(
        termo in texto
        for termo
        in termos_alto
    ):
        return "alto"

    if any(
        termo in texto
        for termo
        in termos_medio
    ):
        return "medio"

    if any(
        termo in texto
        for termo
        in termos_baixo
    ):
        return "baixo"

    return "indefinido"


def obter_risco_resultado(
    resultado: dict[str, Any],
) -> str:

    valor = obter_primeiro(
        resultado,
        "risco",
        "nivel_risco",
        "classificacao",
        "predisposicao",
        "risk",
        padrao="",
    )

    return normalizar_risco(
        valor
    )


def rotulo_risco(
    risco: str,
) -> str:

    mapa = {
        "alto":
            "Maior atenção",

        "medio":
            "Atenção moderada",

        "baixo":
            "Menor atenção",

        "indefinido":
            "Informativo",
    }

    return mapa.get(
        risco,
        "Informativo",
    )


def classe_risco(
    risco: str,
) -> str:

    mapa = {
        "alto":
            "risk-high",

        "medio":
            "risk-medium",

        "baixo":
            "risk-low",

        "indefinido":
            "risk-medium",
    }

    return mapa.get(
        risco,
        "risk-medium",
    )


def nome_resultado(
    resultado: dict[str, Any],
) -> str:

    return str(
        obter_primeiro(
            resultado,
            "doenca",
            "condicao",
            "caracteristica",
            "titulo",
            "nome",
            padrao=(
                "Resultado genético"
            ),
        )
    )


def categoria_resultado(
    resultado: dict[str, Any],
) -> str:

    return str(
        obter_primeiro(
            resultado,
            "categoria",
            "tipo",
            "grupo",
            padrao=(
                "Perfil genético"
            ),
        )
    )


def descricao_resultado(
    resultado: dict[str, Any],
) -> str:

    return str(
        obter_primeiro(
            resultado,
            "descricao_simples",
            "explicacao_simples",
            "descricao",
            "interpretacao",
            "descricao_tecnica",
            padrao=(
                "Consulte os detalhes "
                "deste resultado no relatório."
            ),
        )
    )


def recomendacao_resultado(
    resultado: dict[str, Any],
) -> str:

    return str(
        obter_primeiro(
            resultado,
            "recomendacao",
            "orientacao",
            "impacto_pratico",
            padrao=(
                "Este resultado é informativo "
                "e deve ser interpretado junto "
                "ao contexto clínico e familiar."
            ),
        )
    )


def para_percentual(
    valor: Any,
) -> float:

    try:
        numero = float(
            str(valor)
            .replace(
                "%",
                "",
            )
            .replace(
                ",",
                ".",
            )
            .strip()
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0.0

    if (
        0
        <= numero
        <= 1
    ):
        numero *= 100

    return max(
        0.0,
        min(
            numero,
            100.0,
        ),
    )


def dados_regiao_ancestralidade(
    item: dict[str, Any],
) -> tuple[str, float]:

    regiao = obter_primeiro(
        item,
        "regiao",
        "origem",
        "populacao",
        "nome",
        padrao="Outra região",
    )

    percentual = obter_primeiro(
        item,
        "percentual",
        "porcentagem",
        "valor",
        "percentage",
        padrao=0,
    )

    return (
        str(regiao),
        para_percentual(
            percentual
        ),
    )


def contagem_riscos(
    resultados: list[
        dict[str, Any]
    ],
) -> dict[str, int]:

    contagem = {
        "alto": 0,
        "medio": 0,
        "baixo": 0,
        "indefinido": 0,
    }

    for resultado in resultados:

        risco = (
            obter_risco_resultado(
                resultado
            )
        )

        contagem[risco] = (
            contagem.get(
                risco,
                0,
            )
            + 1
        )

    return contagem


# =============================================================================
# COMPONENTES VISUAIS
# =============================================================================

def cabecalho_pagina(
    eyebrow: str,
    titulo: str,
    subtitulo: str,
) -> None:

    st.html(
        f"""
        <div>

            <div class="eyebrow">
                {escapar(eyebrow)}
            </div>

            <h1 class="page-title">
                {escapar(titulo)}
            </h1>

            <p class="page-subtitle">
                {escapar(subtitulo)}
            </p>

        </div>
        """
    )


def disclaimer() -> None:

    st.html(
        """
        <div class="disclaimer">

            <strong>
                Informação importante:
            </strong>

            esta experiência apresenta
            interpretações educativas baseadas
            exclusivamente no relatório genético
            analisado.

            Os resultados representam
            predisposições e características
            genéticas e

            <strong>
                não constituem diagnóstico médico.
            </strong>

            Para decisões relacionadas à saúde,
            procure um profissional qualificado.

        </div>
        """
    )


def card_metrica(
    titulo: str,
    valor: Any,
    ajuda: str,
) -> None:

    st.html(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                {escapar(titulo)}
            </div>

            <div class="metric-value">
                {escapar(valor)}
            </div>

            <div class="metric-help">
                {escapar(ajuda)}
            </div>

        </div>
        """
    )


def titulo_secao(
    titulo: str,
    complemento: str = "",
) -> None:

    st.html(
        f"""
        <div class="section-title">

            <h3>
                {escapar(titulo)}
            </h3>

            <span>
                {escapar(complemento)}
            </span>

        </div>
        """
    )


def card_resultado(
    resultado: dict[str, Any],
) -> None:

    risco = (
        obter_risco_resultado(
            resultado
        )
    )

    nome = nome_resultado(
        resultado
    )

    categoria = (
        categoria_resultado(
            resultado
        )
    )

    descricao = (
        descricao_resultado(
            resultado
        )
    )

    recomendacao = (
        recomendacao_resultado(
            resultado
        )
    )

    st.html(
        (
            f'<div class="result-card">'

            f'<div class="result-top">'

            f'<div>'

            f'<h4>'
            f'{escapar(nome)}'
            f'</h4>'

            f'<div class="result-category">'
            f'{escapar(categoria)}'
            f'</div>'

            f'</div>'

            f'<span class="risk-pill '
            f'{classe_risco(risco)}">'
            f'{escapar(rotulo_risco(risco))}'
            f'</span>'

            f'</div>'

            f'<div class="result-description">'
            f'{escapar(descricao)}'
            f'</div>'

            f'<div class="result-note">'

            f'<strong>'
            f'Orientação:'
            f'</strong> '

            f'{escapar(recomendacao)}'

            f'</div>'

            f'</div>'
        )
    )


def barra_ancestralidade(
    regiao: str,
    percentual: float,
) -> None:

    st.html(
        (
            f'<div class="ancestry-row">'

            f'<div class="ancestry-meta">'

            f'<span class="ancestry-region">'
            f'{escapar(regiao)}'
            f'</span>'

            f'<span class="ancestry-value">'
            f'{percentual:.1f}%'
            f'</span>'

            f'</div>'

            f'<div class="ancestry-track">'

            f'<div '
            f'class="ancestry-fill" '
            f'style="width: '
            f'{percentual:.2f}%;">'
            f'</div>'

            f'</div>'

            f'</div>'
        )
    )


def tela_vazia(
    icone: str,
    titulo: str,
    texto: str,
) -> None:

    st.html(
        f"""
        <div class="empty-card">

            <div class="icon">
                {escapar(icone)}
            </div>

            <strong>
                {escapar(titulo)}
            </strong>

            <p>
                {escapar(texto)}
            </p>

        </div>
        """
    )


# =============================================================================
# CARREGAMENTO INICIAL
# =============================================================================

if st.session_state.dados is None:

    if JSON_DEMO.exists():

        try:
            st.session_state.dados = (
                carregar_json(
                    JSON_DEMO
                )
            )

            st.session_state.arquivo_relatorio = (
                str(JSON_DEMO)
            )

            st.session_state.erro_relatorio = (
                None
            )

        except Exception as erro:

            st.session_state.erro_relatorio = (
                str(erro)
            )

    else:
        st.session_state.erro_relatorio = (
            "O arquivo "
            "dados_estruturados.json "
            "não foi encontrado na "
            "raiz do projeto."
        )


# =============================================================================
# SINCRONIZAÇÃO DE NAVEGAÇÃO
# =============================================================================

def sincronizar_pagina(
    origem: str,
) -> None:

    nova_pagina = (
        st.session_state[
            origem
        ]
    )

    st.session_state.pagina = (
        nova_pagina
    )

    if origem == "nav_sidebar":
        st.session_state[
            "nav_mobile"
        ] = nova_pagina

    else:
        st.session_state[
            "nav_sidebar"
        ] = nova_pagina


def sincronizar_modo(
    origem: str,
) -> None:

    novo_modo = (
        st.session_state[
            origem
        ]
    )

    st.session_state.modo_resposta = (
        novo_modo
    )

    if origem == "modo_sidebar":
        st.session_state[
            "modo_mobile"
        ] = novo_modo

    else:
        st.session_state[
            "modo_sidebar"
        ] = novo_modo


for chave_nav in (
    "nav_sidebar",
    "nav_mobile",
):
    if chave_nav not in st.session_state:
        st.session_state[
            chave_nav
        ] = (
            st.session_state.pagina
        )


for chave_modo in (
    "modo_sidebar",
    "modo_mobile",
):
    if chave_modo not in st.session_state:
        st.session_state[
            chave_modo
        ] = (
            st.session_state.modo_resposta
        )


# =============================================================================
# PREPARAÇÃO DO RAG
# =============================================================================

def preparar_assistente() -> None:

    if (
        not
        st.session_state.arquivo_relatorio
    ):
        st.warning(
            "Carregue um relatório "
            "antes de preparar o assistente."
        )

        return

    try:

        with st.spinner(
            "Preparando busca semântica..."
        ):

            pipeline_script = (
                RAIZ
                / "sprint2"
                / "pipeline"
                / "pipeline_completo.py"
            )

            if not pipeline_script.exists():

                st.warning(
                    "O pipeline da Sprint 2 "
                    "não foi encontrado."
                )

                return

            resultado = subprocess.run(
                [
                    sys.executable,
                    str(
                        pipeline_script
                    ),
                    st.session_state[
                        "arquivo_relatorio"
                    ],
                ],
                cwd=str(RAIZ),
                capture_output=True,
                text=True,
                timeout=240,
            )

            if (
                resultado.returncode
                != 0
            ):
                detalhe = (
                    resultado.stderr.strip()
                    or
                    resultado.stdout.strip()
                )

                raise RuntimeError(
                    detalhe
                    or
                    "O pipeline retornou erro."
                )

            st.session_state.assistente_preparado = (
                True
            )

            st.success(
                "Assistente preparado."
            )

    except subprocess.TimeoutExpired:

        st.error(
            "A preparação demorou "
            "mais que o esperado."
        )

    except Exception as erro:

        st.error(
            "Não foi possível preparar "
            "o assistente. "
            f"Detalhes: {erro}"
        )


# =============================================================================
# CONTROLES
# =============================================================================

def render_controles(
    prefixo: str,
) -> None:

    st.caption(
        "Relatório"
    )

    upload = st.file_uploader(
        "Enviar outro relatório",
        type=["json"],
        accept_multiple_files=False,
        help=(
            "Envie um relatório "
            "estruturado em JSON."
        ),
        key=f"upload_{prefixo}",
    )

    if upload is not None:

        try:
            processar_upload(
                upload
            )

            st.success(
                "Relatório carregado."
            )

        except Exception as erro:

            st.session_state.erro_relatorio = (
                str(erro)
            )

            st.error(
                "Não foi possível carregar "
                f"o relatório: {erro}"
            )

    if (
        st.session_state
        .arquivo_relatorio
    ):

        nome_arquivo = (
            Path(
                st.session_state
                .arquivo_relatorio
            )
            .name
        )

        st.caption(
            f"Arquivo ativo: "
            f"{nome_arquivo}"
        )

    st.divider()

    st.caption(
        "Assistente"
    )

    chave = st.text_input(
        "OpenAI API Key",
        type="password",
        value=(
            st.session_state
            .api_key_session
        ),
        placeholder="sk-...",
        help=(
            "A chave é utilizada apenas "
            "durante esta sessão."
        ),
        key=f"api_{prefixo}",
    )

    if chave.strip():

        st.session_state.api_key_session = (
            chave.strip()
        )

        os.environ[
            "OPENAI_API_KEY"
        ] = chave.strip()

    chave_modo = (
        f"modo_{prefixo}"
    )

    st.selectbox(
        "Modo de resposta",
        [
            "Paciente",
            "Técnico",
        ],
        key=chave_modo,
        on_change=sincronizar_modo,
        args=(chave_modo,),
        help=(
            "Paciente prioriza linguagem "
            "acessível. Técnico mantém "
            "mais detalhes."
        ),
    )

    if st.button(
        "Preparar assistente",
        use_container_width=True,
        key=f"preparar_{prefixo}",
    ):
        preparar_assistente()

    status = (
        "Pronto"
        if (
            st.session_state
            .assistente_preparado
        )
        else
        "Aguardando preparação"
    )

    st.caption(
        f"Status: {status}"
    )

    st.html(
        """
        <div class="privacy-note">

            O dashboard não exibe CPF
            ou outros identificadores
            desnecessários.

            O histórico permanece apenas
            durante a sessão atual.

        </div>
        """
    )


# =============================================================================
# SIDEBAR DESKTOP
# =============================================================================

with st.sidebar:

    st.html(
        """
        <div class="brand">

            <div class="brand-mark">
                🧬
            </div>

            <div>

                <h2>
                    Genera AI
                </h2>

                <p>
                    Seu DNA explicado
                    com clareza
                </p>

            </div>

        </div>
        """
    )

    st.radio(
        "Navegação",
        PAGINAS,
        key="nav_sidebar",
        label_visibility="collapsed",
        on_change=sincronizar_pagina,
        args=("nav_sidebar",),
    )

    st.divider()

    render_controles(
        "sidebar"
    )


# =============================================================================
# MENU MOBILE PRÓPRIO
# =============================================================================

with st.container(
    key="mobile_nav"
):

    with st.popover(
        "☰ Menu e configurações",
        use_container_width=True,
    ):

        st.markdown(
            "### 🧬 Genera AI"
        )

        st.selectbox(
            "Página",
            PAGINAS,
            key="nav_mobile",
            on_change=sincronizar_pagina,
            args=("nav_mobile",),
        )

        st.divider()

        render_controles(
            "mobile"
        )


# =============================================================================
# VALIDAÇÃO GLOBAL
# =============================================================================

if (
    st.session_state
    .erro_relatorio
):

    cabecalho_pagina(
        "Genera AI",
        "Não foi possível abrir "
        "o relatório",
        (
            "Verifique o arquivo "
            "ou envie outro relatório."
        ),
    )

    st.error(
        st.session_state
        .erro_relatorio
    )

    st.stop()


if not isinstance(
    st.session_state.dados,
    dict,
):

    cabecalho_pagina(
        "Genera AI",
        "Nenhum relatório carregado",
        (
            "Envie um arquivo JSON "
            "para começar."
        ),
    )

    tela_vazia(
        "📄",
        "Relatório necessário",
        (
            "Carregue um relatório "
            "estruturado."
        ),
    )

    st.stop()


dados = (
    st.session_state.dados
)

resultados = (
    obter_resultados(
        dados
    )
)

ancestralidade = (
    obter_ancestralidade(
        dados
    )
)

nome_paciente = (
    obter_nome_paciente(
        dados
    )
)

riscos = (
    contagem_riscos(
        resultados
    )
)


# =============================================================================
# RESUMOS
# =============================================================================

def obter_resumo_automatico() -> Any:

    if (
        st.session_state
        .resumo_relatorio
        is not None
    ):
        return (
            st.session_state
            .resumo_relatorio
        )

    if (
        gerar_resumo_relatorio
        is None
    ):
        return None

    try:

        resumo = (
            gerar_resumo_relatorio(
                dados
            )
        )

        st.session_state.resumo_relatorio = (
            resumo
        )

        return resumo

    except Exception:
        return None


def texto_resumo(
    resumo: Any,
) -> str:

    if resumo is None:
        return ""

    if isinstance(
        resumo,
        str,
    ):
        return resumo

    if isinstance(
        resumo,
        dict,
    ):

        for chave in (
            "resumo_textual",
            "resumo",
            "texto",
            "resumo_geral",
            "sumario",
            "summary",
        ):

            valor = resumo.get(
                chave
            )

            if (
                isinstance(
                    valor,
                    str,
                )
                and
                valor.strip()
            ):
                return valor.strip()

        partes = []

        for (
            chave,
            valor,
        ) in resumo.items():

            if isinstance(
                valor,
                (
                    str,
                    int,
                    float,
                ),
            ):

                partes.append(
                    (
                        f"{str(chave).replace('_', ' ').title()}: "
                        f"{valor}"
                    )
                )

        return "\n".join(
            partes
        )

    return str(
        resumo
    )


# =============================================================================
# RAG / LLM / NLP
# =============================================================================

def buscar_contexto_seguro(
    pergunta: str,
) -> dict[str, Any]:

    try:

        from sprint2.vetorial.buscar import (
            buscar_contexto,
        )

        return buscar_contexto(
            pergunta,
            top_k=3,
            similaridade_minima=0.50,
        )

    except FileNotFoundError as erro:

        raise FileNotFoundError(
            "A base vetorial ainda "
            "não foi criada."
        ) from erro

    except Exception as erro:

        raise RuntimeError(
            "Erro na busca semântica: "
            f"{erro}"
        ) from erro


def obter_api_key() -> str | None:

    chave = (
        st.session_state
        .api_key_session
        or
        os.getenv(
            "OPENAI_API_KEY",
            "",
        )
    )

    chave = str(
        chave
    ).strip()

    return (
        chave
        or None
    )


def modo_llm() -> str:

    if (
        st.session_state
        .modo_resposta
        == "Técnico"
    ):
        return "tecnico"

    return "paciente"


def aplicar_nlp_resposta(
    texto: str,
    modo: str,
) -> tuple[
    str,
    dict[str, Any],
]:

    if modo != "paciente":
        return (
            texto,
            {},
        )

    if simplificar_texto is None:
        return (
            texto,
            {},
        )

    try:

        resultado = (
            simplificar_texto(
                texto
            )
        )

        texto_final = (
            resultado.get(
                "texto_simplificado",
                texto,
            )
        )

        metricas = {
            "original":
                resultado.get(
                    "metricas_original",
                    {},
                ),

            "simplificado":
                resultado.get(
                    "metricas_simplificado",
                    {},
                ),
        }

        return (
            texto_final,
            metricas,
        )

    except Exception:

        return (
            texto,
            {},
        )


def processar_pergunta(
    pergunta: str,
) -> dict[str, Any]:

    pergunta = (
        pergunta.strip()
    )

    if not pergunta:

        raise ValueError(
            "Digite uma pergunta."
        )

    api_key = (
        obter_api_key()
    )

    if not api_key:

        raise PermissionError(
            "Configure sua OpenAI API Key."
        )

    resultado_busca = (
        buscar_contexto_seguro(
            pergunta
        )
    )

    trechos_completos = (
        resultado_busca.get(
            "trechos",
            [],
        )
    )

    trechos_texto = []

    for trecho in trechos_completos:

        if isinstance(
            trecho,
            dict,
        ):

            conteudo = trecho.get(
                "conteudo",
                "",
            )

            if conteudo:

                trechos_texto.append(
                    str(conteudo)
                )

        elif trecho:

            trechos_texto.append(
                str(trecho)
            )

    from llm_connector import (
        responder_com_llm,
    )

    modo = (
        modo_llm()
    )

    resultado_llm = (
        responder_com_llm(
            pergunta=pergunta,
            trechos=trechos_texto,
            modo=modo,
            api_key=api_key,
        )
    )

    status = (
        resultado_llm.get(
            "status",
            "sem_contexto",
        )
    )

    resposta_original = str(
        resultado_llm.get(
            "resposta",
            "",
        )
    )

    if status == "respondido":

        (
            resposta_final,
            metricas,
        ) = aplicar_nlp_resposta(
            resposta_original,
            modo,
        )

    else:

        resposta_final = (
            resposta_original
        )

        metricas = {}

    return {
        "status":
            status,

        "categoria":
            resultado_llm.get(
                "categoria",
                "",
            ),

        "resposta_original":
            resposta_original,

        "resposta":
            resposta_final,

        "fontes":
            trechos_completos,

        "modo":
            modo,

        "metricas_nlp":
            metricas,
    }


# =============================================================================
# COMPONENTES DO CHAT
# =============================================================================

def classe_chat(
    status: str,
) -> tuple[
    str,
    str,
]:

    if status == "bloqueado":
        return (
            "chat-blocked",
            "⚠️",
        )

    if status == "sem_contexto":
        return (
            "chat-no-context",
            "ℹ️",
        )

    return (
        "chat-assistant",
        "🧬",
    )


def exibir_fontes(
    fontes: list[Any],
) -> None:

    if not fontes:
        return

    with st.expander(
        f"Fontes utilizadas "
        f"({len(fontes)})"
    ):

        for (
            indice,
            fonte,
        ) in enumerate(
            fontes,
            start=1,
        ):

            if isinstance(
                fonte,
                dict,
            ):

                conteudo = str(
                    fonte.get(
                        "conteudo",
                        "",
                    )
                )

                secao = str(
                    fonte.get(
                        "secao",
                        "Relatório",
                    )
                )

                origem = str(
                    fonte.get(
                        "fonte",
                        "Relatório genético",
                    )
                )

                try:

                    similaridade = float(
                        fonte.get(
                            "similaridade",
                            0.0,
                        )
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    similaridade = 0.0

            else:

                conteudo = str(
                    fonte
                )

                secao = "Relatório"

                origem = (
                    "Relatório genético"
                )

                similaridade = 0.0

            if (
                len(conteudo)
                > 320
            ):
                conteudo = (
                    conteudo[:320]
                    + "..."
                )

            st.html(
                f"""
                <div class="source-card">

                    <strong>
                        Fonte {indice}
                        ·
                        {escapar(secao)}
                    </strong>

                    <br>

                    {escapar(conteudo)}

                    <br>

                    <small>
                        Origem:
                        {escapar(origem)}
                    </small>

                </div>
                """
            )

            if similaridade > 0:

                valor = max(
                    0.0,
                    min(
                        similaridade,
                        1.0,
                    ),
                )

                st.progress(
                    valor,
                    text=(
                        "Relevância semântica: "
                        f"{valor:.0%}"
                    ),
                )


def exibir_metricas_nlp(
    metricas: dict[str, Any],
) -> None:

    if not metricas:
        return

    original = metricas.get(
        "original",
        {},
    )

    simplificado = metricas.get(
        "simplificado",
        {},
    )

    if (
        not original
        and
        not simplificado
    ):
        return

    with st.expander(
        "Como a linguagem "
        "foi simplificada?"
    ):

        st.caption(
            "Métricas da camada NLP "
            "da Sprint 3."
        )

        col1, col2 = (
            st.columns(2)
        )

        with col1:

            st.markdown(
                "**Texto original**"
            )

            if original:

                for (
                    chave,
                    valor,
                ) in original.items():

                    st.write(
                        (
                            f"{str(chave).replace('_', ' ').title()}: "
                            f"{valor}"
                        )
                    )

            else:

                st.caption(
                    "Métricas não disponíveis."
                )

        with col2:

            st.markdown(
                "**Texto simplificado**"
            )

            if simplificado:

                for (
                    chave,
                    valor,
                ) in simplificado.items():

                    st.write(
                        (
                            f"{str(chave).replace('_', ' ').title()}: "
                            f"{valor}"
                        )
                    )

            else:

                st.caption(
                    "Métricas não disponíveis."
                )


def historico_para_resumo() -> list[
    dict[str, str]
]:

    interacoes = []

    pergunta_atual = None

    for mensagem in (
        st.session_state.messages
    ):

        role = mensagem.get(
            "role"
        )

        if role == "user":

            pergunta_atual = str(
                mensagem.get(
                    "content",
                    "",
                )
            )

        elif (
            role == "assistant"
            and
            pergunta_atual
        ):

            interacoes.append(
                {
                    "pergunta":
                        pergunta_atual,

                    "resposta":
                        str(
                            mensagem.get(
                                "content",
                                "",
                            )
                        ),
                }
            )

            pergunta_atual = None

    return interacoes


# =============================================================================
# PÁGINA: VISÃO GERAL
# =============================================================================

def render_visao_geral() -> None:

    cabecalho_pagina(
        "Visão geral",
        f"Olá, {nome_paciente} 👋",
        (
            "Veja os principais pontos "
            "do seu relatório genético "
            "em uma experiência organizada "
            "e acessível."
        ),
    )

    disclaimer()

    total_resultados = (
        len(resultados)
    )

    total_ancestralidade = (
        len(ancestralidade)
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:

        card_metrica(
            "Resultados analisados",
            total_resultados,
            (
                "Condições e características "
                "presentes no relatório."
            ),
        )

    with col2:

        card_metrica(
            "Maior atenção",
            riscos.get(
                "alto",
                0,
            ),
            (
                "Resultados que merecem "
                "uma leitura mais cuidadosa."
            ),
        )

    with col3:

        card_metrica(
            "Atenção moderada",
            riscos.get(
                "medio",
                0,
            ),
            (
                "Predisposições intermediárias "
                "no relatório."
            ),
        )

    with col4:

        card_metrica(
            "Ancestralidade",
            total_ancestralidade,
            (
                "Regiões ou populações "
                "identificadas."
            ),
        )

    titulo_secao(
        "Principais resultados",
        "Visão resumida do relatório",
    )

    if resultados:

        ordem = {
            "alto": 0,
            "medio": 1,
            "baixo": 2,
            "indefinido": 3,
        }

        priorizados = sorted(
            resultados,
            key=lambda item:
                ordem.get(
                    obter_risco_resultado(
                        item
                    ),
                    4,
                ),
        )

        exibidos = (
            priorizados[:6]
        )

        for inicio in range(
            0,
            len(exibidos),
            3,
        ):

            linha = (
                exibidos[
                    inicio:
                    inicio + 3
                ]
            )

            colunas = (
                st.columns(
                    len(linha)
                )
            )

            for (
                coluna,
                resultado,
            ) in zip(
                colunas,
                linha,
            ):

                with coluna:

                    card_resultado(
                        resultado
                    )

        if (
            len(resultados)
            > 6
        ):

            st.caption(
                (
                    f"Mostrando 6 de "
                    f"{len(resultados)} "
                    "resultados. "
                    "Acesse 'Meus resultados' "
                    "para ver todos."
                )
            )

    else:

        tela_vazia(
            "🧬",
            "Nenhum resultado encontrado",
            (
                "O relatório não possui "
                "resultados reconhecidos."
            ),
        )

    esquerda, direita = (
        st.columns(
            [
                1.1,
                .9,
            ]
        )
    )

    with esquerda:

        titulo_secao(
            "Sua ancestralidade",
            (
                "Composição identificada "
                "no relatório"
            ),
        )

        if ancestralidade:

            ordenada = sorted(
                ancestralidade,
                key=lambda item:
                    dados_regiao_ancestralidade(
                        item
                    )[1],
                reverse=True,
            )

            for item in ordenada[:8]:

                (
                    regiao,
                    percentual,
                ) = (
                    dados_regiao_ancestralidade(
                        item
                    )
                )

                barra_ancestralidade(
                    regiao,
                    percentual,
                )

        else:

            st.info(
                "O relatório não contém "
                "informações de ancestralidade "
                "em formato reconhecido."
            )

    with direita:

        titulo_secao(
            "Resumo automático",
            "Leitura rápida",
        )

        resumo = (
            obter_resumo_automatico()
        )

        texto = (
            texto_resumo(
                resumo
            )
        )

        if texto:

            st.html(
                f"""
                <div class="summary-card">

                    <div class="summary-lead">
                        {escapar(texto)}
                    </div>

                </div>
                """
            )

        else:

            st.html(
                f"""
                <div class="summary-card">

                    <div class="summary-lead">

                        Seu relatório reúne
                        <strong>
                            {total_resultados}
                        </strong>
                        resultados genéticos.

                    </div>

                    <ul class="mini-list">

                        <li>
                            {riscos.get("alto", 0)}
                            de maior atenção.
                        </li>

                        <li>
                            {riscos.get("medio", 0)}
                            de atenção moderada.
                        </li>

                        <li>
                            {riscos.get("baixo", 0)}
                            de menor atenção.
                        </li>

                    </ul>

                </div>
                """
            )

    titulo_secao(
        "Pergunte sobre seu DNA",
        (
            "Assistente com contexto "
            "do relatório"
        ),
    )

    st.html(
        """
        <div class="content-card">

            Use o assistente para entender
            termos técnicos, predisposições,
            características e ancestralidade
            com base no seu próprio relatório.

        </div>
        """
    )

    col_a, col_b, col_c = (
        st.columns(3)
    )

    with col_a:

        if st.button(
            "O que merece mais atenção?",
            use_container_width=True,
        ):

            st.session_state.pagina = (
                "Assistente"
            )

            st.session_state.nav_sidebar = (
                "Assistente"
            )

            st.session_state.nav_mobile = (
                "Assistente"
            )

            st.session_state.pergunta_sugerida = (
                "Quais resultados do meu "
                "relatório merecem mais atenção?"
            )

            st.rerun()

    with col_b:

        if st.button(
            "Explique meus resultados",
            use_container_width=True,
        ):

            st.session_state.pagina = (
                "Assistente"
            )

            st.session_state.nav_sidebar = (
                "Assistente"
            )

            st.session_state.nav_mobile = (
                "Assistente"
            )

            st.session_state.pergunta_sugerida = (
                "Explique os principais "
                "resultados do meu relatório "
                "em linguagem simples."
            )

            st.rerun()

    with col_c:

        if st.button(
            "Entender ancestralidade",
            use_container_width=True,
        ):

            st.session_state.pagina = (
                "Assistente"
            )

            st.session_state.nav_sidebar = (
                "Assistente"
            )

            st.session_state.nav_mobile = (
                "Assistente"
            )

            st.session_state.pergunta_sugerida = (
                "O que os dados de "
                "ancestralidade do meu "
                "relatório significam?"
            )

            st.rerun()


# =============================================================================
# PÁGINA: MEUS RESULTADOS
# =============================================================================

def render_resultados() -> None:

    cabecalho_pagina(
        "Meu DNA",
        "Seus resultados genéticos",
        (
            "Consulte cada resultado "
            "individualmente e compare "
            "a explicação acessível com "
            "os detalhes técnicos."
        ),
    )

    disclaimer()

    if not resultados:

        tela_vazia(
            "🧬",
            "Nenhum resultado disponível",
            (
                "O relatório atual "
                "não possui resultados."
            ),
        )

        return

    col_filtro, col_busca = (
        st.columns(
            [
                .35,
                .65,
            ]
        )
    )

    with col_filtro:

        filtro = st.selectbox(
            "Filtrar por atenção",
            [
                "Todos",
                "Maior atenção",
                "Atenção moderada",
                "Menor atenção",
            ],
        )

    with col_busca:

        busca = st.text_input(
            "Buscar resultado",
            placeholder=(
                "Ex.: diabetes, "
                "metabolismo..."
            ),
        )

    mapa = {
        "Maior atenção":
            "alto",

        "Atenção moderada":
            "medio",

        "Menor atenção":
            "baixo",
    }

    filtrados = []

    for resultado in resultados:

        risco = (
            obter_risco_resultado(
                resultado
            )
        )

        nome = (
            nome_resultado(
                resultado
            )
        )

        categoria = (
            categoria_resultado(
                resultado
            )
        )

        if (
            filtro
            != "Todos"
        ):

            if (
                risco
                != mapa.get(
                    filtro
                )
            ):
                continue

        termo = (
            busca
            .strip()
            .lower()
        )

        if termo:

            conteudo = (
                (
                    f"{nome} "
                    f"{categoria} "
                    f"{descricao_resultado(resultado)}"
                )
                .lower()
            )

            if (
                termo
                not in conteudo
            ):
                continue

        filtrados.append(
            resultado
        )

    st.caption(
        f"{len(filtrados)} "
        "resultado(s) encontrado(s)."
    )

    for resultado in filtrados:

        risco = (
            obter_risco_resultado(
                resultado
            )
        )

        titulo = (
            f"{nome_resultado(resultado)} "
            f"· {rotulo_risco(risco)}"
        )

        with st.expander(
            titulo
        ):

            esquerda, direita = (
                st.columns(
                    [
                        .58,
                        .42,
                    ]
                )
            )

            with esquerda:

                st.markdown(
                    "#### Explicação acessível"
                )

                st.write(
                    descricao_resultado(
                        resultado
                    )
                )

                recomendacao = (
                    recomendacao_resultado(
                        resultado
                    )
                )

                if recomendacao:

                    st.markdown(
                        "#### Orientação"
                    )

                    st.write(
                        recomendacao
                    )

            with direita:

                st.markdown(
                    "#### Detalhes do relatório"
                )

                campos = [
                    (
                        "Categoria",
                        resultado.get(
                            "categoria"
                        ),
                    ),

                    (
                        "Risco original",
                        resultado.get(
                            "risco"
                        ),
                    ),

                    (
                        "Impacto prático",
                        resultado.get(
                            "impacto_pratico"
                        ),
                    ),

                    (
                        "Urgência médica",
                        resultado.get(
                            "urgencia_medica"
                        ),
                    ),
                ]

                for (
                    rotulo,
                    valor,
                ) in campos:

                    if valor not in (
                        None,
                        "",
                        [],
                        {},
                    ):

                        st.markdown(
                            f"**{rotulo}:** "
                            f"{valor}"
                        )

                descricao_tecnica = (
                    resultado.get(
                        "descricao_tecnica"
                    )
                )

                if descricao_tecnica:

                    st.markdown(
                        "**Descrição técnica:**"
                    )

                    st.write(
                        descricao_tecnica
                    )

    titulo_secao(
        "Ancestralidade completa",
        (
            f"{len(ancestralidade)} "
            "região(ões)"
        ),
    )

    if ancestralidade:

        for item in sorted(
            ancestralidade,
            key=lambda item:
                dados_regiao_ancestralidade(
                    item
                )[1],
            reverse=True,
        ):

            (
                regiao,
                percentual,
            ) = (
                dados_regiao_ancestralidade(
                    item
                )
            )

            barra_ancestralidade(
                regiao,
                percentual,
            )

            intervalo = obter_primeiro(
                item,
                "intervalo_confianca_95",
                "intervalo_confianca",
                "confidence_interval",
                padrao=None,
            )

            if intervalo:

                st.caption(
                    "Intervalo de confiança "
                    f"informado: {intervalo}"
                )

    else:

        tela_vazia(
            "🌎",
            "Ancestralidade não disponível",
            (
                "O relatório atual "
                "não apresenta essa seção."
            ),
        )


# =============================================================================
# PÁGINA: ASSISTENTE
# =============================================================================

def render_assistente() -> None:

    cabecalho_pagina(
        "Assistente",
        "Converse sobre seu relatório",
        (
            "Faça perguntas em linguagem natural. "
            "As respostas utilizam busca semântica, "
            "RAG e as salvaguardas das Sprints anteriores."
        ),
    )

    disclaimer()

    if not (
        st.session_state
        .assistente_preparado
    ):

        st.info(
            "Antes de conversar, "
            "prepare o assistente "
            "em Menu e configurações "
            "ou na barra lateral."
        )

    st.html(
        """
        <div class="content-card">

            <strong>
                Algumas perguntas que você pode fazer:
            </strong>

            <br><br>

            • O que merece mais atenção
            no meu relatório?

            <br>

            • Explique meu resultado
            de diabetes em linguagem simples.

            <br>

            • O que minha ancestralidade
            significa?

            <br>

            • Quais recomendações aparecem
            no meu relatório?

        </div>
        """
    )

    if not (
        st.session_state.messages
    ):

        tela_vazia(
            "💬",
            "Nenhuma conversa ainda",
            (
                "Escreva uma dúvida "
                "sobre seu relatório."
            ),
        )

    else:

        for mensagem in (
            st.session_state.messages
        ):

            role = mensagem.get(
                "role",
                "",
            )

            conteudo = str(
                mensagem.get(
                    "content",
                    "",
                )
            )

            if role == "user":

                st.html(
                    f"""
                    <div class="chat-user">

                        <div class="chat-name">
                            Você
                        </div>

                        {
                            escapar(conteudo)
                            .replace(
                                chr(10),
                                "<br>"
                            )
                        }

                    </div>
                    """
                )

            elif role == "assistant":

                status = mensagem.get(
                    "status",
                    "respondido",
                )

                (
                    classe,
                    icone,
                ) = classe_chat(
                    status
                )

                modo_msg = mensagem.get(
                    "modo",
                    "paciente",
                )

                modo_legivel = (
                    "Paciente"
                    if modo_msg
                    == "paciente"
                    else
                    "Técnico"
                )

                st.html(
                    f"""
                    <div class="{classe}">

                        <div class="chat-name">

                            {icone}
                            Genera AI
                            ·
                            {modo_legivel}

                        </div>

                        {
                            escapar(conteudo)
                            .replace(
                                chr(10),
                                "<br>"
                            )
                        }

                    </div>
                    """
                )

                exibir_fontes(
                    mensagem.get(
                        "fontes",
                        [],
                    )
                )

                exibir_metricas_nlp(
                    mensagem.get(
                        "metricas_nlp",
                        {},
                    )
                )

    pergunta_sugerida = (
        st.session_state.pop(
            "pergunta_sugerida",
            "",
        )
    )

    pergunta_chat = (
        st.chat_input(
            "Pergunte sobre seu "
            "relatório genético..."
        )
    )

    pergunta_final = (
        pergunta_sugerida
        or
        pergunta_chat
    )

    if pergunta_final:

        pergunta_final = (
            pergunta_final.strip()
        )

        if not (
            st.session_state
            .assistente_preparado
        ):

            st.warning(
                "Prepare o assistente "
                "antes de enviar perguntas."
            )

            return

        if not obter_api_key():

            st.error(
                "Configure sua OpenAI API Key."
            )

            return

        st.session_state.messages.append(
            {
                "role":
                    "user",

                "content":
                    pergunta_final,
            }
        )

        with st.spinner(
            "Analisando seu relatório..."
        ):

            try:

                resultado = (
                    processar_pergunta(
                        pergunta_final
                    )
                )

                st.session_state.messages.append(
                    {
                        "role":
                            "assistant",

                        "content":
                            resultado[
                                "resposta"
                            ],

                        "resposta_original":
                            resultado[
                                "resposta_original"
                            ],

                        "status":
                            resultado[
                                "status"
                            ],

                        "categoria":
                            resultado[
                                "categoria"
                            ],

                        "fontes":
                            resultado[
                                "fontes"
                            ],

                        "modo":
                            resultado[
                                "modo"
                            ],

                        "metricas_nlp":
                            resultado[
                                "metricas_nlp"
                            ],
                    }
                )

            except FileNotFoundError:

                st.session_state.messages.pop()

                st.error(
                    "A base vetorial "
                    "não foi encontrada."
                )

                return

            except PermissionError as erro:

                st.session_state.messages.pop()

                st.error(
                    str(erro)
                )

                return

            except RuntimeError as erro:

                st.session_state.messages.pop()

                mensagem = str(
                    erro
                )

                if (
                    "quota"
                    in mensagem.lower()
                    or
                    "limit"
                    in mensagem.lower()
                ):

                    st.error(
                        "O limite de uso "
                        "da API foi atingido."
                    )

                else:

                    st.error(
                        "Não foi possível gerar "
                        "a resposta. "
                        f"Detalhes: {mensagem}"
                    )

                return

            except Exception as erro:

                st.session_state.messages.pop()

                st.error(
                    "Erro inesperado: "
                    f"{erro}"
                )

                return

        st.rerun()

    if (
        st.session_state.messages
    ):

        st.divider()

        if st.button(
            "Limpar conversa"
        ):

            st.session_state.messages = []

            st.rerun()


# =============================================================================
# PÁGINA: HISTÓRICO
# =============================================================================

def render_historico() -> None:

    cabecalho_pagina(
        "Histórico",
        "Resumo das suas interações",
        (
            "Veja as perguntas realizadas "
            "nesta sessão e os temas "
            "identificados automaticamente."
        ),
    )

    disclaimer()

    interacoes = (
        historico_para_resumo()
    )

    if not interacoes:

        tela_vazia(
            "🕘",
            "Histórico vazio",
            (
                "As conversas realizadas "
                "com o assistente aparecerão aqui."
            ),
        )

        return

    esquerda, direita = (
        st.columns(
            [
                .58,
                .42,
            ]
        )
    )

    with esquerda:

        titulo_secao(
            "Conversas da sessão",
            (
                f"{len(interacoes)} "
                "interação(ões)"
            ),
        )

        total = (
            len(interacoes)
        )

        for (
            indice,
            interacao,
        ) in enumerate(
            reversed(
                interacoes
            ),
            start=1,
        ):

            numero = (
                total
                - indice
                + 1
            )

            pergunta = (
                interacao[
                    "pergunta"
                ]
            )

            with st.expander(
                (
                    f"Interação {numero} "
                    f"· {pergunta[:70]}"
                )
            ):

                st.markdown(
                    "**Pergunta**"
                )

                st.write(
                    pergunta
                )

                st.markdown(
                    "**Resposta**"
                )

                st.write(
                    interacao[
                        "resposta"
                    ]
                )

    with direita:

        titulo_secao(
            "Resumo automático",
            "NLP",
        )

        if (
            gerar_resumo_interacoes
            is None
        ):

            st.info(
                "O módulo de resumo "
                "não está disponível."
            )

            return

        try:

            resumo = (
                gerar_resumo_interacoes(
                    interacoes
                )
            )

            if (
                formatar_resumo_interacoes
                is not None
            ):

                resumo_formatado = (
                    formatar_resumo_interacoes(
                        resumo
                    )
                )

            else:

                resumo_formatado = (
                    str(resumo)
                )

            st.html(
                f"""
                <div class="summary-card">

                    <div class="summary-lead">

                        {
                            escapar(
                                resumo_formatado
                            )
                            .replace(
                                chr(10),
                                "<br>"
                            )
                        }

                    </div>

                </div>
                """
            )

        except Exception as erro:

            st.info(
                "O resumo das interações "
                "não pôde ser gerado: "
                f"{erro}"
            )

    st.html(
        """
        <div class="privacy-note">

            Este histórico utiliza apenas
            o estado da sessão atual.

            A interface não mantém um banco
            próprio com as conversas do paciente.

        </div>
        """
    )


# =============================================================================
# ROTEAMENTO
# =============================================================================

pagina = (
    st.session_state.pagina
)


if pagina == "Visão geral":

    render_visao_geral()


elif pagina == "Meus resultados":

    render_resultados()


elif pagina == "Assistente":

    render_assistente()


elif pagina == "Histórico":

    render_historico()
