# Exemplos de Interação — Sistema Genera IA

Estes exemplos simulam perguntas reais de usuários e as respostas esperadas do sistema,
baseadas nos dados estruturados do arquivo `dados_estruturados.json` e alinhadas com as User Stories definidas pelo Product Owner.

---

## Exemplo 1 — User Story 1: Entender relatório em linguagem simples (Paciente)

**Perfil do usuário:** Paciente  
**User Story:** "Como paciente, quero entender meu relatório genético em linguagem simples, para saber o que ele significa na prática."
**Pergunta:**

> "O que significa meu relatório genético? Explique de forma simples."

**Dados consultados no JSON:**

```json
{
  "sumario": {
    "resumo_executivo_paciente": "Foram analisadas 7 condições genéticas. Você tem 2 condições de risco alto que merecem atenção especial, 3 de risco médio para monitoramento e 2 de risco baixo sem preocupação específica."
  }
}
```

**Resposta esperada do sistema:**

> Olá, Carlos! Seu relatório genético analisou **7 condições de saúde** importantes. Vou explicar de forma simples:
>
> **🔴 Atenção especial (2 condições):**
>
> - Diabetes tipo 2 — seu DNA indica maior chance de desenvolver
> - Câncer de mama/ovário — alteração importante no gene BRCA2
>
> **🟡 Monitoramento (3 condições):**
>
> - Pressão alta, Alzheimer e Doença Celíaca — risco moderado
>
> **🟢 Sem preocupação (2 condições):**
>
> - Problemas de coagulação e intolerância à lactose — risco baixo
>
> **O que isso significa na prática:** Você não vai necessariamente ter essas doenças. O DNA apenas indica tendências. Com hábitos saudáveis e acompanhamento médico, você pode prevenir ou controlar a maioria delas.

---

## Exemplo 2 — User Story 2: Fazer perguntas específicas sobre o exame (Paciente)

**Perfil do usuário:** Paciente  
**User Story:** "Como paciente, quero fazer perguntas sobre meu exame, para esclarecer dúvidas específicas sobre meus resultados."
**Pergunta:**

> "Por que meu risco de diabetes é alto? O que isso significa exatamente?"

**Dados consultados no JSON:**

```json
{
  "doenca": "Diabetes Mellitus Tipo 2",
  "risco": "Alto",
  "escore_poligênico_percentil": 89,
  "descricao_simples": "Seu DNA indica uma chance maior de desenvolver diabetes tipo 2...",
  "impacto_pratico": "Na prática, isso significa que você deve evitar açúcares simples..."
}
```

**Resposta esperada do sistema:**

> Seu risco de diabetes é alto porque foram encontradas **variações em dois genes importantes** (TCF7L2 e PPARG) que controlam como seu corpo usa insulina e açúcar.
>
> **O que significa "risco alto":**
>
> - Seu perfil genético está no percentil 89 — ou seja, você tem predisposição maior que 89% da população
> - Isso NÃO significa que você vai ter diabetes, mas que precisa de mais cuidado
>
> **Na prática, você deve:**
>
> - Evitar açúcares simples (refrigerante, doces, pão branco)
> - Fazer exercícios regularmente (pelo menos 150 min/semana)
> - Checar sua glicemia a cada 6 meses
> - Consultar um endocrinologista nos próximos 30 dias
>
> Lembre-se: genética é apenas uma parte da história. Estilo de vida faz uma diferença enorme!

---

## Exemplo 3 — User Story 3: Receber recomendações personalizadas (Paciente)

**Perfil do usuário:** Paciente  
**User Story:** "Como paciente, quero receber recomendações personalizadas, para tomar decisões preventivas com base nos meus dados."
**Pergunta:**

> "Com base no meu relatório, o que devo fazer para cuidar da minha saúde?"

**Dados consultados no JSON:**

```json
{
  "sumario": {
    "recomendacoes_prioritarias": [
      "Consulta com endocrinologista para diabetes",
      "Aconselhamento genético oncológico urgente",
      "Monitoramento cardiovascular anual"
    ]
  }
}
```

**Resposta esperada do sistema:**

> Com base nos seus resultados genéticos, aqui estão suas **recomendações personalizadas por prioridade:**
>
> **🚨 URGENTE (próximos 15-30 dias):**
>
> 1. **Geneticista oncológico** — para discutir o resultado do BRCA2 e estratégias preventivas
> 2. **Endocrinologista** — para plano de prevenção do diabetes
>
> **📅 ACOMPANHAMENTO REGULAR:** 3. **Cardiologista anual** — monitorar pressão arterial 4. **Exames de rotina:** glicemia a cada 6 meses, mamografia anual
>
> **🏃‍♂️ MUDANÇAS NO DIA A DIA:**
>
> - Dieta com baixo açúcar e sal
> - Exercícios aeróbicos 150 min/semana
> - Observar sintomas digestivos (possível celíaca)
> - Produtos lácteos com moderação
>
> **💡 Lembre-se:** Essas recomendações são baseadas no seu perfil genético único. Cada pessoa é diferente — por isso é importante o acompanhamento médico personalizado.

---

## Exemplo 4 — User Story 4: Visualização rápida para médicos

**Perfil do usuário:** Médico  
**User Story:** "Como médico, quero visualizar rapidamente os principais riscos do paciente, para otimizar minha análise."
**Pergunta:**

> "Resumo clínico do paciente Carlos Eduardo Mendes — principais riscos e condutas."

**Dados consultados no JSON:**

```json
{
  "sumario": {
    "principais_riscos_medico": [
      "Diabetes Mellitus Tipo 2 (Alto - percentil 89)",
      "Carcinoma de Mama BRCA2 (Alto - variante patogênica)",
      "Hipertensão Arterial (Médio - percentil 67)"
    ]
  }
}
```

**Resposta esperada do sistema:**

> **RESUMO CLÍNICO — Carlos Eduardo Mendes (GEN-2024-00847)**
>
> **🔴 RISCOS ALTOS — Ação imediata:**
>
> **1. Diabetes Mellitus Tipo 2**
>
> - Genótipo: RS7903146 (TCF7L2) T/T homozigoto + RS12255372 T/G
> - PRS: percentil 89 (risco muito elevado)
> - Conduta: Endocrinologia + HbA1c semestral + metformina profilática a considerar
>
> **2. Carcinoma de Mama — BRCA2**
>
> - Variante: c.5946delT (p.Ser1982Argfs) — Classe 5 Patogênica
> - Risco cumulativo: 45-85% (mama), 10-30% (ovário)
> - Conduta: Genética oncológica URGENTE + mamografia/RNM anual + discussão cirurgia profilática
>
> **🟡 RISCOS MÉDIOS — Monitoramento:**
>
> - Hipertensão (percentil 67): MAPA anual, ACE/ARB se indicado
> - Alzheimer tardio (APOE ε3/ε4): avaliação cognitiva > 50 anos
> - Doença Celíaca (HLA-DQ2.5+): tTG-IgA se sintomas
>
> **🟢 RISCOS BAIXOS:** Trombofilia (wild-type), Lactose (tolerância parcial)
>
> **Prioridade clínica:** BRCA2 > Diabetes > demais condições

---

## Exemplo 5 — User Story 5: Dados organizados para acompanhamento (Usuário geral)

**Perfil do usuário:** Paciente/Médico  
**User Story:** "Como usuário, quero acessar meus dados de forma organizada, para facilitar a interpretação e acompanhamento."
**Pergunta:**

> "Mostre meus dados organizados por categoria de risco."

**Dados consultados no JSON:**

```json
{
  "resultados": [
    {
      "risco": "Alto",
      "doenca": "Diabetes Mellitus Tipo 2",
      "categoria": "Metabolismo"
    },
    {
      "risco": "Alto",
      "doenca": "Carcinoma de Mama",
      "categoria": "Oncologia"
    },
    { "risco": "Médio", "doenca": "Hipertensão", "categoria": "Cardiologia" }
  ]
}
```

**Resposta esperada do sistema:**

> **SEUS DADOS ORGANIZADOS POR CATEGORIA DE RISCO:**
>
> ## 🔴 RISCO ALTO (2 condições)
>
> | Condição           | Categoria   | Percentil/Marcador | Próxima Ação             |
> | ------------------ | ----------- | ------------------ | ------------------------ |
> | Diabetes Tipo 2    | Metabolismo | Percentil 89       | Endocrinologista 30 dias |
> | Câncer Mama/Ovário | Oncologia   | BRCA2 patogênico   | Geneticista 15 dias      |
>
> ## 🟡 RISCO MÉDIO (3 condições)
>
> | Condição         | Categoria         | Percentil/Marcador | Próxima Ação         |
> | ---------------- | ----------------- | ------------------ | -------------------- |
> | Hipertensão      | Cardiologia       | Percentil 67       | Cardiologista anual  |
> | Alzheimer tardio | Neurologia        | APOE ε3/ε4         | Neurologia > 50 anos |
> | Doença Celíaca   | Gastroenterologia | HLA-DQ2.5+         | Observar sintomas    |
>
> ## 🟢 RISCO BAIXO (2 condições)
>
> | Condição             | Categoria   | Resultado          | Status              |
> | -------------------- | ----------- | ------------------ | ------------------- |
> | Trombofilia          | Hematologia | Wild-type          | Sem restrições      |
> | Intolerância Lactose | Nutrição    | Tolerância parcial | Consumo moderado OK |
>
> **📊 Resumo:** 7 condições analisadas • 2 alta prioridade • 3 monitoramento • 2 sem preocupação
>
> **📅 Próximos exames:** Glicemia (6 meses), Mamografia (anual), Pressão arterial (anual)

---

## Exemplo 6 — Pergunta fora do escopo (Guard rail ativo)

**Perfil do usuário:** Paciente  
**Pergunta:**

> "Qual remédio devo tomar para prevenir o diabetes?"

**Resposta esperada do sistema:**

> Essa é uma pergunta importante, mas que está **fora do meu escopo**. Não tenho autorização para recomendar medicamentos — isso é responsabilidade exclusiva de um profissional de saúde habilitado.
>
> **O que posso fazer:**
>
> - Explicar seus resultados genéticos
> - Sugerir hábitos preventivos (alimentação, exercícios)
> - Orientar sobre quando procurar ajuda médica
>
> **Para medicamentos:** Por favor, consulte o endocrinologista que recomendei. Ele poderá avaliar se medicamentos como metformina são indicados no seu caso específico.
>
> Posso ajudar com outras dúvidas sobre seus resultados genéticos?

---

## Mapeamento User Stories → Exemplos

| User Story                         | Exemplo   | Perfil        | Foco                           |
| ---------------------------------- | --------- | ------------- | ------------------------------ |
| US1: Entender em linguagem simples | Exemplo 1 | Paciente      | Explicação geral acessível     |
| US2: Fazer perguntas específicas   | Exemplo 2 | Paciente      | Esclarecimento de dúvidas      |
| US3: Recomendações personalizadas  | Exemplo 3 | Paciente      | Ações preventivas              |
| US4: Visualização rápida (médico)  | Exemplo 4 | Médico        | Resumo clínico técnico         |
| US5: Dados organizados             | Exemplo 5 | Usuário geral | Estruturação e acompanhamento  |
| Guard Rail                         | Exemplo 6 | Paciente      | Segurança e limites do sistema |
