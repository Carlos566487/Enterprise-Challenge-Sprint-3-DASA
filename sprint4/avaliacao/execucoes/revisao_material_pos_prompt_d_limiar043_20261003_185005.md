# Revisão manual — pos_prompt_d_limiar043_20261003_185005.jsonl
Para cada resposta: trechos entregues ao modelo e a resposta. Procurar informação acrescentada que não esteja nos trechos e que não seja número/gene/SNP.

## B3 — diabete risco alto oq faço
**Trechos (medico):**
- `resultado_2.1`: Condição: Diabetes Mellitus Tipo 2. Categoria: Metabolismo e Endocrinologia. Nível de risco: Alto. Seu DNA indica uma chance maior de desenvolver diabetes tipo 2. Dois genes importantes para o controle do açúcar no sangue apresentam variações que aumentam esse risco. Isso não significa que você vai ter diabetes, mas que precisa de mais atenção com alimentação e exercícios. Na prática, isso significa que você deve evitar açúcares simples, fazer exercícios regularmente e checar sua glicemia a cada 6 meses. Pequenas mudanças no dia a dia podem fazer grande diferença.
- `recomendacao_2.1`: Recomendação para Diabetes Mellitus Tipo 2 (risco Alto): Monitoramento semestral de glicemia de jejum e HbA1c. Adoção de dieta hipoglicídica com índice glicêmico controlado. Prática regular de atividade física aeróbica (mínimo 150 minutos por semana). Avaliação com endocrinologista recomendada. Urgência: Alta - recomenda-se consulta com endocrinologista nos próximos 30 dias.
- `sumario`: Resumo do relatório genético: Foram analisadas 7 condições genéticas. Você tem 2 condições de risco alto que merecem atenção especial, 3 de risco médio para monitoramento e 2 de risco baixo sem preocupação específica. Total de condições analisadas: 7. Condições de risco alto: 2. Condições de risco médio: 3. Condições de risco baixo: 2. Recomendações prioritárias: Consulta com endocrinologista para diabetes; Aconselhamento genético oncológico urgente; Monitoramento cardiovascular anual.
- `recomendacao_2.4`: Recomendação para Doença de Alzheimer (início tardio) (risco Médio): Manutenção de atividade cognitiva regular (leitura, aprendizado de novas habilidades). Controle de fatores de risco cardiovascular (pressão, colesterol, diabetes). Dieta mediterrânea. Avaliação neurológica periódica a partir dos 50 anos. Urgência: .
- `recomendacao_2.5`: Recomendação para Doença Celíaca (risco Médio): Atenção a sintomas gastrointestinais persistentes (diarreia, distensão, má absorção). Sorologia para anticorpos anti-transglutaminase (tTG-IgA) em caso de sintomas. Não iniciar dieta isenta de glúten sem diagnóstico confirmado por biópsia intestinal. Urgência: .

### B3 · medico · r1 · modelo=qwen2.5:7b
```
Resumo:
O relatório indica um risco alto para Diabetes Mellitus Tipo 2, com base em variações genéticas específicas.

Explicação:
Dois genes importantes para o controle do açúcar no sangue apresentam variações que aumentam o risco de desenvolver diabetes tipo 2. Isso significa que, embora não seja garantido, a probabilidade de desenvolver a doença é maior.

Na prática:
Isso significa que você deve estar mais atento a fatores de risco e adotar medidas preventivas. Recomenda-se evitar açúcares simples, fazer exercícios regularmente e checar a glicemia a cada 6 meses.

Baseado:
[Fonte 1], [Fonte 2]
```

### B3 · medico · r2 · modelo=qwen2.5:7b
```
Resumo:
O relatório indica um risco alto para Diabetes Mellitus Tipo 2, com base em variações genéticas que aumentam a chance de desenvolver a doença.

Explicação:
Dois genes importantes para o controle do açúcar no sangue apresentam variações que aumentam o risco de desenvolver diabetes tipo 2. Isso significa que, embora não seja garantido que você terá a doença, seu risco é considerado alto devido a essas variações genéticas.

Na prática:
Isso significa que você deve estar mais atento a fatores de estilo de vida que podem influenciar o desenvolvimento da doença, como dieta e atividade física. Recomenda-se evitar açúcares simples, fazer exercícios regularmente e checar sua glicemia a cada 6 meses.

Baseado em:
[Fonte 1]
```

### B3 · medico · r3 · modelo=qwen2.5:7b
```
Resumo:
O relatório indica um risco alto de Diabetes Mellitus Tipo 2, baseado em variações genéticas que aumentam a chance de desenvolver a condição. Recomenda-se monitoramento regular e medidas preventivas.

Explicação:
Dois genes importantes para o controle do açúcar no sangue apresentam variações que aumentam o risco de desenvolver diabetes tipo 2. Isso significa que, embora não seja garantido que você terá a doença, é mais provável que você precise de mais atenção com a alimentação e o exercício físico.

Na prática:
Isso significa que você deve evitar alimentos ricos em açúcar simples, manter uma dieta equilibrada e fazer exercícios regularmente. Além disso, é recomendado que você verifique sua glicemia a cada 6 meses.

Baseado:
[Fonte 1], [Fonte 2]
```
