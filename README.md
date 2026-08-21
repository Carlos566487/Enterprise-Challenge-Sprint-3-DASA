<p align="center">
  <a href="https://www.fiap.com.br/">
    <img src="https://raw.githubusercontent.com/Carlos566487/Enterprise-Challenge-Sprint-3-DASA/main/docs/images/logo-fiap.png" alt="FIAP" width="35%"/>
  </a>
</p>

<h1 align="center">🧬 Genera AI · Dasa</h1>
<h2 align="center">Fase 5 — Conectando Mundos: IA Multimodal em Aplicações Enterprise</h2>
<h3 align="center">Enterprise Challenge · Sprint 3 · DASA</h3>
<h4 align="center">Transformando relatórios genéticos em uma experiência conversacional inteligente, segura e acessível</h4>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python"/>
  <img src="https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square&logo=streamlit"/>
  <img src="https://img.shields.io/badge/ChromaDB-vetorial-green?style=flat-square"/>
  <img src="https://img.shields.io/badge/RAG-LLM-purple?style=flat-square"/>
  <img src="https://img.shields.io/badge/OpenAI-GPT--4.1_Mini-black?style=flat-square&logo=openai"/>
  <img src="https://img.shields.io/badge/LGPD-compliant-orange?style=flat-square"/>
  <img src="https://img.shields.io/badge/Sprint-3-blue?style=flat-square"/>
  <img src="https://img.shields.io/badge/Testes-67_casos-brightgreen?style=flat-square"/>
</p>

<p align="center">
  <a href="#1-o-que-foi-construído-nesta-sprint">O que foi feito</a> ·
  <a href="#8-como-executar-o-projeto">Como executar</a> ·
  <a href="#10-governança-e-comunicação-responsável">Governança</a> ·
  <a href="#12-vídeo-de-apresentação">Vídeo</a>
</p>

---

## 👨‍🎓 Equipe

| Nome | RM | Papel — Sprint 3 |
|---|---:|---|
| João | RM565999 | Cientista de IA — Personalização & RAG |
| Endrew Alves | RM563646 | UX / Front-end e Mobile — Dashboard |
| Tayná Esteves | RM562491 | NLP e Automação de Resumos |
| Carlos Eduardo | RM566487 | Governança, Comunicação Responsável & Documentação |

### 👩‍🏫 Professores

**Tutor turma A:** [Caique Nonato da Silva Bezerra](https://www.linkedin.com/in/caique-nonato/) — profcaique.bezerra@fiap.com.br  
**Tutor turma R:** [Leonardo Ruiz Orabona](https://www.linkedin.com/in/leonardoorabona/) — profleonardo.orabona@fiap.com.br  
**Coordenador:** [André Godoi Chiovato](https://www.linkedin.com/in/andregodoichiovato/) - profandre.chiovato@fiap.com.br

---

## ➡️ Link do Projeto:
https://github.com/Carlos566487/Enterprise-Challenge-Sprint-3-DASA.git

---

## 📋 Índice

1. [O que foi construído nesta Sprint](#1-o-que-foi-construído-nesta-sprint)
2. [Evolução da Experiência do Usuário](#2-evolução-da-experiência-do-usuário)
3. [Arquitetura completa](#3-arquitetura-completa)
4. [João — Cientista de IA: Personalização & RAG](#4-joão--cientista-de-ia-personalização--rag)
5. [Endrew — UX / Front-end e Mobile: Dashboard](#5-endrew--ux--front-end-e-mobile-dashboard)
6. [Tayná — NLP e Automação de Resumos](#6-tayná--nlp-e-automação-de-resumos)
7. [Carlos — Governança e Comunicação Responsável](#7-carlos--governança-e-comunicação-responsável)
8. [Como executar o projeto](#8-como-executar-o-projeto)
9. [Estrutura do repositório](#9-estrutura-do-repositório)
10. [Governança e Comunicação Responsável](#10-governança-e-comunicação-responsável)
11. [Continuidade — Sprint 1 → Sprint 2 → Sprint 3](#11-continuidade--sprint-1--sprint-2--sprint-3)
12. [Vídeo de apresentação](#12-vídeo-de-apresentação)

---

## 1. O que foi construído nesta Sprint

A Sprint 2 entregou o motor de inteligência: pipeline RAG funcional, guardrails médicos e interface de chat básica.

**A Sprint 3 transforma esse motor em produto usável.**

| Componente | Responsável | O que entrega |
|---|---|---|
| **Dashboard com cards de risco** | Endrew (UX) | Visão geral visual do relatório genético com classificação de risco |
| **Personalização do RAG** | João (IA) | Adapta tom, profundidade e `top_k` ao perfil do usuário |
| **Simplificação de linguagem (NLP)** | Tayná (NLP) | Pós-processamento para linguagem acessível e resumos automáticos |
| **Governança e comunicação responsável** | Carlos | Disclaimers contextuais, revisão de alarmismo e política de privacidade |

---

## 2. Evolução da Experiência do Usuário

### 🖥️ Dashboard

A interface da Sprint 3 (`sprint3/interface/app.py`) é uma evolução completa da interface de chat da Sprint 2. Ao carregar o relatório, o usuário acessa:

- **Dashboard** com cards de classificação visual de risco (verde / amarelo / laranja)
- **Página "Meus Resultados"** com busca, filtros e detalhes por condição genética
- **Visualização de ancestralidade** em formato visual
- **Resumo automático** do relatório (integrado com o módulo NLP da Tayná)
- **Assistente conversacional** com RAG personalizado (módulo do João)
- **Interface responsiva** para desktop e telas menores

Principais decisões de UX:

| Decisão | Justificativa |
|---|---|
| "Alto risco" → "Maior atenção" | Reduz alarmismo sem omitir a informação |
| Disclaimer médico sempre visível | Obrigação ética e legal — não pode ser fechado |
| Visão geral antes dos detalhes | Reduz sobrecarga cognitiva para o leigo |
| Dados pessoais mínimos exibidos | Princípio da minimização (LGPD) |

### 🤖 Personalização de Respostas

O módulo `sprint3/rag_personalizacao/` adapta a resposta ao **perfil declarado do usuário** sem alterar os fatos do relatório:

| Perfil | Tom | `top_k` | Característica |
|---|---|---|---|
| `leigo_ansioso` | Paciente/calmo | 3 | Risco como tendência estatística, sem alarmismo |
| `leigo_curioso` | Paciente/explicativo | 4 | Linguagem simples + mecanismo biológico |
| `medico` | Técnico | 5 | Marcadores e escores como constam no relatório |

Toda resposta passa por validação de ancoragem: números, percentuais e SNPs na resposta devem aparecer nos trechos recuperados do relatório.

### 📝 Simplificação de Linguagem e Resumos

O módulo `sprint3/nlp/` oferece:
- `nlp_simplificacao.py` — traduz jargão genético para linguagem acessível
- `resumos_automaticos.py` — gera resumos do relatório por seção e geral
- Integração com o RAG via `sprint3/integracao/adaptador_nlp.py`

### 🛡️ Salvaguardas de Comunicação Responsável

O módulo `sprint3/governanca/` implementa:
- Disclaimers fixos contextuais exibidos na interface
- Revisor de linguagem que bloqueia alarmismo e garante contexto estatístico
- Documentação e política de privacidade alinhada com o que está no repositório

---

## 3. Arquitetura completa

```
┌─────────────────────────────────────────────────────────────────────┐
│  SPRINT 1 (base herdada)                                            │
│  relatorio_genera_simulado.pdf  →  dados_estruturados.json          │
│  pdfplumber + PyMuPDF · limpeza · schema JSON padronizado           │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SPRINT 2 (motor herdado — nenhum arquivo alterado)                 │
│  gerar_embeddings.py → ChromaDB → buscar_contexto()                 │
│  agente_especialista.py · guardrails.py · prompts.py                │
│  Interface Streamlit básica (chat)                                   │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SPRINT 3 — Camadas adicionadas (esta entrega)                      │
│                                                                     │
│  sprint3/rag_personalizacao/     ← João                             │
│  perfis.py · personalizador.py · ancoragem.py · historico.py       │
│                                                                     │
│  sprint3/nlp/                    ← Tayná                            │
│  nlp_simplificacao.py · resumos_automaticos.py                      │
│                                                                     │
│  sprint3/governanca/             ← Carlos                           │
│  disclaimers.py · revisor_linguagem.py                              │
│                                                                     │
│  sprint3/integracao/             ← integração das três camadas      │
│  adaptador_nlp.py                                                   │
│                                                                     │
│  sprint3/interface/app.py        ← Endrew                           │
│  Dashboard · Cards · Ancestralidade · Resumos · Chat personalizado  │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
                          Usuário recebe resposta
               com dashboard, fontes, disclaimer e linguagem acessível
```

---

## Cientista de IA: Personalização & RAG

> *"Eu adapto a inteligência ao perfil de quem pergunta."*

Camada que envolve o pipeline da Sprint 2 — **nenhum arquivo de `sprint2/` foi alterado** — e adapta as respostas ao perfil e histórico do usuário.

A personalização atua sobre a **forma** da resposta (tom, profundidade, vocabulário, `top_k`), nunca sobre o **conteúdo** (fatos, números, marcadores, nível de risco, veredito dos guardrails).

### Fluxo

```
pergunta + perfil + usuario_id
   ↓ guardrails sobre a pergunta CRUA        (bloqueio não gasta token)
   ↓ busca semântica com top_k do perfil     sprint2/vetorial/buscar.py
   ↓ pergunta personalizada (forma + continuidade)
   ↓ responder_com_llm()                     sprint2/interface/llm_connector.py
   ↓   ← sempre o caminho real GPT-4.1 Mini, nunca a resposta simulada
   ↓ validação de ancoragem no relatório
   ↓ revisar_linguagem()                     sprint3/governanca/revisor_linguagem.py
   ↓ registro no histórico
contrato estável v1.0
```

### Uso

```python
from sprint3.rag_personalizacao import responder_personalizado

resultado = responder_personalizado(
    pergunta="Eu tenho risco de diabetes?",
    perfil="leigo_ansioso",
    usuario_id="paciente-001",
    api_key=OPENAI_API_KEY,
)
```

```bash
pytest sprint3/rag_personalizacao/ -v    # 32 testes, sem API key
pytest sprint3/integracao/ -v            # 19 testes de integração NLP ↔ RAG
pytest sprint3/governanca/ -v            # 16 testes de governança
pytest                                   # 67 testes no total
```

### Arquivos

| Arquivo | Função |
|---|---|
| `sprint3/rag_personalizacao/perfis.py` | Definição dos 3 perfis de usuário |
| `sprint3/rag_personalizacao/personalizador.py` | Orquestrador da personalização |
| `sprint3/rag_personalizacao/ancoragem.py` | Validação de fidelidade ao relatório |
| `sprint3/rag_personalizacao/historico.py` | Registro e continuidade de histórico |
| `sprint3/rag_personalizacao/test_personalizacao.py` | 32 casos de teste |

---

## UX / Front-end e Mobile: Dashboard

> *"Eu faço o relatório genético ser compreensível para qualquer pessoa."*

A interface da Sprint 3 reconstrói a experiência do usuário a partir dos dados do relatório genético, priorizando clareza visual sobre complexidade técnica.

### Funcionalidades

**Dashboard principal:**
- Cards com classificação visual dos principais resultados genéticos
- Barra de risco relativo com cor (verde / amarelo / laranja) — sem texto alarmista
- Resumo automático gerado pelo módulo NLP

**Página "Meus Resultados":**
- Busca e filtros por condição, categoria e nível de atenção
- Detalhes expandíveis por condição com marcadores genéticos
- Visualização de ancestralidade

**Assistente conversacional:**
- Chat com RAG personalizado (módulo do João)
- Linguagem simplificada (módulo da Tayná)
- Disclaimer médico fixo e fontes rastreáveis

### Arquivos

| Arquivo | Função |
|---|---|
| `sprint3/interface/app.py` | Interface Streamlit completa da Sprint 3 |
| `sprint3/interface/.env.example` | Template de configuração da API key |
| `sprint3/interface/README.md` | Documentação técnica da interface |

---

## NLP e Automação de Resumos

> *"Eu transformo linguagem técnica em algo que qualquer pessoa entende."*

Módulo NLP que pós-processa as respostas do agente e gera resumos automáticos do relatório, sem alterar os fatos — apenas a forma como são comunicados.

### Componentes

| Arquivo | Função |
|---|---|
| `sprint3/nlp/nlp_simplificacao.py` | Simplificação de jargão genético para linguagem acessível |
| `sprint3/nlp/resumos_automaticos.py` | Geração de resumos por seção e geral do relatório |
| `sprint3/integracao/adaptador_nlp.py` | Adaptador para integração com o RAG personalizado |
| `sprint3/integracao/test_integracao_nlp.py` | 19 testes de integração NLP ↔ RAG |

---

##  Governança e Comunicação Responsável

> *"Eu garanto que o que o sistema diz é responsável — e que o que está documentado é verdadeiro."*

Detalhado na seção [10. Governança e Comunicação Responsável](#10-governança-e-comunicação-responsável).

---

## 8. Como executar o projeto

### Pré-requisitos

- Python 3.10 ou superior
- Conta na OpenAI com créditos ([platform.openai.com](https://platform.openai.com))
- Git

### Instalação

```bash
# 1. Clonar este repositório
git clone https://github.com/Carlos566487/Enterprise-Challenge-Sprint-3-DASA.git
cd Enterprise-Challenge-Sprint-3-DASA

# 2. Criar e ativar ambiente virtual
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt
```

### Configuração da API Key

```bash
# Copiar o arquivo de exemplo
cp sprint3/interface/.env.example sprint3/interface/.env

# Editar e inserir sua chave
# OPENAI_API_KEY=sk-...
```

> A chave também pode ser inserida diretamente na **sidebar da interface**, sem necessidade do arquivo `.env`.

### Gerar a base vetorial *(necessário apenas na primeira vez)*

```bash
python sprint2/pipeline/pipeline_completo.py
```

Saída esperada:
```
PIPELINE CONCLUÍDO em ~15s
  Chunks gerados: 25
  Base vetorial: sprint2/vetorial/base_vetorial/
  Pronto para busca semântica.
```

### Iniciar a interface da Sprint 3

```bash
streamlit run sprint3/interface/app.py
```

Acesse no navegador: **http://localhost:8501**

### Executar todos os testes

```bash
pytest -v
# 67 testes: 32 RAG + 19 integração + 16 governança — sem necessidade de API key
```

---

## 9. Estrutura do repositório

```
Enterprise-Challenge-Sprint-3-DASA/
│
├── dados_estruturados.json              ← JSON do relatório (base compartilhada)
├── README.md                            ← Este arquivo
├── requirements.txt                     ← Dependências do projeto
├── CHANGELOG.md                         ← Histórico de entregas por sprint
├── .gitignore
├── .flake8                              ← Configuração de linting
├── .pylintrc                            ← Configuração do Pylint
│
├── docs/
│   └── images/
│       ├── logo-fiap.png
│       ├── arquitetura.png
│       └── pipeline_rag_genera_ia.svg
│
├── sprint1/                             ← Engenharia de Dados
│   ├── README_engenheiro_dados.md
│   ├── mapeamento_secoes.md
│   ├── extracao_tecnica.md
│   ├── priorizacao_campos.md
│   └── exemplos_interacao.md
│
├── sprint2/                             ← Motor de Inteligência (herdado, não alterado)
│   ├── README_sprint2.md
│   ├── embeddings/gerar_embeddings.py
│   ├── vetorial/indexar.py · buscar.py
│   ├── pipeline/pipeline_completo.py
│   ├── agente/agente_especialista.py · prompts.py · guardrails.py · config_llm.py
│   ├── testes/testar_busca.py
│   └── interface/app.py · llm_connector.py
│
└── sprint3/                             ← Produto Usável — esta entrega
    │
    ├── interface/                       ← Endrew — Dashboard e UX
    │   ├── app.py                       ← Interface Streamlit completa (86 KB)
    │   ├── .env.example
    │   └── README.md
    │
    ├── rag_personalizacao/              ← João — Personalização do RAG
    │   ├── __init__.py
    │   ├── perfis.py
    │   ├── personalizador.py
    │   ├── ancoragem.py
    │   ├── historico.py
    │   └── test_personalizacao.py       ← 32 testes
    │
    ├── nlp/                             ← Tayná — NLP e Resumos
    │   ├── nlp_simplificacao.py
    │   ├── resumos_automaticos.py
    │   └── readme.md
    │
    ├── integracao/                      ← Integração NLP ↔ RAG
    │   ├── __init__.py
    │   ├── adaptador_nlp.py
    │   └── test_integracao_nlp.py       ← 19 testes
    │
    └── governanca/                      ← Carlos — Governança e Comunicação
        ├── __init__.py
        ├── disclaimers.py
        ├── revisor_linguagem.py
        └── test_governanca.py           ← 16 testes
```

> **Nota:** `chunks.json`, `base_vetorial/` e `.env` estão no `.gitignore` e devem ser gerados localmente. Nenhum PDF é versionado (política de privacidade — ver seção 10).

---

## 10. Governança e Comunicação Responsável

### Por que uma camada dedicada de governança?

Dados genéticos são intrinsecamente probabilísticos. Uma afirmação categórica como *"você vai desenvolver diabetes"* viola a boa prática médica: a genética indica **predisposição**, não certeza. Ao mesmo tempo, avisos genéricos repetitivos (um banner gigante em toda mensagem) treinam o usuário a ignorá-los — efeito oposto ao desejado.

A solução adotada é uma **camada de governança separada** com três responsabilidades distintas:

1. **Disclaimers contextuais** — exibidos no momento e local certos, não em todo lugar
2. **Revisão de linguagem** — pós-processamento determinístico que corrige alarmismo antes de exibir a resposta
3. **Documentação auditável** — o que está declarado na política de privacidade é verificável no repositório

### O que o agente faz — e o que não faz

| ✅ O agente FAZ | ❌ O agente NÃO FAZ |
|---|---|
| Explica termos genéticos em linguagem simples | Emite diagnósticos médicos |
| Apresenta predisposições como tendências estatísticas | Prescreve medicamentos ou tratamentos |
| Mostra as fontes de cada resposta | Responde fora do escopo do relatório |
| Admite quando não há informação suficiente | Completa lacunas com conhecimento externo |
| Redireciona para profissional quando necessário | Faz previsões médicas absolutas |
| Apresenta risco com contexto estatístico | Usa "risco altíssimo" sem qualificação |

### Disclaimers implementados

| Contexto | Onde é exibido |
|---|---|
| `banner` | Banner fixo no topo da interface em toda sessão |
| `sufixo_risco` | Sufixo automático em respostas sobre risco ou predisposição |
| `sidebar_privacidade` | Sidebar ao carregar qualquer relatório |
| `bloqueio_diagnostico` | Resposta padrão para perguntas diagnósticas bloqueadas |
| `rodape_exportacao` | Rodapé de relatórios exportados |

### Revisão de linguagem (`revisor_linguagem.py`)

Chamada **após** o LLM gerar a resposta e **antes** de exibi-la:

| Categoria | Exemplo de entrada | Saída corrigida |
|---|---|---|
| Certeza sobre doença | `"você vai desenvolver diabetes"` | `"você tem predisposição a desenvolver diabetes"` |
| Escala sem contexto | `"risco altíssimo"` | `"risco elevado (consulte um especialista)"` |
| Diagnóstico implícito | `"alto risco"` | `"maior atenção recomendada"` |
| Risco sem qualificador | `"risco para diabetes"` (sem contexto) | Adiciona: *"consulte um especialista para confirmação clínica"* |

A revisão é **determinística** (regex, sem chamada ao LLM), **idempotente** e **rastreável** (retorna log de alterações).

### Privacidade e LGPD

- Relatório PDF processado **localmente** — não persistido no servidor
- Base vetorial armazenada em disco local — **nunca enviada** externamente
- Apenas trechos relevantes + pergunta são enviados à API OpenAI
- Nenhuma informação pessoal armazenada além da sessão ativa
- `.env` com API key no `.gitignore` — nunca versionado
- `*.pdf` no `.gitignore` — nenhum PDF é versionado no repositório

A solução respeita a **LGPD — Art. 11** (dados sensíveis de saúde): processamento limitado à finalidade informativa, sem armazenamento persistente de dados pessoais.

---

## 11. Continuidade — Sprint 1 → Sprint 2 → Sprint 3

| Entregável | Sprint 1 | Sprint 2 | Sprint 3 |
|---|---|---|---|
| Relatório genético | PDF bruto | Indexado em base vetorial | Visualizado em dashboard |
| Dados | JSON estruturado | 25 chunks com embeddings 384D | Personalizado por perfil |
| IA | Proposta conceitual | Pipeline RAG funcional | RAG personalizado por usuário |
| Busca | Inexistente | Busca semântica por cosseno | Top-k adaptativo por perfil |
| Linguagem | Jargão técnico | Guardrails básicos | NLP + revisão de alarmismo |
| Interface | Wireframe / conceito | Chat funcional (Streamlit) | Dashboard completo + chat |
| Governança | Descrita | Implementada (guardrails) | Módulo dedicado + auditoria |
| Testes | — | Busca e agente | **67 testes** (32 RAG + 19 integração + 16 governança) |

---

## 12. Vídeo de apresentação

> 📹 **Sprint 1:** [https://youtu.be/0x63S_5DD_8](https://youtu.be/0x63S_5DD_8)

> 📹 **Sprint 2:** [https://youtu.be/z1Jqb33pSjU](https://youtu.be/z1Jqb33pSjU)

> 📹 **Sprint 3:** **[LINK DO VÍDEO — PENDENTE DE GRAVAÇÃO E PUBLICAÇÃO]**

---

<p align="center">
  <sub>Projeto desenvolvido para a disciplina de Inteligência Artificial · FIAP 2026</sub><br/>
  <sub>Genera AI · Dasa · Enterprise Challenge · Sprint 3</sub>
</p>
