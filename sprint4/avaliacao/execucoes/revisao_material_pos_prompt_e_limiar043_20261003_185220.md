# Revisão manual — pos_prompt_e_limiar043_20261003_185220.jsonl
Para cada resposta: trechos entregues ao modelo e a resposta. Procurar informação acrescentada que não esteja nos trechos e que não seja número/gene/SNP.

## R3 — Qual é o risco de câncer de mama ao longo da vida segundo o relatório?
**Trechos (leigo_ansioso):**
- `resultado_2.2`: Condição: Carcinoma de Mama (BRCA-relacionado). Categoria: Oncologia. Nível de risco: Alto. Foi encontrada uma alteração importante em um gene chamado BRCA2, que normalmente protege contra câncer. Essa alteração aumenta significativamente o risco de câncer de mama e ovário ao longo da vida. É muito importante consultar um especialista em genética médica para discutir as próximas etapas. Isso significa que você precisa de acompanhamento médico especializado e exames mais frequentes. Existem estratégias preventivas eficazes que um geneticista pode discutir com você.
- `recomendacao_2.2`: Recomendação para Carcinoma de Mama (BRCA-relacionado) (risco Alto): Encaminhamento urgente para aconselhamento genético oncológico. Rastreamento mamográfico anual a partir dos 25 anos. Ressonância magnética de mama anual. Discussão de estratégias de redução de risco com oncologista geneticista. Urgência: Urgente - recomenda-se consulta com geneticista oncológico em até 15 dias.
- `sumario`: Resumo do relatório genético: Foram analisadas 7 condições genéticas. Você tem 2 condições de risco alto que merecem atenção especial, 3 de risco médio para monitoramento e 2 de risco baixo sem preocupação específica. Total de condições analisadas: 7. Condições de risco alto: 2. Condições de risco médio: 3. Condições de risco baixo: 2. Recomendações prioritárias: Consulta com endocrinologista para diabetes; Aconselhamento genético oncológico urgente; Monitoramento cardiovascular anual.

### R3 · leigo_ansioso · r1 · modelo=qwen2.5:7b
```
Resumo:
O relatório indica um risco alto de câncer de mama devido à alteração no gene BRCA2.

Explicação:
O gene BRCA2 é importante para proteger contra o câncer. Quando há uma alteração nesse gene, como no seu caso, o risco de desenvolver câncer de mama aumenta significativamente.

Na prática:
Isso significa que você tem uma tendência maior a desenvolver câncer de mama ao longo da vida, mas não há certeza absoluta. É importante ter acompanhamento médico especializado e realizar exames mais frequentes.

Baseado:
[Fonte 1]
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
As condições com risco baixo são aquelas que, embora possam ter uma ligação genética, não apresentam um alto nível de probabilidade de manifestação clínica. Isso significa que, embora você possa ter um risco ligeiramente aumentado, a probabilidade de desenvolver a condição é baixa.

Na prática:
Isso é uma ótima notícia, pois indica que você não precisa se preocupar com essas condições de forma urgente. No entanto, é sempre bom manter uma atenção moderada e seguir as recomendações médicas para manter a saúde em geral.

Baseado:
[Fonte 1], [Fonte 3]
```
