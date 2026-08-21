# Integrante 4 — Construtor da Experiência
## Genera AI · Sprint 2 · FIAP

---

## Responsabilidade no Projeto

O Integrante 4 é responsável por integrar os módulos desenvolvidos pelos demais
integrantes em uma **interface conversacional funcional e demonstrável**, conectar
o agente ao **LLM real da OpenAI** e garantir que todos os elementos de segurança,
rastreabilidade e conformidade estejam visíveis ao usuário final.

Enquanto os Integrantes 1, 2 e 3 construíram o pipeline de dados, a busca semântica
e o agente com guardrails, o Integrante 4 entrega a **experiência completa**:
a superfície com a qual o usuário interage, o elo que conecta cada módulo, e a
camada que substitui a resposta simulada por uma resposta gerada pelo GPT-4.1 Mini
em tempo real — sem alterar nenhum arquivo existente.

---

## Arquitetura da Interface

```
Usuário
  │
  ▼
[app.py — Streamlit]
  │
  ├─── Carregamento do relatório
  │         │
  │         ▼
  │    pipeline_completo.py (Integrante 1)
  │    dados_estruturados.json → chunks → ChromaDB
  │
  ├─── Pergunta do usuário
  │         │
  │         ▼
  │    buscar_contexto() (Integrante 2 · buscar.py)
  │    ChromaDB · all-MiniLM-L6-v2 · similaridade cosseno
  │         │
  │         ▼ trechos relevantes (conteudo, secao, fonte, similaridade)
  │         │
  │         ▼
  │    responder() (Integrante 3 · agente_especialista.py)
  │    guardrails → construção do prompt → SYSTEM_PROMPT
  │         │
  │         ▼ prompt_final montado
  │         │
  │         ▼
  │    chamar_openai() (Integrante 4 · llm_connector.py)
  │    GPT-4.1 Mini · temperatura 0.2 · max_tokens 700
  │         │
  │         ▼
  └─── Resposta + fontes exibidas no chat
```

---

## Arquivos Entregues

| Arquivo | Responsabilidade |
|---|---|
| `app.py` | Interface Streamlit completa — chat, sidebar, estado, renderização |
| `llm_connector.py` | Integração real com OpenAI; substitui `gerar_resposta_simulada()` |
| `.env.example` | Template para configurar a API Key |
| `README_integrante4.md` | Esta documentação |

---

## Decisões Técnicas

### Por que Streamlit?

Prototipagem rápida com gerenciamento de estado nativo (`st.session_state`),
sem necessidade de backend separado. Permite entrega funcional sem a
complexidade de FastAPI + React, adequado para o escopo acadêmico do Sprint 2.
O histórico de mensagens, modo de resposta e estado da base vetorial são
mantidos nativamente entre interações sem código extra de gerenciamento.

### Por que `llm_connector.py` é um arquivo separado e não modifica o agente?

O `agente_especialista.py` é responsabilidade do Integrante 3.
Criar uma camada de integração separada **respeita a divisão de papéis**,
permite que o agente continue funcionando com a resposta simulada para
os testes do Integrante 3, e **isola a dependência da API OpenAI** em um
único arquivo — facilitando troca de modelo ou provedor no futuro sem tocar
na lógica de guardrails.

### Por que GPT-4.1 Mini?

Definido pelo Integrante 3 em `config_llm.py`. O Integrante 4 respeita
essa decisão e importa os mesmos hiperparâmetros (`TEMPERATURA = 0.2`,
`TOP_P = 0.8`, `MAX_TOKENS = 700`) diretamente de `config_llm.py`,
garantindo consistência entre o que o agente espera e o que o LLM recebe.

### Por que importar `construir_prompt_final` e `montar_contexto` do agente?

Para **não duplicar lógica**. O `llm_connector.py` não reescreve a montagem
do prompt — ele importa as mesmas funções que o `agente_especialista.py`
usaria internamente, garantindo que o prompt enviado ao LLM real seja
idêntico ao que a versão simulada usaria. Isso também significa que qualquer
atualização que o Integrante 3 fizer no `SYSTEM_PROMPT` ou na estrutura do
prompt será automaticamente refletida nas respostas reais.

### Rastreabilidade das fontes

Cada resposta exibe os trechos exatos do relatório que embasaram a geração,
com similaridade cosseno, nome da seção e rastreabilidade até o campo do
JSON original. Isso é um **requisito do projeto**, não uma feature opcional:
o usuário deve poder verificar de onde cada informação foi extraída.

---

## Como Executar

```bash
# 1. A partir da raiz do repositório
pip install -r requirements.txt

# 2. Configurar API Key
cp sprint2/interface/.env.example sprint2/interface/.env
# Editar .env e inserir OPENAI_API_KEY=sk-...

# 3. Gerar a base vetorial (necessário antes do primeiro uso)
python sprint2/pipeline/pipeline_completo.py

# 4. Iniciar a interface
streamlit run sprint2/interface/app.py
```

> **Atalho:** Se preferir, insira a API Key diretamente na sidebar da
> interface (campo `OpenAI API Key`) — sem necessidade de arquivo `.env`.

---

## Fluxo de Uso

```
1. Usuário abre a interface no navegador (localhost:8501)
2. Insere a API Key na sidebar (ou configura no .env)
3. Clica em "▶ Usar relatório de demonstração" (ou faz upload do JSON)
4. Pipeline é executado automaticamente (~15 segundos)
5. Interface exibe: "✅ Relatório de [Nome] carregado — 25 trechos indexados"
6. Usuário digita uma pergunta ou clica em pergunta frequente
7. Sistema busca trechos relevantes → guardrails → GPT-4.1 Mini → exibe resposta
8. Fontes, seção e similaridade ficam disponíveis no expander "📄 Fontes utilizadas"
```

---

## Guardrails e Governança

### Limites do agente (implementados pelo Integrante 3, visíveis na interface)

| Categoria | Exemplo de pergunta bloqueada | Resposta exibida |
|---|---|---|
| Diagnóstico | "Tenho diabetes?" | 🚫 Mensagem explicativa em fundo âmbar |
| Prescrição | "Qual remédio devo tomar?" | 🚫 Mensagem explicativa em fundo âmbar |
| Risco alto | "Quanto tempo vou viver?" | 🚫 Mensagem explicativa em fundo âmbar |
| Fora de escopo | "Me dê uma dieta para emagrecer" | 🚫 Mensagem explicativa em fundo âmbar |
| Sem contexto | Pergunta sem trechos relevantes no ChromaDB | ℹ️ Mensagem em fundo azul |

O `llm_connector.py` **não chama a API OpenAI** quando o status é `"bloqueado"`
ou `"sem_contexto"` — o guardrail decide antes, economizando tokens e
garantindo que respostas inadequadas nunca sejam geradas.

### Privacidade

- Relatório processado **localmente** (ChromaDB em disco, não em nuvem)
- Único dado enviado externamente: trechos relevantes + pergunta à API OpenAI
- Nenhum dado é persistido além da sessão do Streamlit
- Arquivos de upload removidos automaticamente após indexação

### Disclaimers

- **Banner permanente** no topo da interface em toda sessão
- Aviso visível na sidebar sobre natureza informativa do assistente
- Rodapé com referência à LGPD Art. 11 (dados de saúde)

---

## Tratamento de Erros

| Situação | Comportamento |
|---|---|
| API key ausente | Campo visível na sidebar; `st.stop()` impede envio |
| API key inválida | `🔑` Mensagem de erro clara; histórico não corrompido |
| Quota excedida | `💳` Mensagem direcionando ao painel OpenAI |
| Base vetorial ausente | `⚙️` Instrução para executar pipeline; não quebra |
| Erro genérico | `❌` Mensagem com detalhe técnico; mensagem do usuário removida do histórico |

> Em todos os casos de erro, a mensagem do usuário é removida do histórico
> para que ele possa tentar novamente sem poluição visual.

---

## Dependências

```
streamlit>=1.32.0          # Interface web e gerenciamento de estado
openai>=1.0.0              # SDK oficial OpenAI (GPT-4.1 Mini)
chromadb>=0.4.0            # Base vetorial (usada pelo Integrante 2)
sentence-transformers>=2.2.0  # Modelo all-MiniLM-L6-v2 (usado pelo Integrante 2)
python-dotenv>=1.0.0       # Carregamento do arquivo .env
```

---

## Vídeo de Apresentação

🎥 Link: [a ser publicado como não listado no YouTube]

---

*Genera AI · Sprint 2 · FIAP · 2026*
