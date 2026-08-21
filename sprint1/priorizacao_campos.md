# Priorização de Campos — Mapa de Rastreabilidade

## User Stories → Campos JSON → Seções PDF → Exemplos de Interação

---

## USER STORY 1: "Como paciente, quero entender meu relatório genético em linguagem simples, para saber o que ele significa na prática"

**→ Campos do JSON necessários:**

- `sumario.resumo_executivo_paciente`
- `sumario.total_condicoes_analisadas`
- `sumario.condicoes_alto_risco`
- `sumario.condicoes_medio_risco`
- `sumario.condicoes_baixo_risco`
- `resultados[].doenca`
- `resultados[].risco`
- `resultados[].descricao_simples`
- `resultados[].impacto_pratico`

**→ Seções do PDF de origem:**

- Seção 0: Cabeçalho (identificação do paciente)
- Seção 1: Sumário Executivo (contagens por risco)
- Seção 2: Resultados das Análises Genéticas (todas as condições)

**→ Exemplo de interação:** Exemplo 1

---

## USER STORY 2: "Como paciente, quero fazer perguntas sobre meu exame, para esclarecer dúvidas específicas sobre meus resultados"

**→ Campos do JSON necessários:**

- `resultados[].doenca`
- `resultados[].risco`
- `resultados[].marcadores_geneticos[]`
- `resultados[].escore_poligênico_percentil`
- `resultados[].descricao_simples`
- `resultados[].descricao_tecnica`
- `resultados[].impacto_pratico`
- `resultados[].recomendacao`
- `resultados[].urgencia_medica`

**→ Seções do PDF de origem:**

- Seção 2: Resultados das Análises Genéticas (detalhes completos de cada condição)
- Seção 0: Cabeçalho (dados do paciente para personalização)

**→ Exemplo de interação:** Exemplo 2

---

## USER STORY 3: "Como paciente, quero receber recomendações personalizadas, para tomar decisões preventivas com base nos meus dados"

**→ Campos do JSON necessários:**

- `sumario.recomendacoes_prioritarias[]`
- `resultados[].recomendacao`
- `resultados[].urgencia_medica`
- `resultados[].impacto_pratico`
- `resultados[].risco`
- `resultados[].doenca`

**→ Seções do PDF de origem:**

- Seção 2: Resultados das Análises Genéticas (recomendações clínicas de cada condição)
- Seção 1: Sumário Executivo (visão geral para priorização)

**→ Exemplo de interação:** Exemplo 3

---

## USER STORY 4: "Como médico, quero visualizar rapidamente os principais riscos do paciente, para otimizar minha análise"

**→ Campos do JSON necessários:**

- `paciente.nome`
- `paciente.id_relatorio`
- `sumario.principais_riscos_medico[]`
- `sumario.condicoes_alto_risco`
- `sumario.cobertura_genomica_snps`
- `resultados[].doenca`
- `resultados[].risco`
- `resultados[].categoria`
- `resultados[].marcadores_geneticos[]`
- `resultados[].escore_poligênico_percentil`
- `resultados[].descricao_tecnica`
- `resultados[].relevancia_medico`
- `resultados[].urgencia_medica`

**→ Seções do PDF de origem:**

- Seção 0: Cabeçalho (identificação do paciente)
- Seção 1: Sumário Executivo (contagens e metodologia)
- Seção 2: Resultados das Análises Genéticas (dados técnicos completos)
- Seção 5: Rodapé (responsável técnico e versão do relatório)

**→ Exemplo de interação:** Exemplo 4

---

## USER STORY 5: "Como usuário, quero acessar meus dados de forma organizada, para facilitar a interpretação e acompanhamento"

**→ Campos do JSON necessários:**

- `paciente.*` (todos os campos de identificação)
- `sumario.total_condicoes_analisadas`
- `sumario.condicoes_alto_risco`
- `sumario.condicoes_medio_risco`
- `sumario.condicoes_baixo_risco`
- `resultados[].doenca`
- `resultados[].categoria`
- `resultados[].risco`
- `resultados[].escore_poligênico_percentil`
- `resultados[].marcadores_geneticos[]`
- `resultados[].urgencia_medica`
- `ancestralidade[]` (todos os campos)
- `metadata.data_processamento`
- `metadata.versao_relatorio`

**→ Seções do PDF de origem:**

- Seção 0: Cabeçalho (dados do paciente)
- Seção 1: Sumário Executivo (visão geral)
- Seção 2: Resultados das Análises Genéticas (dados organizados por condição)
- Seção 3: Análise de Ancestralidade (dados complementares)
- Seção 5: Rodapé (metadados e rastreabilidade)

**→ Exemplo de interação:** Exemplo 5

---

## Matriz de Prioridade por User Story

| Campo JSON                           | US1 | US2 | US3 | US4 | US5 | Prioridade Geral |
| ------------------------------------ | --- | --- | --- | --- | --- | ---------------- |
| `paciente.*`                         | ✅  | ✅  | ⚪  | ✅  | ✅  | 🔴 Alta          |
| `sumario.resumo_executivo_paciente`  | ✅  | ⚪  | ⚪  | ⚪  | ⚪  | 🟡 Média         |
| `sumario.principais_riscos_medico`   | ⚪  | ⚪  | ⚪  | ✅  | ⚪  | 🟡 Média         |
| `sumario.recomendacoes_prioritarias` | ⚪  | ⚪  | ✅  | ⚪  | ⚪  | 🟡 Média         |
| `resultados[].doenca`                | ✅  | ✅  | ✅  | ✅  | ✅  | 🔴 Máxima        |
| `resultados[].risco`                 | ✅  | ✅  | ✅  | ✅  | ✅  | 🔴 Máxima        |
| `resultados[].descricao_simples`     | ✅  | ✅  | ⚪  | ⚪  | ⚪  | 🔴 Alta          |
| `resultados[].descricao_tecnica`     | ⚪  | ✅  | ⚪  | ✅  | ⚪  | 🔴 Alta          |
| `resultados[].impacto_pratico`       | ✅  | ✅  | ✅  | ⚪  | ⚪  | 🔴 Alta          |
| `resultados[].marcadores_geneticos`  | ⚪  | ✅  | ⚪  | ✅  | ✅  | 🔴 Alta          |
| `resultados[].urgencia_medica`       | ⚪  | ✅  | ✅  | ✅  | ✅  | 🔴 Alta          |
| `resultados[].relevancia_medico`     | ⚪  | ⚪  | ⚪  | ✅  | ⚪  | 🟡 Média         |
| `ancestralidade[]`                   | ⚪  | ⚪  | ⚪  | ⚪  | ✅  | 🟢 Baixa         |
| `metadata.*`                         | ⚪  | ⚪  | ⚪  | ⚪  | ✅  | 🟢 Baixa         |

**Legenda:**

- ✅ Campo essencial para a User Story
- ⚪ Campo não utilizado na User Story
- 🔴 Prioridade Máxima/Alta — campos críticos para múltiplas US
- 🟡 Prioridade Média — campos importantes para US específicas
- 🟢 Prioridade Baixa — campos complementares ou de metadados

---

## Seções PDF por Prioridade (Baseado nas User Stories)

| Seção PDF                         | Prioridade | User Stories Atendidas  | Justificativa                    |
| --------------------------------- | ---------- | ----------------------- | -------------------------------- |
| **Seção 2: Resultados Genéticos** | 🔴 Máxima  | US1, US2, US3, US4, US5 | Core de todas as funcionalidades |
| **Seção 0: Cabeçalho**            | 🔴 Alta    | US1, US2, US4, US5      | Identificação e personalização   |
| **Seção 1: Sumário Executivo**    | 🔴 Alta    | US1, US4, US5           | Visão geral e priorização        |
| **Seção 5: Rodapé**               | 🟡 Média   | US4, US5                | Metadados e rastreabilidade      |
| **Seção 3: Ancestralidade**       | 🟡 Média   | US5                     | Dados complementares             |
| **Seção 4: Metodologia**          | 🟢 Baixa   | —                       | Auditoria técnica apenas         |

---

## Campos Novos Adicionados (Baseados nas User Stories)

Os seguintes campos foram **adicionados ao JSON original** para atender especificamente às User Stories:

### Para User Story 1 (linguagem simples):

- `sumario.resumo_executivo_paciente`
- `resultados[].impacto_pratico`

### Para User Story 3 (recomendações personalizadas):

- `sumario.recomendacoes_prioritarias[]`
- `resultados[].urgencia_medica`

### Para User Story 4 (visualização médica):

- `sumario.principais_riscos_medico[]`
- `resultados[].relevancia_medico`

### Para eficiência do laboratório (Dasa):

- `metadata.tempo_processamento_segundos`
- `metadata.qualidade_extracao`
- `metadata.campos_extraidos_total`
- `metadata.confiabilidade_dados`

Esses campos garantem que cada User Story tenha os dados necessários para ser implementada com qualidade.
