# Revisão manual — pos_prompt_a_limiar043_20261003_183841.jsonl
Para cada resposta: trechos entregues ao modelo e a resposta. Procurar informação acrescentada que não esteja nos trechos e que não seja número/gene/SNP.

## F3 — Quantas condições foram analisadas e quantas são de risco alto?
**Trechos (leigo_ansioso):**
- `resultado_2.7`: Condição: Intolerância à Lactose (tipo adulto). Categoria: Nutrigenômica. Nível de risco: Baixo. Você tem uma tolerância parcial à lactose (o açúcar do leite). Isso significa que provavelmente consegue consumir leite e derivados em quantidades moderadas sem grandes problemas. Produtos fermentados como iogurte e queijos curados costumam ser ainda melhor tolerados. 
- `resultado_2.2`: Condição: Carcinoma de Mama (BRCA-relacionado). Categoria: Oncologia. Nível de risco: Alto. Foi encontrada uma alteração importante em um gene chamado BRCA2, que normalmente protege contra câncer. Essa alteração aumenta significativamente o risco de câncer de mama e ovário ao longo da vida. É muito importante consultar um especialista em genética médica para discutir as próximas etapas. Isso significa que você precisa de acompanhamento médico especializado e exames mais frequentes. Existem estratégias preventivas eficazes que um geneticista pode discutir com você.
- `resultado_2.6`: Condição: Trombofilia Hereditária (Fator V de Leiden). Categoria: Hematologia. Nível de risco: Baixo. Ótima notícia: você não possui as mutações genéticas mais comuns associadas a coágulos sanguíneos hereditários. Seu risco genético para trombose está dentro do normal para a população geral. 

### F3 · leigo_ansioso · r1 · modelo=qwen2.5:7b
```
Resumo:
No relatório, foram analisadas três condições: Intolerância à Lactose, Carcinoma de Mama (BRCA-relacionado) e Trombofilia Hereditária (Fator V de Leiden). Das três, uma é de risco alto (Carcinoma de Mama) e duas são de risco baixo (Intolerância à Lactose e Trombofilia Hereditária).

Explicação:
O relatório examinou três condições genéticas diferentes. Cada uma delas tem um nível de risco associado, que pode variar de baixo a alto.

Na prática:
Isso significa que das três condições analisadas, uma tem um risco significativo (Carcinoma de Mama), enquanto as outras duas têm riscos considerados normais ou menores.

Baseado:
[Fonte 1], [Fonte 2], [Fonte 3]
```

### F3 · leigo_ansioso · r2 · modelo=qwen2.5:7b
```
Resumo:
No relatório, foram analisadas três condições: Intolerância à Lactose, Carcinoma de Mama (BRCA-relacionado) e Trombofilia Hereditária (Fator V de Leiden). Das três, uma é de risco alto.

Explicação:
O relatório analisou três condições genéticas diferentes, cada uma com um nível de risco diferente. O risco alto está associado à condição de Carcinoma de Mama (BRCA-relacionado).

Na prática:
Isso significa que das três condições analisadas, apenas uma (Carcinoma de Mama) tem um risco considerado alto. As outras duas (Intolerância à Lactose e Trombofilia Hereditária) têm riscos baixos.

Baseado em:
[Fonte 1], [Fonte 2], [Fonte 3]
```
**Trechos (leigo_curioso):**
- `resultado_2.7`: Condição: Intolerância à Lactose (tipo adulto). Categoria: Nutrigenômica. Nível de risco: Baixo. Você tem uma tolerância parcial à lactose (o açúcar do leite). Isso significa que provavelmente consegue consumir leite e derivados em quantidades moderadas sem grandes problemas. Produtos fermentados como iogurte e queijos curados costumam ser ainda melhor tolerados. 
- `resultado_2.2`: Condição: Carcinoma de Mama (BRCA-relacionado). Categoria: Oncologia. Nível de risco: Alto. Foi encontrada uma alteração importante em um gene chamado BRCA2, que normalmente protege contra câncer. Essa alteração aumenta significativamente o risco de câncer de mama e ovário ao longo da vida. É muito importante consultar um especialista em genética médica para discutir as próximas etapas. Isso significa que você precisa de acompanhamento médico especializado e exames mais frequentes. Existem estratégias preventivas eficazes que um geneticista pode discutir com você.
- `resultado_2.6`: Condição: Trombofilia Hereditária (Fator V de Leiden). Categoria: Hematologia. Nível de risco: Baixo. Ótima notícia: você não possui as mutações genéticas mais comuns associadas a coágulos sanguíneos hereditários. Seu risco genético para trombose está dentro do normal para a população geral. 
- `recomendacao_2.3`: Recomendação para Hipertensão Arterial Essencial (risco Médio): Monitoramento regular da pressão arterial (pelo menos 2 vezes por ano). Dieta com baixo teor de sódio (menos de 2g de sal por dia). Controle de peso corporal e prática de exercícios físicos regulares. Avaliação cardiológica anual. Urgência: .

### F3 · leigo_curioso · r1 · modelo=qwen2.5:7b
```
Resumo:
No relatório, foram analisadas quatro condições: Intolerância à Lactose, Carcinoma de Mama (BRCA-relacionado), Trombofilia Hereditária (Fator V de Leiden) e Hipertensão Arterial Essencial. Entre essas condições, uma é de risco alto: Carcinoma de Mama (BRCA-relacionado).

Explicação:
O relatório analisou quatro condições diferentes, cada uma com um nível de risco diferente. O Carcinoma de Mama (BRCA-relacionado) é a única condição que foi classificada como de risco alto.

Na prática:
Isso significa que o risco de desenvolver câncer de mama é significativamente maior devido à alteração encontrada no gene BRCA2. No entanto, é importante lembrar que o risco genético não determina com certeza se uma pessoa desenvolverá a doença, mas sim aumenta a probabilidade.

Baseado em:
[Fonte 2]
```

### F3 · leigo_curioso · r2 · modelo=qwen2.5:7b
```
Resumo:
No relatório, foram analisadas quatro condições: Intolerância à Lactose, Carcinoma de Mama (BRCA-relacionado), Trombofilia Hereditária (Fator V de Leiden) e Hipertensão Arterial Essencial. Das quatro condições, uma é de risco alto: Carcinoma de Mama (BRCA-relacionado).

Explicação:
O relatório examinou quatro condições diferentes, cada uma com seu próprio nível de risco. O Carcinoma de Mama (BRCA-relacionado) é a única condição classificada como de risco alto.

Na prática:
Isso significa que, entre as condições analisadas, há um risco significativo associado ao Carcinoma de Mama. O risco alto é devido a uma alteração importante no gene BRCA2, que normalmente protege contra o desenvolvimento de câncer. A presença dessa alteração aumenta o risco de câncer de mama e ovário ao longo da vida.

Baseado em:
[Fonte 2]
```

### F3 · medico · r1 · modelo=qwen2.5:7b
```
Resumo:
No relatório, foram analisadas quatro condições, sendo uma de risco alto (Carcinoma de Mama (BRCA-relacionado)) e três com risco baixo (Intolerância à Lactose, Trombofilia Hereditária (Fator V de Leiden) e Hipertensão Arterial Essencial).

Explicação:
O relatório analisou quatro condições genéticas diferentes, classificando-as em riscos baixo e alto. Um risco alto indica uma probabilidade significativamente maior de desenvolver a condição em questão, enquanto um risco baixo sugere que a probabilidade é dentro do normal para a população geral.

Na prática:
Isso significa que uma condição (Carcinoma de Mama (BRCA-relacionado)) foi identificada com um risco alto, o que requer acompanhamento médico especializado. As outras três condições (Intolerância à Lactose, Trombofilia Hereditária (Fator V de Leiden) e Hipertensão Arterial Essencial) foram classificadas com riscos baixos, indicando que não há mutações genéticas preocupantes nessas áreas.

Baseado em:
[Fonte 1], [Fonte 2], [Fonte 3], [Fonte 4]
```

### F3 · medico · r2 · modelo=qwen2.5:7b
```
Resumo:
No relatório, foram analisadas quatro condições: Intolerância à Lactose, Carcinoma de Mama (BRCA-relacionado), Trombofilia Hereditária (Fator V de Leiden) e Hipertensão Arterial Essencial. Das quatro condições analisadas, uma é de risco alto: Carcinoma de Mama (BRCA-relacionado).

Explicação:
O relatório analisou quatro condições genéticas diferentes, cada uma com seu próprio nível de risco. O Carcinoma de Mama relacionado ao gene BRCA2 foi identificado como tendo um risco alto. As outras três condições analisadas não apresentaram riscos altos.

Na prática:
Isso significa que, dentre as condições analisadas, apenas o risco de desenvolver câncer de mama relacionado ao gene BRCA2 é considerado alto. As outras condições apresentam riscos baixos ou não foram identificadas como de alto risco no relatório.

Baseado em:
[Fonte 2]
```

## R4 — Quais condições do meu relatório têm risco baixo?
**Trechos (leigo_ansioso):**
- `resultado_2.6`: Condição: Trombofilia Hereditária (Fator V de Leiden). Categoria: Hematologia. Nível de risco: Baixo. Ótima notícia: você não possui as mutações genéticas mais comuns associadas a coágulos sanguíneos hereditários. Seu risco genético para trombose está dentro do normal para a população geral. 
- `sumario`: Resumo do relatório genético: Foram analisadas 7 condições genéticas. Você tem 2 condições de risco alto que merecem atenção especial, 3 de risco médio para monitoramento e 2 de risco baixo sem preocupação específica. Total de condições analisadas: 7. Condições de risco alto: 2. Condições de risco médio: 3. Condições de risco baixo: 2. Recomendações prioritárias: Consulta com endocrinologista para diabetes; Aconselhamento genético oncológico urgente; Monitoramento cardiovascular anual.
- `resultado_2.7`: Condição: Intolerância à Lactose (tipo adulto). Categoria: Nutrigenômica. Nível de risco: Baixo. Você tem uma tolerância parcial à lactose (o açúcar do leite). Isso significa que provavelmente consegue consumir leite e derivados em quantidades moderadas sem grandes problemas. Produtos fermentados como iogurte e queijos curados costumam ser ainda melhor tolerados. 

### R4 · leigo_ansioso · r1 · modelo=qwen2.5:7b
```
Resumo:
As condições com risco baixo no seu relatório são Trombofilia Hereditária (Fator V de Leiden) e Intolerância à Lactose (tipo adulto).

Explicação:
O relatório menciona duas condições com risco baixo. A Trombofilia Hereditária (Fator V de Leiden) indica que você não possui as mutações genéticas mais comuns associadas a coágulos sanguíneos hereditários. Isso significa que seu risco genético para trombose está dentro do normal para a população geral. A Intolerância à Lactose (tipo adulto) indica que você tem uma tolerância parcial ao açúcar do leite, o que significa que provavelmente consegue consumir leite e derivados em quantidades moderadas sem grandes problemas.

Na prática:
Essas condições com risco baixo não representam uma ameaça imediata à sua saúde, mas podem indicar uma tendência genética. É importante manter uma vida saudável e seguir as recomendações médicas, mesmo que o risco seja baixo.

Baseado em:
[Fonte 1], [Fonte 3]
```

### R4 · leigo_ansioso · r2 · modelo=qwen2.5:7b
```
Resumo:
As condições com risco baixo no seu relatório são Trombofilia Hereditária (Fator V de Leiden) e Intolerância à Lactose (tipo adulto).

Explicação:
O relatório menciona duas condições com risco baixo: Trombofilia Hereditária (Fator V de Leiden) e Intolerância à Lactose (tipo adulto). Isso significa que, embora você possua variantes genéticas associadas a essas condições, seu risco genético para desenvolver problemas relacionados a elas está dentro do normal para a população geral.

Na prática:
Essa informação é boa noticia, pois indica que você não precisa se preocupar excessivamente com essas condições. No entanto, é sempre bom manter uma vida saudável e seguir orientações médicas para prevenir qualquer problema.

Baseado em:
[Fonte 1] e [Fonte 3]
```

### R4 · leigo_curioso · r1 · modelo=qwen2.5:7b
```
Resumo:
No seu relatório, duas condições têm risco baixo: Trombofilia Hereditária (Fator V de Leiden) e Intolerância à Lactose (tipo adulto).

Explicação:
As condições com risco baixo são aquelas que têm uma probabilidade menor de causar problemas de saúde significativos. No seu caso, a Trombofilia Hereditária (Fator V de Leiden) e a Intolerância à Lactose (tipo adulto) estão nessa categoria.

Na prática:
Isso significa que, embora exista uma pequena chance de desenvolver problemas relacionados a essas condições, a probabilidade é baixa. Portanto, você não precisa se preocupar com essas condições de forma urgente, mas pode ser útil estar atento e seguir as recomendações médicas para manter a saúde geral.

Baseado em:
[Fonte 1], [Fonte 3]
```

### R4 · leigo_curioso · r2 · modelo=qwen2.5:7b
```
Resumo:
No seu relatório, duas condições têm risco baixo: Trombofilia Hereditária (Fator V de Leiden) e Intolerância à Lactose (tipo adulto).

Explicação:
As condições com risco baixo no seu relatório são aquelas que têm uma probabilidade menor de causar problemas de saúde significativos. Isso significa que, embora possam existir, a chance de você desenvolver a condição é baixa.

Na prática:
- Trombofilia Hereditária (Fator V de Leiden): Este relatório indica que você não possui as mutações genéticas mais comuns associadas a coágulos sanguíneos hereditários. Portanto, seu risco genético para trombose está dentro do normal para a população geral. Isso significa que, embora a trombose possa ocorrer, a probabilidade é baixa devido à sua genética.
- Intolerância à Lactose (tipo adulto): Você tem uma tolerância parcial à lactose, o que significa que provavelmente consegue consumir leite e derivados em quantidades moderadas sem grandes problemas. Produtos fermentados como iogurte e queijos curados costumam ser ainda melhor tolerados.

Baseado em:
[Fonte 1], [Fonte 3]
```

### R4 · medico · r1 · modelo=qwen2.5:7b
```
Resumo:
- Trombofilia Hereditária (Fator V de Leiden): Nível de risco baixo.
- Intolerância à Lactose (tipo adulto): Nível de risco baixo.

Explicação:
As condições genéticas com nível de risco baixo no seu relatório são a Trombofilia Hereditária (Fator V de Leiden) e a Intolerância à Lactose (tipo adulto). Essas condições indicam que a probabilidade de desenvolvimento de certos problemas de saúde associados a elas é menor em comparação com outras condições de risco mais elevado.

Na prática:
Isso significa que, embora você possua variantes genéticas ligadas a essas condições, o risco de manifestação clínica é considerado baixo. Portanto, a necessidade de intervenção médica específica ou monitoramento regular é menos urgente em comparação com condições de risco alto ou médio.

Baseado em:
- [Fonte 1]
- [Fonte 3]
```

### R4 · medico · r2 · modelo=qwen2.5:7b
```
Resumo:
As condições com risco baixo no relatório são Trombofilia Hereditária (Fator V de Leiden) e Intolerância à Lactose (tipo adulto).

Explicação:
As condições com risco baixo são aquelas que não apresentam mutações genéticas associadas a um alto risco de desenvolver certos problemas de saúde. No seu relatório, foram identificadas duas condições nessa categoria.

1. Trombofilia Hereditária (Fator V de Leiden): Embora seja uma condição que pode levar a coágulos sanguíneos hereditários, seu relatório indica que você não possui as mutações genéticas mais comuns associadas a este risco. Portanto, seu risco genético para trombose está dentro do normal para a população geral.
2. Intolerância à Lactose (tipo adulto): Esta condição indica que você tem uma tolerância parcial à lactose, permitindo que você consuma leite e derivados em quantidades moderadas sem grandes problemas. Produtos fermentados como iogurte e queijos curados são ainda melhor tolerados.

Na prática:
Essas condições não requerem tratamento específico, mas podem ser importantes para considerar em contextos de saúde geral. Por exemplo, a intolerância à lactose pode influenciar a escolha de uma dieta adequada, especialmente se você estiver seguindo um plano alimentar mais restritivo.

Baseado em:
[Fonte 1], [Fonte 3]
```
