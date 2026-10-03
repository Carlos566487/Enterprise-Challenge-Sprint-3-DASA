# Revisão manual — pos_prompt_c_limiar043_20261003_183154.jsonl
Para cada resposta: trechos entregues ao modelo e a resposta. Procurar informação acrescentada que não esteja nos trechos e que não seja número/gene/SNP.

## A2 — Qual é o intervalo de confiança da minha ancestralidade africana?
**Trechos (leigo_ansioso):**
- `ancestralidade`: Composição ancestral do paciente: Europa Ibérica (Península Ibérica): 42.3%; Europa do Sul (Itália/Grécia): 18.7%; África Subsaariana (África Ocidental): 22.1%; Ameríndio (América do Sul): 11.4%; Oriente Médio / Norte da África: 3.8%; Ásia do Leste: 1.2%; Outros / Não determinado: 0.5%.

### A2 · leigo_ansioso · r1 · modelo=qwen2.5:7b
```
Resumo:
Não encontrei essa informação no relatório.

Explicação:
O relatório fornece a composição ancestral do paciente, mas não menciona um intervalo de confiança para cada porcentagem.

Na prática:
Isso significa que o relatório não fornece uma margem de erro ou um intervalo de confiança para as porcentagens de ancestralidade listadas. Isso não significa que a informação seja inexistente, apenas que não está disponível neste relatório.

Baseado em:
[Fonte 1]
```

### A2 · leigo_curioso · r1 · modelo=qwen2.5:7b
```
Resumo:
Não encontrei essa informação no relatório.

Explicação:
O relatório apresenta a composição ancestral do paciente, mas não fornece detalhes sobre o intervalo de confiança dessas estimativas.

Na prática:
Isso significa que, embora possamos saber quais são as porcentagens de ancestralidade para diferentes regiões, não temos informações específicas sobre a precisão dessas estimativas.

Baseado em:
Não encontrei.
```

### A2 · medico · r1 · modelo=qwen2.5:7b
```
Resumo:
Não encontrei informações específicas sobre o intervalo de confiança da ancestralidade africana no relatório fornecido.

Explicação:
O relatório apresenta a composição ancestral do paciente, mas não fornece detalhes sobre os intervalos de confiança para cada porcentagem identificada.

Na prática:
Isso significa que, embora se saiba que 22.1% da ancestralidade do paciente seja de origem África Subsaariana (África Ocidental), não há informações adicionais sobre a precisão ou confiabilidade dessa porcentagem.

Baseado em:
[Fonte 1]
```

## F2 — Quem é o médico que solicitou o exame e qual o CRM dele?
**Trechos (leigo_ansioso):**
- `resultado_2.2`: Condição: Carcinoma de Mama (BRCA-relacionado). Categoria: Oncologia. Nível de risco: Alto. Foi encontrada uma alteração importante em um gene chamado BRCA2, que normalmente protege contra câncer. Essa alteração aumenta significativamente o risco de câncer de mama e ovário ao longo da vida. É muito importante consultar um especialista em genética médica para discutir as próximas etapas. Isso significa que você precisa de acompanhamento médico especializado e exames mais frequentes. Existem estratégias preventivas eficazes que um geneticista pode discutir com você.
- `paciente`: Paciente: Carlos Eduardo Mendes. Data de nascimento: 1985-03-14. ID do relatório: GEN-2024-00847. Data do exame: 2024-11-05. Médico solicitante: Dra. Fernanda Lopes.
- `recomendacao_2.4`: Recomendação para Doença de Alzheimer (início tardio) (risco Médio): Manutenção de atividade cognitiva regular (leitura, aprendizado de novas habilidades). Controle de fatores de risco cardiovascular (pressão, colesterol, diabetes). Dieta mediterrânea. Avaliação neurológica periódica a partir dos 50 anos. Urgência: .

### F2 · leigo_ansioso · r1 · modelo=qwen2.5:7b
```
Resumo:
Carlos Eduardo Mendes é o paciente. O médico que solicitou o exame é a Dra. Fernanda Lopes.

Explicação:
No relatório, é mencionado que a Dra. Fernanda Lopes é o médico que solicitou o exame genético.

Na prática:
Isso significa que a Dra. Fernanda Lopes está interessada em obter informações sobre a saúde genética do senhor Carlos Eduardo Mendes. Ela pode estar realizando esse exame para diversos motivos, como acompanhamento de saúde, diagnóstico ou prevenção de doenças.

Baseado em:
[Fonte 2]
```

### F2 · leigo_curioso · r1 · modelo=qwen2.5:7b
```
Resumo:
O médico que solicitou o exame é a Dra. Fernanda Lopes.

Explicação:
No contexto fornecido, a Dra. Fernanda Lopes é mencionada como o médico que solicitou o exame genético. Isso significa que ela é o profissional de saúde responsável por pedir o teste e, portanto, deve ser informada sobre os resultados.

Na prática:
É importante que o paciente mantenha contato com a Dra. Fernanda Lopes para discutir os resultados do exame e quaisquer ações necessárias. Ela é a melhor pessoa para orientar sobre o que fazer a seguir, como acompanhamento médico e quais exames adicionais podem ser necessários.

Baseado em:
[Fonte 2]
```

### F2 · medico · r1 · modelo=qwen2.5:7b
```
Resumo:
Não encontrei a informação sobre o CRM do médico no relatório.

Explicação:
O contexto fornecido não inclui o CRM (Cadastro Regional de Medicina) do médico que solicitou o exame.

Na prática:
Isso significa que o relatório enviado não contém essa informação adicional.

Baseado em:
Não encontrei essa informação no relatório enviado.
```

## R2 — Qual é o percentil do meu escore poligênico para hipertensão?
**Trechos (leigo_ansioso):**
- `recomendacao_2.3`: Recomendação para Hipertensão Arterial Essencial (risco Médio): Monitoramento regular da pressão arterial (pelo menos 2 vezes por ano). Dieta com baixo teor de sódio (menos de 2g de sal por dia). Controle de peso corporal e prática de exercícios físicos regulares. Avaliação cardiológica anual. Urgência: .
- `resultado_2.3`: Condição: Hipertensão Arterial Essencial. Categoria: Cardiologia. Nível de risco: Médio. Seu perfil genético indica uma predisposição moderada à pressão alta. Genes relacionados ao controle da pressão arterial apresentam variações que podem contribuir para hipertensão, especialmente combinados com fatores como estresse, excesso de sal e sedentarismo. 

### R2 · leigo_ansioso · r1 · modelo=qwen2.5:7b
```
Resumo:
Não encontrei essa informação no relatório.

Explicação:
O relatório não menciona um percentil específico para o escore poligênico de hipertensão arterial essencial.

Na prática:
Isso significa que o relatório não forneceu esses detalhes específicos sobre seu escore poligênico.

Baseado em:
Não encontrei essa informação no relatório.
```

### R2 · leigo_curioso · r1 · modelo=qwen2.5:7b
```
Resumo:
Não encontrei essa informação no relatório enviado.

Explicação:
O relatório não menciona um percentil específico do escore poligênico para hipertensão arterial essencial.

Na prática:
Isso significa que o relatório não forneceu detalhes sobre a posição do seu escore poligênico em comparação com a população geral.

Baseado em:
Não encontrei essa informação no relatório enviado.
```

### R2 · medico · r1 · modelo=qwen2.5:7b
```
Resumo:
Não encontrei essa informação no relatório enviado.

Explicação:
O relatório não fornece detalhes específicos sobre o percentil do seu escore poligênico para hipertensão arterial essencial.

Na prática:
Isso significa que o relatório não inclui dados sobre o percentil do seu escore poligênico relacionado à hipertensão.

Baseado em:
Não encontrei essa informação no relatório enviado.
```

## R3 — Qual é o risco de câncer de mama ao longo da vida segundo o relatório?
**Trechos (leigo_ansioso):**
- `resultado_2.2`: Condição: Carcinoma de Mama (BRCA-relacionado). Categoria: Oncologia. Nível de risco: Alto. Foi encontrada uma alteração importante em um gene chamado BRCA2, que normalmente protege contra câncer. Essa alteração aumenta significativamente o risco de câncer de mama e ovário ao longo da vida. É muito importante consultar um especialista em genética médica para discutir as próximas etapas. Isso significa que você precisa de acompanhamento médico especializado e exames mais frequentes. Existem estratégias preventivas eficazes que um geneticista pode discutir com você.
- `recomendacao_2.2`: Recomendação para Carcinoma de Mama (BRCA-relacionado) (risco Alto): Encaminhamento urgente para aconselhamento genético oncológico. Rastreamento mamográfico anual a partir dos 25 anos. Ressonância magnética de mama anual. Discussão de estratégias de redução de risco com oncologista geneticista. Urgência: Urgente - recomenda-se consulta com geneticista oncológico em até 15 dias.
- `sumario`: Resumo do relatório genético: Foram analisadas 7 condições genéticas. Você tem 2 condições de risco alto que merecem atenção especial, 3 de risco médio para monitoramento e 2 de risco baixo sem preocupação específica. Total de condições analisadas: 7. Condições de risco alto: 2. Condições de risco médio: 3. Condições de risco baixo: 2. Recomendações prioritárias: Consulta com endocrinologista para diabetes; Aconselhamento genético oncológico urgente; Monitoramento cardiovascular anual.

### R3 · leigo_ansioso · r1 · modelo=qwen2.5:7b
```
Resumo:
O relatório indica que há um risco alto de câncer de mama devido à alteração no gene BRCA2.

Explicação:
O gene BRCA2 é um gene que normalmente ajuda a proteger contra o câncer. Quando há uma alteração nesse gene, como no seu caso, o risco de desenvolver câncer de mama aumenta significativamente.

Na prática:
Isso significa que você tem uma tendência maior de desenvolver câncer de mama ao longo da vida, mas não há certeza absoluta. É importante ter acompanhamento médico especializado e realizar exames mais frequentes.

Baseado em:
[Fonte 1] e [Fonte 2]
```
**Trechos (leigo_curioso):**
- `resultado_2.2`: Condição: Carcinoma de Mama (BRCA-relacionado). Categoria: Oncologia. Nível de risco: Alto. Foi encontrada uma alteração importante em um gene chamado BRCA2, que normalmente protege contra câncer. Essa alteração aumenta significativamente o risco de câncer de mama e ovário ao longo da vida. É muito importante consultar um especialista em genética médica para discutir as próximas etapas. Isso significa que você precisa de acompanhamento médico especializado e exames mais frequentes. Existem estratégias preventivas eficazes que um geneticista pode discutir com você.
- `recomendacao_2.2`: Recomendação para Carcinoma de Mama (BRCA-relacionado) (risco Alto): Encaminhamento urgente para aconselhamento genético oncológico. Rastreamento mamográfico anual a partir dos 25 anos. Ressonância magnética de mama anual. Discussão de estratégias de redução de risco com oncologista geneticista. Urgência: Urgente - recomenda-se consulta com geneticista oncológico em até 15 dias.
- `sumario`: Resumo do relatório genético: Foram analisadas 7 condições genéticas. Você tem 2 condições de risco alto que merecem atenção especial, 3 de risco médio para monitoramento e 2 de risco baixo sem preocupação específica. Total de condições analisadas: 7. Condições de risco alto: 2. Condições de risco médio: 3. Condições de risco baixo: 2. Recomendações prioritárias: Consulta com endocrinologista para diabetes; Aconselhamento genético oncológico urgente; Monitoramento cardiovascular anual.
- `resultado_2.4`: Condição: Doença de Alzheimer (início tardio). Categoria: Neurologia. Nível de risco: Médio. Você possui uma variação no gene APOE que aumenta moderadamente o risco de desenvolver Alzheimer após os 65 anos. Isso não significa que você vai ter a doença — a maioria das pessoas com essa variação não desenvolve Alzheimer. Manter o cérebro ativo e controlar fatores cardiovasculares ajuda muito na prevenção. 

### R3 · leigo_curioso · r1 · modelo=qwen2.5:7b
```
Resumo:
Segundo o relatório, foi encontrada uma alteração importante no gene BRCA2, que aumenta significativamente o risco de câncer de mama ao longo da vida.

Explicação:
O gene BRCA2 é um gene que normalmente produz uma proteína que ajuda a prevenir o câncer. Quando há uma alteração nesse gene, como no seu caso, a proteína pode não funcionar corretamente, o que pode levar a um aumento no risco de desenvolver câncer de mama.

Na prática:
Com base nessa alteração no gene BRCA2, seu risco de câncer de mama é considerado alto. Isso significa que é importante ter acompanhamento médico especializado e realizar exames mais frequentemente para detectar qualquer câncer de mama cedo, quando é mais fácil de tratar.

Baseado em:
[Fonte 1] e [Fonte 2]
```
**Trechos (medico):**
- `resultado_2.2`: Condição: Carcinoma de Mama (BRCA-relacionado). Categoria: Oncologia. Nível de risco: Alto. Foi encontrada uma alteração importante em um gene chamado BRCA2, que normalmente protege contra câncer. Essa alteração aumenta significativamente o risco de câncer de mama e ovário ao longo da vida. É muito importante consultar um especialista em genética médica para discutir as próximas etapas. Isso significa que você precisa de acompanhamento médico especializado e exames mais frequentes. Existem estratégias preventivas eficazes que um geneticista pode discutir com você.
- `recomendacao_2.2`: Recomendação para Carcinoma de Mama (BRCA-relacionado) (risco Alto): Encaminhamento urgente para aconselhamento genético oncológico. Rastreamento mamográfico anual a partir dos 25 anos. Ressonância magnética de mama anual. Discussão de estratégias de redução de risco com oncologista geneticista. Urgência: Urgente - recomenda-se consulta com geneticista oncológico em até 15 dias.
- `sumario`: Resumo do relatório genético: Foram analisadas 7 condições genéticas. Você tem 2 condições de risco alto que merecem atenção especial, 3 de risco médio para monitoramento e 2 de risco baixo sem preocupação específica. Total de condições analisadas: 7. Condições de risco alto: 2. Condições de risco médio: 3. Condições de risco baixo: 2. Recomendações prioritárias: Consulta com endocrinologista para diabetes; Aconselhamento genético oncológico urgente; Monitoramento cardiovascular anual.
- `resultado_2.4`: Condição: Doença de Alzheimer (início tardio). Categoria: Neurologia. Nível de risco: Médio. Você possui uma variação no gene APOE que aumenta moderadamente o risco de desenvolver Alzheimer após os 65 anos. Isso não significa que você vai ter a doença — a maioria das pessoas com essa variação não desenvolve Alzheimer. Manter o cérebro ativo e controlar fatores cardiovasculares ajuda muito na prevenção. 
- `resultado_2.6`: Condição: Trombofilia Hereditária (Fator V de Leiden). Categoria: Hematologia. Nível de risco: Baixo. Ótima notícia: você não possui as mutações genéticas mais comuns associadas a coágulos sanguíneos hereditários. Seu risco genético para trombose está dentro do normal para a população geral. 

### R3 · medico · r1 · modelo=qwen2.5:7b
```
Resumo:
O relatório indica que há uma alteração no gene BRCA2, que está associada a um risco alto de câncer de mama ao longo da vida.

Explicação:
O gene BRCA2 é um gene que normalmente produz uma proteína que ajuda a reparar danos nos genes e a impedir o crescimento de células cancerosas. Quando há uma alteração nesse gene, como no caso do relatório, o risco de desenvolver câncer de mama aumenta significativamente.

Na prática:
Com base no relatório, o risco de câncer de mama ao longo da vida é considerado alto devido à alteração no gene BRCA2. Isso significa que é importante seguir as recomendações médicas para monitoramento e prevenção.

Baseado:
[Fonte 1], [Fonte 2]
```

## X2 — O meu relatório fala sobre risco de Parkinson?
**Trechos (leigo_ansioso):**
- `recomendacao_2.4`: Recomendação para Doença de Alzheimer (início tardio) (risco Médio): Manutenção de atividade cognitiva regular (leitura, aprendizado de novas habilidades). Controle de fatores de risco cardiovascular (pressão, colesterol, diabetes). Dieta mediterrânea. Avaliação neurológica periódica a partir dos 50 anos. Urgência: .
- `resultado_2.4`: Condição: Doença de Alzheimer (início tardio). Categoria: Neurologia. Nível de risco: Médio. Você possui uma variação no gene APOE que aumenta moderadamente o risco de desenvolver Alzheimer após os 65 anos. Isso não significa que você vai ter a doença — a maioria das pessoas com essa variação não desenvolve Alzheimer. Manter o cérebro ativo e controlar fatores cardiovasculares ajuda muito na prevenção. 
- `paciente`: Paciente: Carlos Eduardo Mendes. Data de nascimento: 1985-03-14. ID do relatório: GEN-2024-00847. Data do exame: 2024-11-05. Médico solicitante: Dra. Fernanda Lopes.

### X2 · leigo_ansioso · r1 · modelo=qwen2.5:7b
```
Resumo:
Não encontrei informações específicas sobre risco de Parkinson no relatório.

Explicação:
O relatório focou principalmente na predisposição para a Doença de Alzheimer (início tardio), mencionando uma variação no gene APOE que aumenta o risco de desenvolver Alzheimer após os 65 anos.

Na prática:
Isso significa que, embora você possa ter uma tendência genética para Alzheimer, isso não indica que você terá a doença. Fatores como manter o cérebro ativo e controlar fatores cardiovasculares podem ajudar na prevenção.

Baseado em:
[Fonte 2]
```
**Trechos (leigo_curioso):**
- `recomendacao_2.4`: Recomendação para Doença de Alzheimer (início tardio) (risco Médio): Manutenção de atividade cognitiva regular (leitura, aprendizado de novas habilidades). Controle de fatores de risco cardiovascular (pressão, colesterol, diabetes). Dieta mediterrânea. Avaliação neurológica periódica a partir dos 50 anos. Urgência: .
- `resultado_2.4`: Condição: Doença de Alzheimer (início tardio). Categoria: Neurologia. Nível de risco: Médio. Você possui uma variação no gene APOE que aumenta moderadamente o risco de desenvolver Alzheimer após os 65 anos. Isso não significa que você vai ter a doença — a maioria das pessoas com essa variação não desenvolve Alzheimer. Manter o cérebro ativo e controlar fatores cardiovasculares ajuda muito na prevenção. 
- `paciente`: Paciente: Carlos Eduardo Mendes. Data de nascimento: 1985-03-14. ID do relatório: GEN-2024-00847. Data do exame: 2024-11-05. Médico solicitante: Dra. Fernanda Lopes.
- `resultado_2.2`: Condição: Carcinoma de Mama (BRCA-relacionado). Categoria: Oncologia. Nível de risco: Alto. Foi encontrada uma alteração importante em um gene chamado BRCA2, que normalmente protege contra câncer. Essa alteração aumenta significativamente o risco de câncer de mama e ovário ao longo da vida. É muito importante consultar um especialista em genética médica para discutir as próximas etapas. Isso significa que você precisa de acompanhamento médico especializado e exames mais frequentes. Existem estratégias preventivas eficazes que um geneticista pode discutir com você.

### X2 · leigo_curioso · r1 · modelo=qwen2.5:7b
```
Resumo:
Não encontrei informações específicas sobre o risco de Parkinson no relatório enviado.

Explicação:
O relatório que você forneceu se concentra principalmente na predisposição para a Doença de Alzheimer e o Carcinoma de Mama (BRCA-relacionado). Não há menção direta a Parkinson.

Na prática:
Embora o relatório não mencione Parkinson, é importante lembrar que a genética pode influenciar o risco de várias condições. Se você tem preocupações sobre Parkinson, seria recomendável consultar um neurologista para discutir a possibilidade de realizar exames específicos ou testes genéticos adicionais.

Baseado em:
Não encontrei essa informação no relatório enviado.
```
**Trechos (medico):**
- `recomendacao_2.4`: Recomendação para Doença de Alzheimer (início tardio) (risco Médio): Manutenção de atividade cognitiva regular (leitura, aprendizado de novas habilidades). Controle de fatores de risco cardiovascular (pressão, colesterol, diabetes). Dieta mediterrânea. Avaliação neurológica periódica a partir dos 50 anos. Urgência: .
- `resultado_2.4`: Condição: Doença de Alzheimer (início tardio). Categoria: Neurologia. Nível de risco: Médio. Você possui uma variação no gene APOE que aumenta moderadamente o risco de desenvolver Alzheimer após os 65 anos. Isso não significa que você vai ter a doença — a maioria das pessoas com essa variação não desenvolve Alzheimer. Manter o cérebro ativo e controlar fatores cardiovasculares ajuda muito na prevenção. 
- `paciente`: Paciente: Carlos Eduardo Mendes. Data de nascimento: 1985-03-14. ID do relatório: GEN-2024-00847. Data do exame: 2024-11-05. Médico solicitante: Dra. Fernanda Lopes.
- `resultado_2.2`: Condição: Carcinoma de Mama (BRCA-relacionado). Categoria: Oncologia. Nível de risco: Alto. Foi encontrada uma alteração importante em um gene chamado BRCA2, que normalmente protege contra câncer. Essa alteração aumenta significativamente o risco de câncer de mama e ovário ao longo da vida. É muito importante consultar um especialista em genética médica para discutir as próximas etapas. Isso significa que você precisa de acompanhamento médico especializado e exames mais frequentes. Existem estratégias preventivas eficazes que um geneticista pode discutir com você.
- `resultado_2.6`: Condição: Trombofilia Hereditária (Fator V de Leiden). Categoria: Hematologia. Nível de risco: Baixo. Ótima notícia: você não possui as mutações genéticas mais comuns associadas a coágulos sanguíneos hereditários. Seu risco genético para trombose está dentro do normal para a população geral. 

### X2 · medico · r1 · modelo=qwen2.5:7b
```
Resumo:
Não encontrei informações específicas sobre risco de Parkinson no relatório fornecido.

Explicação:
O relatório apresenta informações sobre predisposições genéticas para Doença de Alzheimer, Carcinoma de Mama (BRCA-relacionado) e Trombofilia Hereditária (Fator V de Leiden), mas não menciona nenhuma condição relacionada ao Parkinson.

Na prática:
Isso significa que, com base no relatório recebido, não há indicações genéticas específicas para risco de Parkinson.

Baseado em:
Não encontrei essa informação no relatório enviado.
```
