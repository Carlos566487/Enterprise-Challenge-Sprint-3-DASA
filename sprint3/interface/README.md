# 🧬 Interface Sprint 3 — Genera AI

Esta pasta contém a evolução da interface do projeto DASA/Genera para a **Sprint 3 — Experiência do Usuário**.

O objetivo desta etapa foi transformar os recursos técnicos desenvolvidos na Sprint 2 em uma experiência mais clara, visual e acessível para o usuário final.

## O que foi implementado

- Dashboard com visão geral do relatório genético.
- Cards com classificação visual dos principais resultados.
- Página de resultados com busca, filtros e detalhes.
- Visualização de ancestralidade.
- Resumo automático do relatório.
- Assistente conversacional integrado ao RAG da Sprint 2.
- Simplificação de linguagem utilizando NLP.
- Modos de resposta para paciente e perfil técnico.
- Exibição das fontes recuperadas pela busca semântica.
- Histórico de interações durante a sessão.
- Avisos e salvaguardas para evitar interpretação como diagnóstico médico.
- Interface responsiva para desktop e telas menores.
- Upload de novos relatórios JSON.

## Principais decisões de UX

A interface foi organizada para apresentar primeiro as informações mais importantes e permitir que o usuário acesse os detalhes quando desejar.

Algumas decisões adotadas:

- uso de linguagem menos alarmista;
- apresentação de “Alto risco” como “Maior atenção” na camada visual;
- separação entre visão geral e resultados detalhados;
- uso de cards e barras para facilitar a leitura;
- exibição apenas de dados pessoais necessários;
- disclaimer médico visível;
- responsividade para uso em dispositivos móveis.

Os dados originais do relatório não são alterados. As mudanças são apenas de apresentação e experiência do usuário.

## Integração com as Sprints anteriores

A interface reutiliza os componentes já desenvolvidos na Sprint 2:

```text
dados_estruturados.json
        ↓
Embeddings
        ↓
ChromaDB
        ↓
Busca semântica
        ↓
RAG
        ↓
Guardrails
        ↓
LLM
        ↓
NLP
        ↓
Interface Sprint 3
```
## Como executar a interface da Sprint 3

A partir da raiz do repositório, crie um ambiente virtual:

```bash
python -m venv .venv
```

### Windows / PowerShell

Você pode ativar o ambiente com:

```powershell
.\.venv\Scripts\Activate.ps1
```

Caso o PowerShell bloqueie a ativação por política de execução, não é obrigatório ativar o ambiente. Você pode utilizar diretamente o Python da pasta `.venv`.

### Instalar as dependências

Com o ambiente ativado:

```bash
pip install -r requirements.txt
```

Ou, sem ativar o ambiente virtual:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Executar o projeto

Com o ambiente ativado:

```bash
streamlit run sprint3/interface/app.py
```

Ou diretamente pelo ambiente virtual:

```powershell
.\.venv\Scripts\python.exe -m streamlit run sprint3/interface/app.py
```

Depois de alguns segundos, a aplicação será aberta no navegador.

Caso não abra automaticamente, acesse:

```text
http://localhost:8501
```

### Preparar o assistente

Com a aplicação aberta:

1. Acesse a barra lateral.
2. Clique em **Preparar assistente**.
3. Aguarde a mensagem:

```text
Assistente preparado.
Status: Pronto
```

Esse processo prepara os embeddings e a base vetorial utilizados pela busca semântica e pelo RAG.

### OpenAI API Key

A OpenAI API Key é necessária apenas para gerar respostas reais no assistente conversacional.

A chave pode ser informada no campo protegido disponível na barra lateral da aplicação.

A chave real **não deve ser enviada para o GitHub**.

O arquivo `.env.example` deve conter apenas um exemplo:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
```

Mesmo sem uma API Key, ainda é possível testar:

- dashboard;
- cards de resultados;
- página **Meus resultados**;
- busca e filtros;
- ancestralidade;
- resumo automático;
- responsividade;
- upload de arquivos JSON;
- preparação da base vetorial.

### Encerrar a aplicação

No terminal em que o Streamlit está sendo executado, pressione:

```text
Ctrl + C
```

para encerrar o servidor.
