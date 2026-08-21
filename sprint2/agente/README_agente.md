# 1. Decisões Técnicas do Agente

## Objetivo

Desenvolver um agente especialista capaz de interpretar relatórios genéticos estruturados e responder perguntas em linguagem natural de forma clara, segura e rastreável.

O agente não realiza diagnósticos médicos e opera exclusivamente sobre informações recuperadas do relatório por meio da arquitetura RAG (Retrieval-Augmented Generation).

---

## Modelo de Linguagem Escolhido

Modelo principal:
GPT-4.1 Mini

Modelo alternativo:
Gemini Flash

Justificativa:
O modelo foi escolhido por apresentar bom desempenho em interpretação textual, seguimento de instruções e integração com arquiteturas RAG, permitindo respostas mais consistentes e menor probabilidade de alucinação.

---

## Configuração do Modelo

| Parâmetro | Valor |
|----------|------|
| Temperatura | 0.2 |
| Top-p | 0.8 |
| Máximo de Tokens | 700 |
| Frequency Penalty | 0 |
| Presence Penalty | 0 |

---

## Estratégia de Resposta

O agente opera em dois modos:

### Modo Paciente
Explicações simplificadas, acessíveis e sem linguagem alarmista.

### Modo Técnico
Explicações mais detalhadas e técnicas para usuários avançados.

---

## Restrições

O agente:

✓ Responde apenas com base no relatório carregado  
✓ Explica termos genéticos  
✓ Exibe fontes utilizadas  

O agente NÃO:

✗ Diagnostica doenças  
✗ Prescreve tratamentos  
✗ Responde fora do escopo do relatório

# 2. Estrutura do Módulo do Agente

O módulo `agente/` foi criado para concentrar toda a lógica responsável pelo comportamento conversacional da solução Genera AI.

Enquanto as demais etapas do projeto tratam da extração, estruturação, geração de embeddings e busca semântica, este módulo define como o agente interpreta os trechos recuperados e transforma essas informações em respostas seguras, claras e rastreáveis para o usuário final.

## Organização dos Arquivos

| Arquivo | Responsabilidade |
|--------|------------------|
| `config_llm.py` | Define o modelo de linguagem e os hiperparâmetros utilizados pelo agente. |
| `prompts.py` | Armazena o system prompt, templates de resposta e prompts de fallback. |
| `guardrails.py` | Implementa regras de segurança para impedir diagnóstico, prescrição e respostas fora do escopo. |
| `agente_especialista.py` | Orquestra o fluxo principal do agente, combinando pergunta, contexto recuperado, prompts e validações. |
| `testes_agente.py` | Reúne testes com perguntas comuns, ambíguas e perguntas-limite para validar o comportamento do agente. |

## Papel do Módulo na Arquitetura RAG

O agente não acessa diretamente o relatório bruto. Ele recebe trechos previamente recuperados pela busca semântica e utiliza esses trechos como única base para formular a resposta.

Fluxo esperado:

```txt
Pergunta do usuário
↓
Busca semântica no relatório
↓
Trechos relevantes recuperados
↓
Aplicação dos guardrails
↓
Construção do prompt final
↓
Resposta do agente
↓
Exibição das fontes utilizadas

# 3. Guardrails Médicos

O agente possui uma camada de validação antes da geração da resposta. Essa camada impede que perguntas sensíveis sejam enviadas diretamente ao modelo de linguagem quando envolvem diagnóstico, prescrição, previsão médica absoluta ou temas fora do escopo do relatório.

## Categorias Bloqueadas

| Categoria | Exemplo | Comportamento esperado |
|----------|---------|------------------------|
| Diagnóstico | "Tenho câncer?" | Recusa segura e orientação para profissional de saúde |
| Prescrição | "Qual remédio devo tomar?" | Recusa indicação de medicamento ou dose |
| Risco alto | "Quanto tempo vou viver?" | Explica que genética não define prognóstico individual |
| Fora do escopo | "Qual dieta devo fazer?" | Informa que responde apenas sobre o relatório genético |
| Sem contexto | Nenhum trecho recuperado | Responde que não há informação suficiente |

## Objetivo dos Guardrails

Os guardrails reduzem riscos de alucinação, interpretações indevidas e uso inadequado do sistema em contexto de saúde.

O agente foi projetado para atuar como uma ferramenta educativa e explicativa, não como ferramenta diagnóstica.

# 4. Agente Especialista

O arquivo `agente_especialista.py` concentra a lógica principal do agente conversacional.

Ele recebe uma pergunta do usuário, valida a segurança da pergunta por meio dos guardrails, organiza os trechos recuperados pela busca semântica e constrói o prompt final que será enviado ao modelo de linguagem.

## Fluxo do Agente

```txt
Pergunta do usuário
↓
Validação dos guardrails
↓
Recebimento dos trechos recuperados pelo RAG
↓
Validação de contexto
↓
Construção do prompt final
↓
Geração da resposta
↓
Retorno com resposta + fontes

```

## Estratégia de Funcionamento

O agente foi desenvolvido seguindo o padrão RAG (Retrieval-Augmented Generation).

Diferente de um chatbot tradicional, ele não gera respostas livremente.

Toda resposta segue o seguinte processo:

1. Receber pergunta do usuário
2. Validar segurança da pergunta
3. Receber contexto recuperado pela busca semântica
4. Construir prompt controlado
5. Gerar resposta
6. Exibir fontes utilizadas

---

## Componentes Internos

### Construção de Contexto

A função `montar_contexto()` organiza os trechos recuperados pelo mecanismo de busca vetorial em um formato padronizado para consumo pelo modelo.

Exemplo:

```txt
[Fonte 1]
Predisposição genética moderada...

[Fonte 2]
Marcadores relacionados...
```

---

### Construção do Prompt

A função `construir_prompt_final()` combina:

- System Prompt
- Modo selecionado
- Contexto recuperado
- Pergunta do usuário

Objetivo:

- reduzir alucinações
- garantir rastreabilidade
- manter consistência de linguagem

---

### Modos de Resposta

| Modo | Objetivo |
|------|----------|
| paciente | Linguagem simples e acolhedora |
| técnico | Linguagem detalhada e precisa |

---

### Tratamento de Ausência de Dados

Caso nenhum trecho relevante seja encontrado:

```txt
Não encontrei informações suficientes no relatório enviado para responder com segurança.
```

Isso evita que o modelo complete lacunas utilizando conhecimento externo.

---

## Benefícios da Arquitetura

✓ Redução de alucinação do modelo  
✓ Maior segurança em contexto médico  
✓ Respostas rastreáveis  
✓ Separação entre recuperação e geração  
✓ Facilidade de manutenção e escalabilidade  

---

## Evolução Futura

Na integração final do projeto, a função simulada de geração poderá ser substituída por uma conexão direta com APIs de modelos de linguagem como GPT-4.1 Mini ou Gemini Flash.

Essa decisão permite desenvolvimento incremental sem bloquear o restante do grupo.

# 5. Testes e Validação do Agente

Para reduzir riscos de comportamento imprevisível, foi implementada uma etapa dedicada de validação do agente.

Os testes simulam cenários reais e cenários extremos.

---

## Categorias Testadas

| Categoria | Objetivo |
|----------|----------|
| Resposta normal | Verificar interpretação correta |
| Termo técnico | Avaliar simplificação da linguagem |
| Diagnóstico | Validar bloqueio seguro |
| Prescrição | Validar recusa de indicação |
| Fora do escopo | Garantir foco no relatório |
| Risco alto | Evitar conclusões sensíveis |
| Modo técnico | Validar profundidade |
| Sem contexto | Validar comportamento sem dados |

---

## Métrica de Aprovação

Um teste é considerado aprovado quando o agente:

✓ responde com base no contexto  
✓ recusa perguntas proibidas  
✓ admite ausência de informação  
✓ mantém linguagem segura  

---

## Resultado Esperado

```txt
Testes aprovados: 8/8
Confiabilidade: 100%
```

---

## Justificativa

A existência dessa camada de validação reduz alucinação e aumenta confiabilidade em aplicações que lidam com informações genéticas e saúde.

# 6. Impacto para Negócio e Diferenciais da Solução

O módulo do agente foi projetado para não atuar apenas como uma interface conversacional, mas como uma camada de interpretação segura capaz de ampliar o valor percebido dos relatórios genéticos.

---

## Problema Atual

Relatórios genéticos possuem alto valor científico, porém apresentam barreiras como:

- excesso de linguagem técnica;
- baixa taxa de leitura completa;
- dificuldade de interpretação;
- aumento de dúvidas para canais de atendimento.

---

## Solução Proposta

O agente transforma relatórios extensos em conversas contextualizadas e rastreáveis.

Exemplo:

Antes:

```txt
Paciente recebe PDF
↓
Não entende o conteúdo
↓
Abandona leitura
```

Depois:

```txt
Paciente pergunta
↓
Agente busca trechos relevantes
↓
Explica em linguagem natural
↓
Paciente entende o relatório
```

---

## Diferenciais Implementados

| Diferencial | Benefício |
|------------|-----------|
| RAG | Redução de alucinação |
| Guardrails | Segurança em saúde |
| Respostas rastreáveis | Transparência |
| Modo paciente/técnico | Personalização |
| Fallback seguro | Maior confiabilidade |
| Testes de validação | Qualidade contínua |

---

## Potencial de Evolução

A arquitetura permite futuras extensões:

### Histórico longitudinal

Comparar relatórios do mesmo usuário ao longo do tempo.

---

### Memória contextual

Adaptar profundidade das respostas conforme perfil do paciente.

---

### Explicações multimodais

Transformar resultados em gráficos e explicações visuais.

---

### Insights preventivos

Exemplo:

"Você perguntou sobre metabolismo. Existem fatores ambientais que costumam influenciar esse marcador."

(Sempre sem substituir orientação médica.)

---

## Indicadores de Sucesso (KPIs)

| Indicador | Objetivo |
|----------|----------|
| Taxa de perguntas respondidas | >90% |
| Redução de respostas fora do escopo | >80% |
| Taxa de leitura do relatório | aumento |
| Confiança do usuário | aumento |
| Redução de suporte humano | redução |

---

# Conclusão

O módulo Genera AI foi desenvolvido para atuar como um interpretador genético seguro, rastreável e centrado no usuário.

A proposta combina recuperação semântica, engenharia de prompts, controle de comportamento e mecanismos de validação para entregar uma experiência mais compreensível sem abrir mão da responsabilidade em contexto de saúde.

A arquitetura foi desenhada para permitir evolução futura sem dependência de um modelo específico de linguagem.

# 7. Rastreabilidade das Respostas

Como o sistema opera em contexto de saúde, todas as respostas do agente devem possuir rastreabilidade explícita.

Isso significa que cada interpretação apresentada ao usuário precisa indicar quais trechos recuperados do relatório foram utilizados na construção da resposta.

---

## Objetivos da Rastreabilidade

- reduzir alucinação do modelo;
- aumentar transparência;
- permitir auditoria da resposta;
- garantir alinhamento com aplicações em saúde;
- preservar confiança do usuário.

---

## Estratégia Implementada

O agente recebe os trechos recuperados pela busca semântica e devolve esses mesmos trechos junto da resposta.

Estrutura:

```txt
Pergunta
↓
Busca Semântica
↓
Trechos Recuperados
↓
Resposta Gerada
↓
Exibição das Fontes
```

---

## Exemplo

Entrada:

```txt
Pergunta:
Existe predisposição genética para diabetes?
```

Saída:

```txt
Resumo:
Foi identificada associação genética moderada.

Explicação:
O relatório sugere associação genética relacionada ao metabolismo da glicose.

Na prática:
Esse resultado representa tendência estatística e não diagnóstico.

Baseado em:
resultado_2.1
recomendacao_2.1
```

---

## Comportamento Esperado

Se nenhuma fonte for recuperada:

```txt
Não encontrei informações suficientes no relatório enviado para responder com segurança.
```

O agente nunca deve complementar respostas utilizando conhecimento externo.
