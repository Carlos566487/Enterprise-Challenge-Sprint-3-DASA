# Curva de limiar de similaridade — e o teste do modelo multilíngue

**Genera AI · Sprint 4 · Avaliação de IA & PLN** — João (RM565999)

Todos os números vêm de execuções reais gravadas em `execucoes/`:

| Arquivo | O que é |
|---|---|
| `rankings_producao_20260929_190552.json` | ranking real (top_k 25 e 10) das 20 perguntas na busca de produção (`all-MiniLM-L6-v2`) |
| `rankings_multilingue_20260929_190631.json` | o mesmo, numa base **paralela fora do repositório** com `paraphrase-multilingual-MiniLM-L12-v2` |
| `curva_limiar_20260929_190819.json` | curva, separação, fronteira e análise de top_k, para os dois modelos |
| `varredura_limiar_20260928_205359.json` | varredura real anterior (18 pontos, 288 buscas) usada para validar o método |

**Método.** O limiar só filtra o que a consulta já trouxe. A curva aplica os cortes
analiticamente sobre o ranking real, na ordem de produção de `buscar_trechos()`: primeiro
`top_k` (quantidade de resultados da consulta), depois o filtro de similaridade. **O método
foi validado:** os 18 pontos da varredura real (limiares 0,35–0,60 × top_k 3/4/5, com busca de
verdade a cada ponto) coincidem com a derivação analítica.

População avaliada: **11 perguntas respondíveis** (têm resposta na base) e **5 sem resposta**
(X1, X2, X3, B1, B2). As 4 de guardrail não entram na curva — no contrato v1.0 elas são
bloqueadas antes da busca —, mas aparecem na §4 porque o dashboard busca antes do guardrail.

---

## 1. Conclusão — não existe ponto satisfatório

**Nenhum limiar, em nenhum dos dois modelos, recupera as 11 perguntas respondíveis sem dar
trecho a pelo menos uma pergunta sem resposta.** As duas populações se sobrepõem:

| | Produção (`all-MiniLM-L6-v2`) | Multilíngue |
|---|---:|---:|
| Menor similaridade do melhor chunk essencial de uma respondível | 0,355 (R3) | 0,345 (A1) |
| Maior similaridade de uma pergunta sem resposta | 0,527 (X2) | 0,585 (B2) |
| Algum limiar separa? | **não** | **não** |
| Ponto com 11/11 e 0 sem-resposta (top_k 3–10) | **nenhum** | **nenhum** |

Ajustar o número só escolhe qual erro preferir. O que existe é uma **fronteira de
compromisso**.

### Fronteira de compromisso (produção, top_k=3)

Pontos não dominados: nenhum outro limiar dá mais ganho com menos custo.

| Limiar | Ganho: respondíveis com chunk essencial (de 11) | **Custo: sem resposta que recebem trecho (de 5)** | Custo: trechos irrelevantes admitidos |
|---|---:|---|---:|
| 0,43 | **9** | **1** (X2 — recebe os trechos de Alzheimer) | 6 |
| 0,45 | 8 | 1 (X2) | 5 |
| 0,48–0,49 | 6 | 1 (X2) | 1 |
| 0,53 | 4 | **0** | 1 |
| 0,58–0,60 | 3 | 0 | 0 |
| *0,50 (atual)* | *4* | *1 (X2)* | *1* |

**O limiar de produção 0,50 não está na fronteira. Ele é dominado dos dois lados:**
- 0,48–0,49 dá **6/11** pelo **mesmo custo** (X2 e 1 irrelevante);
- 0,53 dá o **mesmo ganho** (4/11) com **custo zero** em perguntas sem resposta.

A escolha dentro da fronteira não é técnica. Depende de qual erro é pior para o paciente:
recusar uma pergunta que tem resposta ("não encontrei informação") ou responder uma pergunta
sem resposta com trechos de outra condição (Parkinson respondido com dados de Alzheimer). Os
dois pontos defensáveis são os extremos úteis:
- **0,43** — máxima cobertura (9/11), ao custo de 1 pergunta sem resposta em 5 receber
  contexto errado;
- **0,53** — nenhuma pergunta sem resposta recebe contexto, ao custo de cobrir só 4/11.

Os dois são estritamente melhores que o 0,50 atual. Nenhum é bom. Mudar o padrão de produção
é decisão do grupo.

---

## 2. Curva completa — produção, top_k=3

O custo (coluna em negrito) tem o mesmo peso visual que o ganho.

| Limiar | Respondíveis com essencial (de 11) | Recall | Precisão | **Sem resposta que recebem trecho (de 5)** | Irrelevantes admitidos | X2 (Parkinson) recebe |
|---:|---:|---:|---:|---|---:|---|
| 0,35 | 9 | 0,82 | 0,61 | **5** (X1, X2, X3, B1, B2) | 13 | recomendacao_2.4, resultado_2.4, paciente |
| 0,36 | 9 | 0,82 | 0,61 | **3** (X2, X3, B2) | 13 | recomendacao_2.4, resultado_2.4, paciente |
| 0,37 | 9 | 0,82 | 0,62 | **2** (X2, B2) | 12 | recomendacao_2.4, resultado_2.4, paciente |
| 0,38 | 9 | 0,82 | 0,62 | **2** (X2, B2) | 12 | recomendacao_2.4, resultado_2.4, paciente |
| 0,39 | 9 | 0,82 | 0,68 | **2** (X2, B2) | 10 | recomendacao_2.4, resultado_2.4, paciente |
| 0,40 | 9 | 0,82 | 0,68 | **1** (X2) | 10 | recomendacao_2.4, resultado_2.4, paciente |
| 0,41 | 9 | 0,82 | 0,68 | **1** (X2) | 10 | recomendacao_2.4, resultado_2.4, paciente |
| 0,42 | 9 | 0,82 | 0,73 | **1** (X2) | 9 | recomendacao_2.4, resultado_2.4, paciente |
| 0,43 | 9 | 0,82 | 0,82 | **1** (X2) | 6 | recomendacao_2.4, resultado_2.4, paciente |
| 0,44 | 8 | 0,73 | 0,82 | **1** (X2) | 6 | recomendacao_2.4, resultado_2.4, paciente |
| 0,45 | 8 | 0,68 | 0,83 | **1** (X2) | 5 | recomendacao_2.4, resultado_2.4, paciente |
| 0,46 | 6 | 0,55 | 0,78 | **1** (X2) | 4 | recomendacao_2.4, resultado_2.4, paciente |
| 0,47 | 6 | 0,55 | 0,85 | **1** (X2) | 2 | recomendacao_2.4, resultado_2.4, paciente |
| 0,48 | 6 | 0,55 | 0,95 | **1** (X2) | 1 | recomendacao_2.4, resultado_2.4 |
| 0,49 | 6 | 0,55 | 0,95 | **1** (X2) | 1 | recomendacao_2.4, resultado_2.4 |
| **0,50** | **4** | **0,36** | 0,93 | **1** (X2) | 1 | recomendacao_2.4, resultado_2.4 |
| 0,51 | 4 | 0,36 | 0,93 | **1** (X2) | 1 | recomendacao_2.4, resultado_2.4 |
| 0,52 | 4 | 0,36 | 0,93 | **1** (X2) | 1 | recomendacao_2.4 |
| 0,53 | 4 | 0,36 | 0,93 | **0** | 1 | — |
| 0,54 | 3 | 0,27 | 0,92 | **0** | 1 | — |
| 0,55 | 3 | 0,27 | 0,92 | **0** | 1 | — |
| 0,56 | 3 | 0,27 | 0,92 | **0** | 1 | — |
| 0,57 | 3 | 0,27 | 0,92 | **0** | 1 | — |
| 0,58 | 3 | 0,27 | 1,00 | **0** | 0 | — |
| 0,59 | 3 | 0,27 | 1,00 | **0** | 0 | — |
| 0,60 | 3 | 0,27 | 1,00 | **0** | 0 | — |

Recall = média, sobre as 11 respondíveis, da fração de chunks essenciais recuperados.
Precisão = média, nas respondíveis que receberam trecho, da fração de trechos essenciais ou
aceitáveis. Os perfis `leigo_curioso` (top_k=4) e `medico` (top_k=5) têm o **mesmo ganho** em
todos os limiares e **mais irrelevantes** (em 0,43: 6 com top_k=3, 11 com top_k=4, 14 com top_k=5);
as curvas completas estão no JSON.

**X2 (Parkinson).** Recebe trecho em todo limiar até 0,52. Sempre os chunks de **Alzheimer**
(`recomendacao_2.4`, `resultado_2.4`, a 0,527 e 0,510), mais `paciente` abaixo de 0,48. Só sai
a partir de 0,53, junto com a perda de F1 logo depois (0,536).

---

## 3. O top_k=3 é restrição?

Posição real de cada chunk essencial no top 10 de produção (`rankings_producao_*.json`, busca
com top_k=10):

| Pergunta | Chunk essencial | Posição | Similaridade |
|---|---|---:|---:|
| **F3** | `sumario` | **6** | 0,403 |
| **R3** | `marcadores_2.2` | **fora do top 10** (13º no top 25) | 0,355 |
| demais 9 | — | ≤ 3 | — |

**Sim, para 1 das 11 perguntas.** A F3 só recupera o chunk essencial com top_k ≥ 6 e limiar
≤ 0,40. Com top_k=6 e limiar 0,40, o ganho sobe de 9 para **10/11**, e o custo em irrelevantes
sobe de 10 para **28** (a X2 passa a receber 6 trechos). A R3 não é recuperável com top_k ≤ 10
em nenhum limiar ≥ 0,35: o trecho com o risco numérico está longe demais no ranking. O top_k é
candidato a ajuste, mas o ganho é de uma pergunta e o preço é quase triplicar o ruído.

---

## 4. Perguntas de guardrail no dashboard

No contrato v1.0, G1–G4 são bloqueadas antes da busca. No dashboard, a busca vem antes do
guardrail. **Medido:** com top_k=3 e o limiar 0,50 que o dashboard usa, **G1, G2 e G4 recebem
trechos** (`curva_limiar_*.json`, campo `guardrail_com_trecho`). É isso que alimentaria o painel
"Fontes utilizadas" ao lado da recusa — o bug descrito para o Endrew no relatório (§13). A
recuperação foi medida; a exibição foi constatada por leitura de código.

---

## 5. Teste da hipótese da causa raiz: modelo multilíngue

**Hipótese:** a sobreposição vem de usar um modelo treinado em inglês sobre português; um
modelo multilíngue abriria a faixa e separaria as populações.

**Experimento:** uma base ChromaDB paralela, **fora do repositório** (no diretório temporário
da sessão), com os **mesmos 25 documentos e metadados** lidos da base de produção,
codificados por `paraphrase-multilingual-MiniLM-L12-v2`, e consultados com a mesma lógica de
`buscar_trechos()`. **Dimensão confirmada: 384**, igual à de produção — a troca não mexeria na
arquitetura do ChromaDB. A base de produção e `gerar_embeddings.py` não foram tocados.

### Resultados lado a lado

| Métrica | Produção | Multilíngue | A hipótese previa |
|---|---:|---:|---|
| Desvio padrão das similaridades (20 × 25) | 0,128 | 0,156 | mais larga ✔ |
| Amplitude média por pergunta | 0,435 | 0,531 | mais larga ✔ |
| Margem média entre 1º e 2º chunk | 0,042 | 0,066 | maior ✔ |
| **AUC de separação** (respondível > sem resposta) | **0,818** | **0,727** | maior ✘ |
| Existe limiar que separa? | não | **não** | sim ✘ |
| **A1** (ancestralidade) — chunk certo | 0,494 | **0,345** | subir ✘ |
| **X2** (Parkinson) — melhor chunk | 0,527 | 0,496 | descer ✔ (pouco) |
| Maior pergunta sem resposta | X2 0,527 | **B2 0,585** ("e o gene?") | — |
| **Ordenação, sem limiar:** melhor essencial em 1º lugar | 5/11 | **7/11** | — |
| Melhor essencial no top 3 | 9/11 | 9/11 | — |
| MRR do melhor essencial | 0,659 | **0,765** | — |
| No limiar atual 0,50, top_k=3: respondíveis com essencial | 4/11 | **7/11** | — |
| No limiar atual 0,50, top_k=3: sem resposta com trecho | 1 (X2) | 1 (B2) | — |
| Melhor ponto da fronteira (top_k=3) | 9/11 com 1 sem-resposta (0,43) | 8/11 com 2 (0,47); 7/11 com 1 (0,50) | — |

### Veredito

**A hipótese é refutada no que importa.** O modelo multilíngue abre a faixa de
similaridades, como previsto, mas **não separa melhor as populações — separa pior** (AUC
0,818 → 0,727). A1, o caso-símbolo, **desce** de 0,494 para 0,345. Uma pergunta sem resposta
("e o gene?") passa a marcar 0,585, acima de várias respondíveis. **A sobreposição não é
causada pelo idioma do modelo; ela persiste com um modelo treinado em português.** A
explicação atribuída ao `all-MiniLM-L6-v2` no relatório anterior estava errada e foi corrigida.

A conclusão não depende de um caso só: tirando B2 (cuja anotação "nenhum chunk relevante" é a
mais discutível — "e o gene?" traz de fato chunks de genes), o multilíngue ainda não separa
(maior sem-resposta X2 0,496 > menor essencial A1 0,345). Tirando X2, a produção também não
separa (B2 0,390 > R3 0,355).

**O que o experimento mostra de positivo:** o multilíngue **ordena melhor**. O chunk
essencial fica em 1º lugar em 7 de 11 perguntas (contra 5), e o MRR sobe de 0,66 para 0,77. No
limiar atual, recupera o essencial em **7/11 perguntas contra 4/11**, com o mesmo número de
perguntas sem resposta recebendo trecho (1). Ele melhora a recuperação, mas não resolve o
problema de decidir, pela similaridade, se a resposta existe.

**Explicação mais provável para a sobreposição** (hipótese nova, não testada): as 25
passagens são todas do mesmo relatório e do mesmo domínio (risco genético, recomendações), e as
perguntas sem resposta estão perto desse domínio por construção (Parkinson ao lado de
Alzheimer; "e o gene?" ao lado dos marcadores). Num corpus tão homogêneo, a similaridade de
cosseno mede proximidade de assunto, não se a resposta está presente. A decisão
"sem_contexto" pede outro instrumento — por exemplo, o próprio LLM verificando se os trechos
respondem à pergunta, ou uma reclassificação (reranker) — e não um limiar melhor.

**Limites do experimento:** 11 perguntas respondíveis e 5 sem resposta; uma execução por
modelo (a busca é determinística, então repetir não mudaria o resultado); um único modelo
multilíngue testado. Diferenças de 1–2 perguntas estão dentro do que um conjunto maior poderia
inverter.

---

## 6. Curva completa — multilíngue, top_k=3

| Limiar | Respondíveis com essencial (de 11) | Recall | Precisão | **Sem resposta que recebem trecho (de 5)** | Irrelevantes admitidos | X2 (Parkinson) recebe |
|---:|---:|---:|---:|---|---:|---|
| 0,35 | 8 | 0,73 | 0,65 | **5** (X1, X2, X3, B1, B2) | 10 | resultado_2.4, recomendacao_2.4, marcadores_2.4 |
| 0,36–0,43 | 8 | 0,73 | 0,65–0,72 | **4** (X1, X2, X3, B2) | 10–8 | resultado_2.4, recomendacao_2.4, marcadores_2.4 |
| 0,44–0,46 | 8 | 0,73 | 0,72–0,73 | **2** (X2, B2) | 8–7 | resultado_2.4, recomendacao_2.4 |
| 0,47 | 8 | 0,73 | 0,88 | **2** (X2, B2) | 3 | resultado_2.4 |
| 0,48–0,49 | 7 | 0,64 | 0,87–0,93 | **2** (X2, B2) | 3–2 | resultado_2.4 |
| **0,50–0,51** | **7** | 0,64 | 0,93 | **1** (B2) | 2 | — |
| 0,52–0,54 | 6 | 0,55 | 0,92–0,96 | **1** (B2) | 2–1 | — |
| 0,55–0,58 | 5 | 0,45 | 0,95 | **1** (B2) | 1 | — |
| 0,59 | 5 | 0,45 | 0,95 | **0** | 1 | — |
| 0,60 | 5 | 0,45 | 1,00 | **0** | 0 | — |

Linhas agrupadas onde o resultado é idêntico; os 26 pontos individuais estão em
`curva_limiar_20260929_190819.json` e `curva_limiar_20260929_190819_tabelas.md`.
