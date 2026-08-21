# Mapeamento das Seções do PDF Simulado

## Relatório Genera — `relatorio_genera_simulado.pdf`

---

## Visão Geral da Estrutura

O PDF simulado é um documento nativo (texto selecionável, não escaneado), gerado programaticamente com formatação profissional. Possui **4 páginas** organizadas nas seguintes seções principais:

---

## Seção 0 — Cabeçalho / Identificação do Documento

**Tipo de dado:** Texto estruturado em tabela  
**Aparência no PDF:** Bloco no topo de todas as páginas com logotipo, título e dados do paciente em grade de 4 colunas.
**🔴 PRIORIDADE: ALTA** — Essencial para User Stories 1, 4 e 5 (identificação do paciente e organização dos dados)

| Campo              | Exemplo                          |
| ------------------ | -------------------------------- |
| Nome do paciente   | Carlos Eduardo Mendes            |
| Data de nascimento | 14/03/1985                       |
| CPF                | `***.***.***-**` (anonimizado)   |
| ID do relatório    | GEN-2024-00847                   |
| Data do exame      | 05/11/2024                       |
| Data de emissão    | 12/11/2024                       |
| Médico solicitante | Dra. Fernanda Lopes CRM/SP 87432 |
| Laboratório        | Dasa Genômica — SP               |

**Desafio de extração:** Os campos estão em células de tabela sem rótulos explícitos em linha separada — o extrator precisa associar rótulo (coluna par) ao valor (coluna ímpar).

---

## Seção 1 — Sumário Executivo

**Tipo de dado:** Texto corrido + tabela de resumo numérico  
**Aparência no PDF:** Parágrafo descritivo seguido de tabela com 5 colunas de contagem.
**🔴 PRIORIDADE: ALTA** — Crítico para User Stories 4 e 5 (visualização rápida para médicos e dados organizados)

**Conteúdo:**

- Descrição da metodologia de coleta (saliva) e plataforma de genotipagem (Illumina GSA v3.0)
- Totais consolidados: condições analisadas, distribuição por nível de risco
- Aviso legal sobre caráter informativo do relatório

**Tabela de resumo:**

| Condições Analisadas | Risco Alto | Risco Médio | Risco Baixo | Cobertura Genômica |
| -------------------- | ---------- | ----------- | ----------- | ------------------ |
| 7                    | 2          | 3           | 2           | 654.027 SNPs       |

**Desafio de extração:** O aviso legal aparece em fonte menor e pode ser confundido com rodapé — deve ser identificado como campo `aviso_legal` e não como dado clínico.

---

## Seção 2 — Resultados das Análises Genéticas

**Tipo de dado:** Misto — tabela de classificação + texto técnico corrido  
**Aparência no PDF:** Cada condição ocupa um bloco com subtítulo numerado (2.1, 2.2 ... 2.7), seguido de tabela de 3 colunas e dois parágrafos de texto.
**🔴 PRIORIDADE: MÁXIMA** — Essencial para TODAS as User Stories (1, 2, 3, 4, 5)

### Estrutura de cada condição:

```
[Subtítulo numerado] Nome da Doença
┌─────────────────────────────────────────────────────────┐
│ Nível de Risco │ Categoria │ Marcadores Principais       │
│ ALTO/MÉDIO/BAIXO │ Especialidade │ RS##### (gene) — alelo │
└─────────────────────────────────────────────────────────┘
Descrição Técnica: [texto com terminologia genômica]
Recomendação Clínica: [texto com orientações médicas]
```

### Condições presentes:

| ID  | Doença                                      | Risco | Categoria                      | Relevância User Stories |
| --- | ------------------------------------------- | ----- | ------------------------------ | ----------------------- |
| 2.1 | Diabetes Mellitus Tipo 2                    | ALTO  | Metabolismo e Endocrinologia   | US1,2,3,4,5             |
| 2.2 | Carcinoma de Mama (BRCA-relacionado)        | ALTO  | Oncologia                      | US1,2,3,4,5             |
| 2.3 | Hipertensão Arterial Essencial              | MÉDIO | Cardiologia                    | US1,2,3,4,5             |
| 2.4 | Doença de Alzheimer (início tardio)         | MÉDIO | Neurologia                     | US1,2,3,4,5             |
| 2.5 | Doença Celíaca                              | MÉDIO | Gastroenterologia / Imunologia | US1,2,3,4,5             |
| 2.6 | Trombofilia Hereditária (Fator V de Leiden) | BAIXO | Hematologia                    | US1,2,3,4,5             |
| 2.7 | Intolerância à Lactose (tipo adulto)        | BAIXO | Nutrigenômica                  | US1,2,3,4,5             |

**Desafio de extração:**

- Os marcadores genéticos aparecem em célula única separados por `|` — precisam ser divididos em lista
- A descrição técnica e a recomendação são parágrafos consecutivos identificados apenas pelo rótulo em negrito no início
- Termos como `ε3/ε4`, `c.5946delT` e `p.Ser1982Argfs` contêm caracteres especiais que podem ser corrompidos em extratores simples

---

## Seção 3 — Análise de Ancestralidade

**Tipo de dado:** Texto introdutório + tabela de percentuais  
**Aparência no PDF:** Parágrafo metodológico seguido de tabela de 3 colunas com 7 regiões.
**🟡 PRIORIDADE: MÉDIA** — Relevante para User Story 5 (dados organizados) mas não crítica para as demais

| Região                          | Percentual | Intervalo de Confiança |
| ------------------------------- | ---------- | ---------------------- |
| Europa Ibérica                  | 42,3%      | 39,1% – 45,5%          |
| Europa do Sul                   | 18,7%      | 16,2% – 21,2%          |
| África Subsaariana              | 22,1%      | 19,4% – 24,8%          |
| Ameríndio (América do Sul)      | 11,4%      | 9,2% – 13,6%           |
| Oriente Médio / Norte da África | 3,8%       | 2,1% – 5,5%            |
| Ásia do Leste                   | 1,2%       | 0,3% – 2,1%            |
| Outros / Não determinado        | 0,5%       | 0,0% – 1,2%            |

**Desafio de extração:** Os percentuais usam vírgula decimal (padrão brasileiro) — o parser deve tratar `42,3%` como `42.3` numericamente.

---

## Seção 4 — Metodologia e Controle de Qualidade

**Tipo de dado:** Texto corrido + tabela técnica  
**Aparência no PDF:** Parágrafo descritivo + tabela de 3 colunas com etapas do pipeline laboratorial.
**🟢 PRIORIDADE: BAIXA** — Relevante apenas para laboratório/Dasa (eficiência), não impacta User Stories do paciente/médico

**Conteúdo:** Descreve as etapas do pipeline bioinformático (extração de DNA, genotipagem, controle de qualidade, imputação, análise de risco, ancestralidade, anotação de variantes).

**Desafio de extração:** Contém notação científica (`1×10⁻⁶`) e símbolos especiais (`≥`, `μL`) que podem ser mal interpretados por extratores básicos.

---

## Seção 5 — Rodapé / Assinatura Técnica

**Tipo de dado:** Texto simples  
**Aparência no PDF:** Linha de assinatura + dados do laboratório + versão do documento.
**🟡 PRIORIDADE: MÉDIA** — Importante para metadados e rastreabilidade (User Story 5)

**Conteúdo:**

- Nome e CRM do responsável técnico
- Endereço e CNES do laboratório
- Versão do relatório (`3.2.1`) e data de emissão

**Desafio de extração:** O rodapé se repete em todas as páginas — o extrator deve deduplicar e tratar como metadado, não como conteúdo clínico.

---

## Resumo dos Tipos de Dado por Seção

| Seção                | Tipo Principal     | Estrutura            | Complexidade | Prioridade User Stories |
| -------------------- | ------------------ | -------------------- | ------------ | ----------------------- |
| Cabeçalho            | Identificação      | Tabela 4 colunas     | Média        | 🔴 Alta                 |
| Sumário Executivo    | Contagens + texto  | Tabela + parágrafo   | Baixa        | 🔴 Alta                 |
| Resultados Genéticos | Clínico técnico    | Tabela + texto misto | Alta         | 🔴 Máxima               |
| Ancestralidade       | Percentuais        | Tabela 3 colunas     | Baixa        | 🟡 Média                |
| Metodologia          | Técnico-científico | Tabela + parágrafo   | Média        | 🟢 Baixa                |
| Rodapé               | Metadados          | Texto simples        | Baixa        | 🟡 Média                |

---

## Justificativa da Priorização

**🔴 Prioridade Máxima/Alta:**

- **Resultados Genéticos:** Core de todas as User Stories — sem esses dados, nenhuma funcionalidade funciona
- **Cabeçalho:** Identificação essencial para organização e personalização
- **Sumário:** Visão rápida crítica para médicos (US4) e organização geral (US5)

**🟡 Prioridade Média:**

- **Ancestralidade:** Interessante para o usuário mas não impacta decisões de saúde
- **Rodapé:** Importante para rastreabilidade e confiança, mas não é consultado ativamente

**🟢 Prioridade Baixa:**

- **Metodologia:** Relevante apenas para auditoria técnica e controle de qualidade do laboratório
