# CHANGELOG — Genera AI · Dasa · FIAP

Este arquivo documenta o histórico de entregas do projeto por sprint, incluindo
trabalho produzido fora do fluxo de commits git (ex: desenvolvimento local,
ferramentas de IA, iterações internas) para que o avaliador tenha visibilidade
completa do progresso real.

> **Nota de transparência:** O repositório possui histórico de commits esparso
> porque parte do desenvolvimento foi feita diretamente nos arquivos locais
> (com ferramentas como VS Code, Antigravity/Opal e Jupyter) sem push
> intermediário. Os arquivos entregues estão no estado funcional descrito abaixo.

---

## Sprint 3 — 2026-06-14 a 2026-08-20
**Tema:** Produto Usável — Dashboard, Personalização, NLP e Governança

### Entregáveis produzidos nesta sprint

| Módulo | Responsável | Arquivos | Status |
|---|---|---|---|
| `sprint3/interface/app.py` | Endrew Alves | Interface Streamlit completa (86 KB) com dashboard, cards, ancestralidade, resumo, chat | ✅ Concluído |
| `sprint3/rag_personalizacao/` | João | perfis.py, personalizador.py, ancoragem.py, historico.py, 32 testes | ✅ Concluído |
| `sprint3/nlp/` | Tayná Esteves | nlp_simplificacao.py, resumos_automaticos.py, integracao/agente_nlp.py | ✅ Concluído |
| `sprint3/integracao/` | João + Tayná | adaptador_nlp.py, 19 testes de integração | ✅ Concluído |
| `sprint3/governanca/` | Carlos Eduardo | disclaimers.py, revisor_linguagem.py, 16 testes, README | ✅ Concluído |
| `README.md` raiz | Carlos Eduardo | Atualizado para Sprint 3, seções de equipe e governança | ✅ Concluído |
| `.gitignore` | Carlos Eduardo | Adicionado padrão `*.pdf` (política de privacidade) | ✅ Concluído |
| `CHANGELOG.md` | Carlos Eduardo | Este arquivo | ✅ Concluído |

### Linha do tempo (estimada)

| Período | Atividade |
|---|---|
| Jun/2026 (semanas 1–2) | Definição de escopo da Sprint 3, divisão de responsabilidades |
| Jun/2026 (semanas 3–4) | Desenvolvimento do módulo de personalização RAG (João) |
| Jul/2026 (semanas 1–2) | Desenvolvimento do dashboard (Endrew) |
| Jul/2026 (semanas 3–4) | Módulo NLP e integração (Tayná) |
| Ago/2026 (semana 1–2) | Módulo de governança, disclaimers, revisão de linguagem (Carlos) |
| Ago/2026 (semana 3) | Testes, documentação, commit e entrega |

### Nota sobre o commit único no histórico

O repositório apresenta apenas 1 commit visível (`e406b5a — 2026-06-13`), feito por
um agente de IA durante uma sessão de documentação. Todo o conteúdo das pastas
`sprint1/`, `sprint2/` e `sprint3/` foi desenvolvido fora do fluxo de commits
regulares e está sendo consolidado e commitado nesta data (2026-08-20) como
parte da entrega final da Sprint 3.

Isso **não representa ausência de trabalho** — os arquivos entregues têm
complexidade, testes e documentação que evidenciam o desenvolvimento realizado.

---

## Sprint 2 — 2026-04 a 2026-06-13
**Tema:** Inteligência do Sistema — RAG, Embeddings, Agente, Interface

### Entregáveis produzidos

| Módulo | Responsável | Descrição |
|---|---|---|
| `sprint2/embeddings/gerar_embeddings.py` | João | Pipeline de chunking e embeddings (25 chunks, 384D) |
| `sprint2/vetorial/indexar.py`, `buscar.py` | Endrew | Indexação ChromaDB e busca semântica por cosseno |
| `sprint2/agente/` | Tayná | Orquestrador, prompts, guardrails, config LLM, testes |
| `sprint2/interface/app.py`, `llm_connector.py` | Carlos | Interface Streamlit + integração OpenAI real |
| `dados_estruturados.json` | — | JSON do relatório (base compartilhada gerada na Sprint 1) |

**Vídeo Sprint 2:** https://youtu.be/z1Jqb33pSjU

---

## Sprint 1 — 2026-02 a 2026-04
**Tema:** Engenharia de Dados — Extração e Estruturação do Relatório PDF

### Entregáveis produzidos

| Arquivo | Descrição |
|---|---|
| `sprint1/README_engenheiro_dados.md` | Documentação técnica da sprint |
| `sprint1/mapeamento_secoes.md` | Mapeamento das seções do relatório PDF |
| `sprint1/extracao_tecnica.md` | Decisões técnicas de extração (pdfplumber, PyMuPDF) |
| `sprint1/priorizacao_campos.md` | Critérios de priorização dos campos |
| `sprint1/exemplos_interacao.md` | Exemplos de interação com o sistema |
| `dados_estruturados.json` | Produto final: JSON estruturado do relatório |

**Vídeo Sprint 1:** https://youtu.be/0x63S_5DD_8
