# Sprint 2 — Integrante 1: Minerador de Dados

## Genera / Dasa / FIAP — Pipeline de Embeddings e Indexação Vetorial

---

## Para os outros integrantes — leia antes de tudo

Este documento explica o que foi feito nesta etapa, o que foi entregue para vocês e como usar.

### O que esta etapa faz

O Sprint 1 produziu o `dados_estruturados.json` com todos os dados do relatório genético já extraídos e organizados. Esta etapa pega esse JSON e transforma em uma **base vetorial pesquisável**, que é a fundação do sistema RAG.

Em termos simples:

```
dados_estruturados.json  →  chunks de texto  →  embeddings  →  ChromaDB
```

Quando o agente receber uma pergunta do paciente, ele vai buscar nessa base os trechos mais relevantes do relatório e usá-los como contexto para responder.

---

## O que foi entregue para cada integrante

### Para o Integrante 2 — Arquiteto da Busca

Você recebe a base vetorial pronta em:

```
sprint2/vetorial/base_vetorial/
```

**Como conectar:**

```python
import chromadb
from sentence_transformers import SentenceTransformer

BASE_VETORIAL = "sprint2/vetorial/base_vetorial"
COLECAO_NOME  = "genera_relatorio"
MODELO_NOME   = "all-MiniLM-L6-v2"  # use o mesmo modelo para gerar o embedding da pergunta

cliente  = chromadb.PersistentClient(path=BASE_VETORIAL)
colecao  = cliente.get_collection(COLECAO_NOME)
modelo   = SentenceTransformer(MODELO_NOME)

# Buscar os 3 trechos mais relevantes para uma pergunta
pergunta = "Eu tenho risco de diabetes?"
embedding = modelo.encode(pergunta).tolist()

resultados = colecao.query(
    query_embeddings=[embedding],
    n_results=3,
    include=["documents", "metadatas", "distances"]
)
```

**O que cada resultado contém:**

| Campo                      | Descrição                                                        |
| -------------------------- | ---------------------------------------------------------------- |
| `documents[0][i]`          | Texto do trecho relevante                                        |
| `metadatas[0][i]["secao"]` | Identificador da seção (ex: `resultado_2.1`, `recomendacao_2.1`) |
| `metadatas[0][i]["fonte"]` | Rastreabilidade até o campo do JSON original                     |
| `distances[0][i]`          | Distância cosseno — similaridade = `1 - distance`                |

**Importante:** use sempre o modelo `all-MiniLM-L6-v2` para gerar o embedding da pergunta. Se usar outro modelo, os vetores serão incompatíveis com a base.
Foi implementada a camada oficial de busca semântica em:

```txt
sprint2/vetorial/buscar.py
```
---

### Para o Integrante 3 — Domador do Agente

Você recebe os mesmos recursos do Integrante 2, mais o contexto de como os chunks estão organizados.

**Tipos de chunk disponíveis na base:**

| Seção              | Conteúdo                                                     | Quando aparece                      |
| ------------------ | ------------------------------------------------------------ | ----------------------------------- |
| `paciente`         | Nome, datas, médico solicitante                              | Perguntas de identificação          |
| `sumario`          | Visão geral, contagens por risco, recomendações prioritárias | Perguntas gerais sobre o relatório  |
| `resultado_2.X`    | Descrição simples + impacto prático da condição              | Perguntas sobre doenças específicas |
| `recomendacao_2.X` | Recomendação clínica + urgência                              | Perguntas sobre o que fazer         |
| `marcadores_2.X`   | Marcadores genéticos + descrição técnica                     | Perguntas técnicas (perfil médico)  |
| `ancestralidade`   | Composição ancestral completa                                | Perguntas sobre origem              |
| `metadata`         | Laboratório, responsável técnico, versão                     | Perguntas sobre o relatório em si   |

**Para o system prompt:** os chunks de `resultado_2.X` já contêm a `descricao_simples` e o `impacto_pratico` — linguagem já acessível para o paciente. Os chunks de `marcadores_2.X` contêm a `descricao_tecnica` — use para o perfil médico.

**Cada resposta do agente deve citar a `fonte` do chunk** — isso garante rastreabilidade e evita alucinações.

### Módulo implementado pelo Integrante 3 — Agente Especialista

A partir dos trechos recuperados pela busca semântica, foi desenvolvido um módulo responsável por controlar como o sistema interpreta e apresenta as respostas ao usuário.

Localização:

```txt
sprint2/agente/
```

Componentes implementados:

| Arquivo | Função |
|----------|--------|
| `config_llm.py` | Configuração do modelo e hiperparâmetros |
| `prompts.py` | System prompts e estratégias de resposta |
| `guardrails.py` | Regras de segurança médica |
| `agente_especialista.py` | Orquestração do fluxo do agente |
| `testes_agente.py` | Testes de validação |

Fluxo completo:

```txt
Pergunta
↓
Busca Semântica
↓
Trechos Recuperados
↓
Validação por Guardrails
↓
Construção do Prompt
↓
Geração da Resposta
↓
Exibição das Fontes
```

Diferenciais adicionados:

- arquitetura RAG controlada;
- respostas rastreáveis;
- suporte a modo paciente e modo técnico;
- recusa segura para perguntas médicas sensíveis;
- resposta controlada quando não existir contexto suficiente.

O agente foi projetado para explicar o relatório, e não substituir avaliação médica.

---

### Para o Integrante 4 — Construtor da Experiência

Para reindexar a base quando um novo relatório for carregado pelo usuário:

```bash
python sprint2/pipeline/pipeline_completo.py caminho/para/novo_relatorio.json
```

O pipeline apaga a coleção anterior e recria do zero. Leva cerca de 15 segundos.

---

## Estrutura de arquivos desta etapa

```
sprint2/
├── embeddings/
│   ├── gerar_embeddings.py   → divide o JSON em chunks e gera embeddings
│   └── chunks.json           → gerado automaticamente (não versionar)
├── vetorial/
│   ├── indexar.py            → indexa os chunks no ChromaDB
│   └── base_vetorial/        → base ChromaDB persistida (não versionar)
├── pipeline/
│   └── pipeline_completo.py  → executa as duas etapas em sequência
├── testes/
│   └── testar_busca.py       → valida a busca com 5 perguntas de exemplo
└── README_sprint2.md         → este arquivo
```

> `chunks.json` e `base_vetorial/` estão no `.gitignore` — cada integrante precisa rodar o pipeline localmente para gerá-los.

---

## Como rodar localmente

### 1. Instalar dependências

```bash
pip install chromadb sentence-transformers
```

### 2. Gerar a base vetorial (pipeline completo)

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

### 3. Validar que a busca funciona

```bash
python sprint2/testes/testar_busca.py
```

Saída esperada (exemplo):

```
PERGUNTA: Eu tenho risco de diabetes?
  [1] Similaridade: 0.5953 | Seção: resultado_2.1
      Condição: Diabetes Mellitus Tipo 2. Nível de risco: Alto...

PERGUNTA: Existe algum problema genético relacionado ao câncer?
  [1] Similaridade: 0.6305 | Seção: resultado_2.2
      Condição: Carcinoma de Mama (BRCA-relacionado). Nível de risco: Alto...
```

---

## Decisões técnicas

### Por que ChromaDB?

- Local e gratuito — sem conta externa, sem API key, sem servidor
- Persistência em disco — a base é salva e reutilizada entre execuções
- Distância cosseno configurada nativamente (`hnsw:space: cosine`)
- API simples, integração direta com Python

### Por que `all-MiniLM-L6-v2`?

- Gratuito e local — roda sem internet após o primeiro download
- Dimensão 384 — leve, rápido, adequado para o volume do projeto
- Boa qualidade para busca semântica em textos de saúde em português
- Padrão da comunidade para RAG em projetos acadêmicos

### Estratégia de chunking

Cada chunk representa uma unidade semântica, não um número fixo de tokens. Para cada condição genética são gerados 3 chunks separados: descrição simples (para o paciente), recomendação (para ações preventivas) e marcadores técnicos (para o médico). Isso garante que a busca recupere exatamente o tipo de informação que a pergunta pede.

---

## Números da base vetorial

| Métrica                 | Valor              |
| ----------------------- | ------------------ |
| Total de chunks         | 25                 |
| Dimensão dos embeddings | 384                |
| Modelo                  | all-MiniLM-L6-v2   |
| Distância               | Cosseno            |
| Coleção ChromaDB        | `genera_relatorio` |
