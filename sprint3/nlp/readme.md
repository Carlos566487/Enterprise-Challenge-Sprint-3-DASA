# 🧠 Módulo de NLP — Simplificação de Linguagem e Resumos Automáticos

## Projeto Genera AI — DASA Challenge

Este diretório contém o módulo de **Processamento de Linguagem Natural (NLP)** desenvolvido na **Sprint 3** do projeto **Genera AI**, realizado no contexto do desafio acadêmico da DASA.

O objetivo principal deste módulo é melhorar a comunicação entre o sistema de inteligência artificial e o usuário final, especialmente em situações nas quais informações genéticas originalmente apresentadas em linguagem técnica precisam ser compreendidas por pessoas sem conhecimento especializado na área.

A solução desenvolvida atua sobre os dados e respostas produzidos pelo sistema para:

- simplificar termos técnicos relacionados à genética;
- tornar explicações mais acessíveis para usuários leigos;
- preservar o significado essencial das informações;
- gerar resumos automáticos de relatórios estruturados;
- identificar os principais temas abordados nas interações;
- atualizar automaticamente o resumo do histórico de conversas;
- calcular métricas simples de legibilidade;
- integrar o processamento de NLP ao agente especialista e ao fluxo de RAG desenvolvido anteriormente.

> **Importante:** o módulo de NLP não realiza diagnóstico médico e não cria novas conclusões clínicas. Seu papel é organizar, resumir e tornar mais acessíveis as informações disponíveis no contexto fornecido pelo sistema.

---

# 1. Visão Geral da Solução

Relatórios genéticos podem conter termos como *variante genética*, *predisposição genética*, *marcadores genéticos*, *genótipo*, *fenótipo*, *herdabilidade* e *polimorfismo*.

Embora esses termos sejam adequados em um contexto técnico, eles podem dificultar a compreensão do resultado por usuários que não possuem formação na área.

Por esse motivo, o módulo desenvolvido na Sprint 3 adiciona uma camada de **NLP orientada à acessibilidade da informação**.

De forma simplificada, o fluxo implementado pode ser representado da seguinte maneira:

```text
Pergunta do usuário
        ↓
Agente Especialista
        ↓
Validação por Guardrails
        ↓
Recuperação de contexto pelo RAG
        ↓
Construção da resposta
        ↓
Módulo de NLP
        ↓
Simplificação da linguagem
        ↓
Cálculo de métricas
        ↓
Registro da interação
        ↓
Atualização automática do resumo
        ↓
Resposta final ao usuário
```

Dessa forma, o NLP não substitui os mecanismos implementados anteriormente. Ele funciona como uma **camada complementar de processamento**, integrada ao fluxo existente.

---

# 2. Objetivos do Módulo

A implementação foi estruturada em quatro objetivos principais.

## 2.1 Simplificação de linguagem

Transformar expressões técnicas em construções mais compreensíveis para usuários leigos.

Exemplo:

**Texto técnico:**

> O relatório identificou uma variante genética associada a uma predisposição genética para determinada condição.

**Texto simplificado:**

> O relatório identificou uma alteração no DNA ligada a uma chance maior de desenvolver determinada condição.

O objetivo não é apenas substituir palavras isoladas, mas tornar a comunicação final mais natural e compreensível.

---

## 2.2 Geração automática de resumos

O sistema também utiliza os dados estruturados do relatório para produzir uma visão resumida das informações mais importantes.

Entre os dados utilizados estão:

- quantidade total de condições analisadas;
- quantidade de condições classificadas por nível de risco;
- principais resultados presentes no relatório;
- recomendações prioritárias;
- histórico de perguntas realizadas ao agente.

---

## 2.3 Resumo das interações

Além do relatório, o sistema acompanha as perguntas feitas pelo usuário.

Com isso, o módulo consegue identificar temas recorrentes e gerar automaticamente um resumo do histórico.

Exemplo:

```text
RESUMO AUTOMÁTICO DAS INTERAÇÕES

O histórico possui 3 interações válidas. Os principais temas abordados
foram interpretação dos níveis de risco genético, risco genético
relacionado ao diabetes, alterações e características encontradas
no DNA e necessidade de acompanhamento profissional.

A dúvida mais recente do usuário foi:
"Preciso procurar um médico por causa desse resultado?"

TEMAS IDENTIFICADOS:
- interpretação dos níveis de risco genético
- risco genético relacionado ao diabetes
- alterações e características encontradas no DNA
- necessidade de acompanhamento profissional
```

Esse mecanismo permite preservar uma representação resumida do contexto da conversa sem simplesmente reproduzir todas as perguntas anteriores.

---

## 2.4 Integração com o agente especialista

O módulo foi integrado ao agente desenvolvido anteriormente para que o processamento de NLP faça parte do fluxo da aplicação.

A integração permite combinar:

- validação de segurança;
- contexto recuperado pelo RAG;
- resposta do agente;
- simplificação de linguagem;
- métricas de legibilidade;
- armazenamento do histórico;
- resumo automático das interações.

---

# 3. Estrutura de Arquivos

A organização deste módulo é:

```text
sprint3/
└── nlp/
    ├── integracao/
    │   └── agente_nlp.py
    │
    ├── nlp_simplificacao.py
    ├── resumos_automaticos.py
    └── README.md
```

Cada arquivo possui uma responsabilidade específica.

| Arquivo | Responsabilidade |
|---|---|
| `nlp_simplificacao.py` | Simplificação de termos e textos técnicos e cálculo de métricas |
| `resumos_automaticos.py` | Geração de resumos do relatório e das interações |
| `integracao/agente_nlp.py` | Integração entre agente especialista, NLP e histórico |
| `README.md` | Documentação técnica do módulo |

Essa separação facilita a manutenção e evita concentrar diferentes responsabilidades em um único arquivo.

---

# 4. Arquivo `nlp_simplificacao.py`

O arquivo `nlp_simplificacao.py` concentra as funções relacionadas à **simplificação da linguagem** e à **análise básica de legibilidade**.

---

## 4.1 Dicionário de termos técnicos

O módulo utiliza um conjunto controlado de termos técnicos e suas respectivas formas mais acessíveis.

Entre os conceitos tratados estão:

```text
predisposição genética
variante genética
marcadores genéticos
fenótipo
genótipo
risco aumentado
risco reduzido
herdabilidade
polimorfismo
alelo
```

A estratégia adotada permite que termos encontrados no texto sejam identificados e tratados antes da apresentação ao usuário.

Entretanto, durante o desenvolvimento foi observado que uma substituição puramente literal pode produzir construções gramaticalmente inadequadas.

Por exemplo, uma substituição direta poderia gerar:

```text
Também foram avaliados características do DNA presentes no DNA.
```

ou:

```text
O informação genética presente no DNA...
```

Esses resultados demonstram uma limitação importante de abordagens baseadas exclusivamente em substituição lexical.

Por isso, o texto final foi refinado para privilegiar construções mais naturais.

---

# 5. Estratégia de Simplificação

A simplificação foi projetada para preservar três propriedades:

1. **clareza**;
2. **coerência gramatical**;
3. **preservação do significado essencial**.

Um dos testes utilizados durante o desenvolvimento partiu do seguinte texto:

### Texto original

```text
O relatório identificou uma variante genética associada a uma
predisposição genética para determinada condição.

Também foram avaliados marcadores genéticos presentes no DNA.

Esse resultado indica risco aumentado, mas não significa que
a pessoa necessariamente desenvolverá a condição.

O genótipo deve ser interpretado em conjunto com outros fatores,
como histórico familiar, hábitos de vida e acompanhamento profissional.

O resultado apresenta uma associação genética e não representa
um diagnóstico definitivo.
```

Após o processamento, foi obtida uma versão mais acessível:

### Texto simplificado

```text
O relatório identificou uma alteração no DNA ligada a uma chance maior
de desenvolver determinada condição.

Também foram analisadas características do DNA.

Esse resultado indica chance maior, mas não significa que a pessoa
terá essa condição.

Essas informações do DNA devem ser analisadas junto com outros fatores,
como histórico familiar, hábitos de vida e acompanhamento profissional.

O resultado mostra uma relação com fatores genéticos e não é um diagnóstico.
```

Essa versão reduz a quantidade de expressões especializadas sem eliminar informações importantes sobre a interpretação do resultado.

---

# 6. Funções de Simplificação

## `substituir_termo()`

Responsável por localizar determinado termo técnico no texto.

A busca utiliza expressões regulares (*regular expressions*) e não diferencia letras maiúsculas de minúsculas.

A função também busca evitar substituições indevidas dentro de outras palavras.

---

## `simplificar_termos()`

Aplica as regras de simplificação definidas pelo módulo.

Os termos são processados considerando seu tamanho, permitindo que expressões compostas sejam tratadas antes de palavras menores potencialmente presentes dentro delas.

Essa estratégia reduz conflitos entre substituições.

---

## `limpar_texto()`

Responsável pela normalização básica do texto.

Entre suas funções estão:

- remoção de espaços duplicados;
- normalização de quebras de linha;
- remoção de espaços desnecessários no início e no final.

---

## `dividir_frases()`

Realiza uma separação simples das frases utilizando sinais de pontuação como referência.

Essa função é posteriormente utilizada no cálculo das métricas de texto.

---

## `simplificar_texto()`

É a principal função pública do módulo de simplificação.

O processamento segue, de forma geral:

```text
Texto recebido
      ↓
Validação de conteúdo
      ↓
Limpeza do texto
      ↓
Simplificação dos termos
      ↓
Ajustes de linguagem
      ↓
Nova limpeza
      ↓
Cálculo das métricas
      ↓
Retorno estruturado
```

O retorno contém:

```python
{
    "texto_original": "...",
    "texto_simplificado": "...",
    "metricas_original": {...},
    "metricas_simplificado": {...}
}
```

Isso permite comparar diretamente o texto antes e depois do processamento.

---

# 7. Métricas de Legibilidade

O módulo implementa métricas simples para auxiliar na comparação entre o texto original e o texto simplificado.

As métricas calculadas são:

- número de palavras;
- número de frases;
- média de palavras por frase;
- média de caracteres por palavra.

Exemplo obtido nos testes:

### Texto original

```python
{
    "palavras": 68,
    "frases": 5,
    "media_palavras_por_frase": 13.6,
    "media_caracteres_por_palavra": 6.41
}
```

### Texto simplificado

```python
{
    "palavras": 69,
    "frases": 5,
    "media_palavras_por_frase": 13.8,
    "media_caracteres_por_palavra": 5.61
}
```

Um resultado relevante desse teste foi a redução da média de caracteres por palavra:

```text
6.41 → 5.61
```

Isso é coerente com o objetivo de substituir parte do vocabulário especializado por palavras mais familiares.

### Observação importante

Essas métricas **não devem ser interpretadas isoladamente como uma medida definitiva de compreensão**.

Um texto pode possuir mais palavras e ainda assim ser mais fácil de entender.

Por isso, as métricas funcionam como indicadores auxiliares, enquanto a qualidade da simplificação também depende da coerência semântica e gramatical.

---

# 8. Arquivo `resumos_automaticos.py`

O arquivo `resumos_automaticos.py` implementa a segunda parte principal da solução: a geração automática de resumos.

O módulo trabalha com dois tipos de informação:

1. dados estruturados do relatório;
2. histórico de interações entre usuário e agente.

---

# 9. Carregamento dos Dados Estruturados

Os dados utilizados pelo sistema são obtidos a partir do arquivo:

```text
dados_estruturados.json
```

O carregamento é realizado por meio do módulo nativo `json` do Python.

A utilização de dados estruturados permite acessar campos específicos do relatório sem depender da interpretação de um texto completo.

Exemplos de informações utilizadas:

```text
paciente
sumario
total_condicoes_analisadas
condicoes_alto_risco
condicoes_medio_risco
condicoes_baixo_risco
principais_riscos_medico
recomendacoes_prioritarias
```

---

# 10. Resumo Automático do Relatório

A função responsável pelo resumo acessa os dados estruturados e constrói uma representação compacta das informações consideradas mais relevantes.

Um exemplo obtido durante os testes foi:

```text
RESUMO AUTOMÁTICO DO RELATÓRIO

O relatório analisou 7 condições genéticas: 2 foram classificadas
como alto risco, 3 como médio risco e 2 como baixo risco.

PRINCIPAIS RESULTADOS IDENTIFICADOS:
- Diabetes Mellitus Tipo 2 (Alto - percentil 89)
- Carcinoma de Mama BRCA2 (Alto - variante patogênica)
- Hipertensão Arterial (Médio - percentil 67)

RECOMENDAÇÕES PRESENTES NO RELATÓRIO:
- Consulta com endocrinologista para diabetes
- Aconselhamento genético oncológico urgente
- Monitoramento cardiovascular anual
```

A construção foi planejada para evitar redundâncias.

Durante versões anteriores, por exemplo, informações sobre a quantidade de condições analisadas apareciam repetidamente.

A versão final concentra essas informações em uma única sentença:

> O relatório analisou 7 condições genéticas: 2 foram classificadas como alto risco, 3 como médio risco e 2 como baixo risco.

Isso melhora a objetividade do resumo sem eliminar informação.

---

# 11. Resumo Automático das Interações

O sistema também mantém uma representação resumida das perguntas realizadas ao agente.

A função responsável por esse processamento:

1. recebe o histórico de interações;
2. valida as perguntas existentes;
3. ignora entradas sem conteúdo válido;
4. identifica temas relacionados às perguntas;
5. remove repetições;
6. organiza os temas encontrados;
7. identifica a pergunta mais recente;
8. gera uma descrição textual do histórico.

---

# 12. Identificação de Temas

A identificação dos temas permite transformar perguntas específicas em categorias mais gerais.

Durante os testes foram identificados temas como:

```text
interpretação dos níveis de risco genético
risco genético relacionado ao diabetes
alterações e características encontradas no DNA
informações analisadas no DNA
necessidade de acompanhamento profissional
ancestralidade genética
diferença entre predisposição genética e diagnóstico
```

Por exemplo:

### Pergunta

```text
O que meu relatório diz sobre ancestralidade?
```

### Tema identificado

```text
ancestralidade genética
```

Outro exemplo:

### Pergunta

```text
Isso significa que eu tenho a doença?
```

### Tema

```text
diferença entre predisposição genética e diagnóstico
```

A utilização de temas permite representar o histórico de forma mais compacta e semanticamente útil.

---

# 13. Tratamento de Singular e Plural

O resumo também considera a quantidade de interações existentes.

Com apenas uma interação:

```text
O histórico possui 1 interação válida.
```

Com várias:

```text
O histórico possui 3 interações válidas.
```

O mesmo princípio é utilizado na apresentação dos temas.

Quando existe apenas um:

```text
O principal tema abordado foi ancestralidade genética.
```

Quando existem vários:

```text
Os principais temas abordados foram interpretação dos níveis de risco
genético, risco genético relacionado ao diabetes e necessidade de
acompanhamento profissional.
```

Esse tratamento melhora a naturalidade da saída gerada.

---

# 14. Atualização Automática do Histórico

O módulo implementa uma função específica para atualizar o resumo quando uma nova interação é registrada.

O fluxo é:

```text
Histórico atual
      +
Nova interação
      ↓
Atualização da lista
      ↓
Nova análise dos temas
      ↓
Geração do resumo atualizado
```

Exemplo:

### Histórico inicial

```text
1. O que significa risco alto?
2. O que meu relatório diz sobre diabetes?
3. O que significa essa alteração no DNA?
```

### Nova pergunta

```text
Isso significa que eu tenho a doença?
```

O resumo passa a incorporar também o tema:

```text
diferença entre predisposição genética e diagnóstico
```

e a nova pergunta passa a ser registrada como a dúvida mais recente.

---

# 15. Testes do Módulo de Resumos

Foram implementados diferentes cenários de teste para validar o comportamento do sistema.

## Teste 1 — Resumo automático do relatório

Valida:

- leitura dos dados estruturados;
- quantidade de condições;
- classificação dos riscos;
- principais resultados;
- recomendações.

---

## Teste 2 — Resumo automático das interações

Valida:

- quantidade de interações;
- identificação de múltiplos temas;
- organização dos temas;
- identificação da pergunta mais recente.

---

## Teste 3 — Ancestralidade

Foi criado um teste específico para verificar se perguntas relacionadas à ancestralidade são classificadas corretamente.

Entrada:

```text
O que meu relatório diz sobre ancestralidade?
```

Resultado:

```text
TEMAS IDENTIFICADOS:
- ancestralidade genética
```

---

## Teste 4 — Atualização automática

Valida a inclusão de uma nova interação no histórico.

A pergunta:

```text
Isso significa que eu tenho a doença?
```

passa a gerar o tema:

```text
diferença entre predisposição genética e diagnóstico
```

demonstrando que o resumo pode evoluir à medida que novas interações são adicionadas.

---

# 16. Arquivo `integracao/agente_nlp.py`

O arquivo:

```text
sprint3/nlp/integracao/agente_nlp.py
```

é responsável por integrar os componentes desenvolvidos nesta Sprint com o agente especialista e o fluxo já existente.

A integração conecta:

```text
Agente Especialista / RAG
          ↓
Resposta técnica
          ↓
NLP
          ↓
Simplificação
          ↓
Métricas
          ↓
Histórico
          ↓
Resumo automático
```

O objetivo é demonstrar que os componentes de NLP não funcionam apenas isoladamente, mas podem participar do fluxo completo da aplicação.

---

# 17. Integração com o Agente Especialista

O agente especialista utilizado como base é responsável por orquestrar:

1. pergunta do usuário;
2. validação por guardrails;
3. contexto recuperado pelo RAG;
4. construção do prompt;
5. geração de uma resposta;
6. retorno das fontes utilizadas.

O contexto recuperado é organizado em blocos semelhantes a:

```text
[Fonte 1]
Trecho recuperado do relatório.

[Fonte 2]
Outro trecho relevante.
```

O prompt também estabelece que a resposta deve utilizar o contexto recuperado.

Caso a informação não esteja disponível no contexto, o agente deve informar que não encontrou a informação no relatório, evitando completar deliberadamente a resposta com informações não recuperadas.

---

# 18. Modos de Resposta

O agente prevê dois modos principais de comunicação.

## Modo paciente

Prioriza:

- linguagem simples;
- explicação de termos;
- menor quantidade de jargão;
- acessibilidade da informação.

## Modo técnico

Prioriza:

- maior detalhamento;
- precisão científica;
- preservação de terminologia especializada;
- explicação das limitações da interpretação genética.

O módulo de NLP desenvolvido nesta Sprint é especialmente relevante para o **modo paciente**.

---

# 19. Guardrails e Segurança

Antes da geração da resposta, a pergunta é submetida aos mecanismos de guardrails existentes no agente.

O fluxo segue:

```text
Pergunta
   ↓
verificar_guardrails()
   ↓
Permitida?
   ├── Não → resposta bloqueada
   └── Sim
        ↓
Contexto
        ↓
validar_contexto()
        ↓
Contexto válido?
   ├── Não → resposta de ausência de contexto
   └── Sim → processamento continua
```

Esse comportamento é importante porque o NLP não deve contornar as validações de segurança realizadas anteriormente.

A simplificação ocorre **depois que a resposta foi construída dentro do fluxo validado**.

---

# 20. Rastreamento das Fontes

O agente retorna também os trechos recuperados que foram utilizados como contexto.

A estrutura de retorno inclui informações como:

```python
{
    "status": "respondido",
    "categoria": "resposta_rag",
    "resposta": "...",
    "fontes": [...]
}
```

Isso contribui para a rastreabilidade do fluxo, permitindo manter a relação entre resposta e contexto recuperado.

---

# 21. Resultado da Integração

Nos testes de integração, a aplicação apresenta informações como:

```text
STATUS: respondido
MODO: paciente
```

e compara:

```text
RESPOSTA TÉCNICA ORIGINAL
```

com:

```text
RESPOSTA SIMPLIFICADA PARA O USUÁRIO
```

Exemplo:

### Resposta técnica

```text
O relatório identificou uma variante genética associada a uma
predisposição genética para determinada condição.
```

### Resposta simplificada

```text
O relatório identificou uma alteração no DNA ligada a uma chance
maior de desenvolver determinada condição.
```

---

# 22. Exemplo Completo de Simplificação

### Pergunta do usuário

```text
Meu resultado indica que eu tenho uma chance maior de desenvolver alguma condição?
```

### Resposta técnica original

```text
O relatório identificou uma variante genética associada a uma
predisposição genética para determinada condição.

Também foram avaliados marcadores genéticos presentes no DNA.

Esse resultado indica risco aumentado, mas não significa que
a pessoa necessariamente desenvolverá a condição.

O genótipo deve ser interpretado em conjunto com outros fatores,
como histórico familiar, hábitos de vida e acompanhamento profissional.

O resultado apresenta uma associação genética e não representa
um diagnóstico definitivo.
```

### Resposta simplificada

```text
O relatório identificou uma alteração no DNA ligada a uma chance maior
de desenvolver determinada condição.

Também foram analisadas características do DNA.

Esse resultado indica chance maior, mas não significa que a pessoa
terá essa condição.

Essas informações do DNA devem ser analisadas junto com outros fatores,
como histórico familiar, hábitos de vida e acompanhamento profissional.

O resultado mostra uma relação com fatores genéticos e não é um diagnóstico.
```

---

# 23. Integração com o Histórico

Após cada interação processada, a pergunta pode ser armazenada no histórico.

A partir desse histórico, o módulo de resumos identifica os temas e gera uma nova representação da conversa.

Exemplo de saída:

```text
RESUMO AUTOMÁTICO DAS INTERAÇÕES

O histórico possui 2 interações válidas. Os principais temas abordados
foram alterações e características encontradas no DNA, informações
analisadas no DNA e interpretação dos níveis de risco genético.

A dúvida mais recente do usuário foi:
"Pode explicar esse resultado de um jeito mais simples?"

TEMAS IDENTIFICADOS:
- alterações e características encontradas no DNA
- informações analisadas no DNA
- interpretação dos níveis de risco genético
```

---

# 24. Fluxo Técnico Completo

A integração desenvolvida pode ser representada de forma mais detalhada como:

```text
┌───────────────────────────┐
│     Pergunta do usuário   │
└─────────────┬─────────────┘
              ↓
┌───────────────────────────┐
│        Guardrails         │
│  validação da solicitação │
└─────────────┬─────────────┘
              ↓
┌───────────────────────────┐
│            RAG            │
│ recuperação de contexto   │
└─────────────┬─────────────┘
              ↓
┌───────────────────────────┐
│    Agente Especialista    │
│ construção da resposta    │
└─────────────┬─────────────┘
              ↓
┌───────────────────────────┐
│       Módulo de NLP       │
│ simplificação linguística │
└─────────────┬─────────────┘
              ↓
┌───────────────────────────┐
│ Métricas de legibilidade  │
│ original × simplificado   │
└─────────────┬─────────────┘
              ↓
┌───────────────────────────┐
│ Registro da interação     │
└─────────────┬─────────────┘
              ↓
┌───────────────────────────┐
│ Identificação de temas    │
└─────────────┬─────────────┘
              ↓
┌───────────────────────────┐
│ Atualização automática    │
│ do resumo das interações  │
└─────────────┬─────────────┘
              ↓
┌───────────────────────────┐
│       Resultado final     │
└───────────────────────────┘
```

---

# 25. Como Executar

Os comandos abaixo devem ser executados a partir da **raiz do repositório**.

## Testar a simplificação de linguagem

```bash
python sprint3/nlp/nlp_simplificacao.py
```

Esse teste apresenta:

- texto original;
- texto simplificado;
- métricas do texto original;
- métricas do texto simplificado.

---

## Testar os resumos automáticos

```bash
python sprint3/nlp/resumos_automaticos.py
```

O script executa cenários de teste relacionados a:

- resumo do relatório;
- resumo das interações;
- identificação de ancestralidade;
- atualização automática do histórico.

---

## Testar a integração completa

```bash
python sprint3/nlp/integracao/agente_nlp.py
```

Esse teste demonstra o fluxo integrado entre:

- agente;
- NLP;
- simplificação;
- métricas;
- histórico;
- resumo automático.

---

# 26. Dependências

Os módulos desenvolvidos utilizam principalmente recursos nativos do Python, incluindo:

```python
import json
import re
from pathlib import Path
```

Além disso, o arquivo de integração depende dos componentes do agente especialista já presentes no projeto.

As dependências gerais do projeto devem ser mantidas no arquivo:

```text
requirements.txt
```

localizado na raiz do repositório.

---

# 27. Decisões de Arquitetura

Durante o desenvolvimento, algumas decisões foram adotadas para melhorar a organização da solução.

## Separação de responsabilidades

A simplificação de linguagem e a geração de resumos foram mantidas em arquivos diferentes.

Isso permite:

- manutenção independente;
- testes isolados;
- reutilização das funções;
- integração mais simples;
- melhor organização do código.

---

## NLP como camada complementar

O NLP não substitui o agente especialista nem o RAG.

Ele complementa a arquitetura existente.

Essa decisão preserva a separação entre:

- **recuperação da informação**;
- **geração da resposta**;
- **adaptação da linguagem**.

---

## Preservação do texto original

O módulo mantém tanto o texto original quanto o texto simplificado.

Isso possibilita:

- comparação entre versões;
- cálculo das métricas;
- depuração;
- rastreabilidade;
- avaliação da transformação realizada.

---

## Histórico incremental

A atualização das interações foi implementada de forma incremental.

Uma nova pergunta pode ser adicionada ao histórico sem eliminar as anteriores, e o resumo é recalculado considerando o conjunto atualizado.

---

# 28. Tratamento de Casos Vazios

O módulo também considera situações nas quais não há dados suficientes para processamento.

Por exemplo, quando não existem interações:

```text
Ainda não existem interações para resumir.
```

Quando as interações não possuem perguntas válidas:

```text
Não foram encontradas perguntas válidas no histórico.
```

Na simplificação, textos vazios também são tratados antes do processamento.

Esse comportamento evita erros em chamadas com conteúdo ausente.

---

# 29. Cuidados com Informação Genética

Como o projeto trabalha com informações relacionadas à genética, a comunicação deve evitar transformar uma associação estatística ou genética em diagnóstico.

Por esse motivo, as respostas de teste reforçam distinções como:

```text
chance maior ≠ certeza de desenvolver a condição
```

e:

```text
associação genética ≠ diagnóstico
```

O módulo de NLP procura simplificar a linguagem sem remover essas diferenças conceituais.

---

# 30. Limitações da Implementação Atual

Apesar dos resultados obtidos, a implementação possui limitações que devem ser consideradas.

### Simplificação baseada em regras

Parte da simplificação depende de regras e expressões previamente definidas.

Consequentemente, termos não previstos podem permanecer no texto original.

### Métricas simples

As métricas implementadas avaliam características estruturais do texto, como comprimento médio das palavras e frases.

Elas não representam, sozinhas, uma avaliação completa da compreensão humana.

### Identificação de temas

A classificação dos temas utiliza regras definidas para o escopo do projeto.

Em uma aplicação de maior escala, essa etapa poderia utilizar modelos de classificação, embeddings ou outras técnicas de NLP.

### Resposta simulada do agente

Nos testes do agente especialista existe uma função de resposta simulada para permitir a execução sem dependência obrigatória de uma API externa.

Essa abordagem facilita os testes locais da integração.

Em uma aplicação produtiva, essa função pode ser substituída pela chamada ao modelo de linguagem adotado pelo projeto.

---

# 31. Possíveis Evoluções

A arquitetura permite futuras extensões, como:

- utilização de modelos de linguagem para simplificação contextual;
- classificação automática de temas por embeddings;
- aplicação de índices formais de legibilidade;
- personalização do nível de linguagem;
- expansão do vocabulário técnico;
- avaliação automática de preservação semântica;
- armazenamento persistente do histórico;
- integração com interface conversacional;
- comparação automática entre resposta técnica e resposta simplificada;
- testes automatizados para diferentes perfis de perguntas;
- geração de resumos progressivos para conversas extensas.

---

# 32. Critérios Considerados na Implementação

O desenvolvimento priorizou:

**Clareza**  
A informação deve ser compreensível para usuários não especialistas.

**Precisão**  
A simplificação não deve transformar uma possibilidade genética em diagnóstico.

**Coerência**  
As frases produzidas devem permanecer gramaticalmente e semanticamente adequadas.

**Rastreabilidade**  
O fluxo mantém relação com o contexto recuperado pelo agente.

**Modularidade**  
Cada arquivo possui responsabilidade definida.

**Reutilização**  
As funções podem ser utilizadas individualmente ou por meio da integração.

**Segurança**  
O NLP respeita as validações realizadas pelos guardrails.

---

# 33. Resultado Final da Sprint 3 — NLP

A implementação realizada neste módulo adiciona ao Genera AI uma camada de processamento voltada à **compreensão e organização das informações apresentadas ao usuário**.

Ao final do desenvolvimento, o módulo é capaz de:

- [x] receber textos técnicos;
- [x] identificar termos genéticos definidos no módulo;
- [x] produzir versões mais acessíveis;
- [x] preservar informações essenciais;
- [x] calcular métricas do texto;
- [x] carregar dados estruturados do relatório;
- [x] gerar resumos automáticos;
- [x] resumir históricos de interação;
- [x] identificar temas das perguntas;
- [x] tratar singular e plural nas saídas;
- [x] identificar a pergunta mais recente;
- [x] atualizar automaticamente o resumo após novas interações;
- [x] integrar o NLP ao agente especialista;
- [x] preservar o fluxo de guardrails;
- [x] utilizar o contexto recuperado pelo RAG;
- [x] manter rastreabilidade das fontes;
- [x] executar testes independentes e integrados.

---

# 34. Conclusão

O módulo de NLP desenvolvido na Sprint 3 amplia a capacidade do **Genera AI** ao atuar sobre um problema essencial em aplicações de inteligência artificial aplicadas a informações técnicas: **não basta recuperar uma informação correta; é necessário apresentá-la de forma compreensível ao usuário**.

A solução implementada estabelece uma camada intermediária entre a resposta técnica produzida pelo sistema e sua apresentação final.

Essa camada combina:

> **simplificação de linguagem + métricas + resumos automáticos + histórico de interações + integração com o agente**

A arquitetura também mantém compatibilidade com os componentes desenvolvidos anteriormente, especialmente o **agente especialista, os guardrails e o mecanismo de RAG**.

Com isso, a Sprint 3 não cria apenas funções isoladas de processamento textual, mas integra o NLP ao fluxo existente do projeto, preparando a solução para evoluções futuras e para uma experiência conversacional mais clara, organizada e acessível.

---

## Estrutura resumida

```text
Genera AI
│
├── RAG
│   └── recupera informações relevantes
│
├── Guardrails
│   └── valida perguntas e contexto
│
├── Agente Especialista
│   └── organiza e produz a resposta
│
└── NLP — Sprint 3
    │
    ├── Simplificação de linguagem
    ├── Métricas de texto
    ├── Resumos automáticos
    ├── Identificação de temas
    ├── Histórico de interações
    └── Integração com o agente
```

---

**Projeto:** Genera AI  
**Challenge:** DASA  
**Sprint:** 3  
**Módulo:** Processamento de Linguagem Natural — NLP  
**Diretório:** `sprint3/nlp/`
