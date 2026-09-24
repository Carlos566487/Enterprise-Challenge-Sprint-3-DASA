# Extrator PDF → JSON — Sprint 1

Fecha a única etapa do pipeline que existia apenas em documentação: transformar o
relatório genético em PDF no `dados_estruturados.json` que alimenta a busca
semântica, o agente e as interfaces.

---

## Como rodar

```bash
# o PDF não é versionado — regenere primeiro (ver sprint1/README_dados_simulados.md)
pip install reportlab
cd sprint1 && python gerar_pdf.py && cd ..

# extrair
python sprint1/extracao/extrair_pdf.py sprint1/relatorio_genera_simulado.pdf saida.json
```

Gera `saida.json` com os dados e `saida.avisos.json` com a lista de campos não
extraídos e o motivo de cada um.

Como biblioteca:

```python
from sprint1.extracao import extrair_relatorio

resultado = extrair_relatorio("sprint1/relatorio_genera_simulado.pdf")
resultado["dados"]   # dict no schema do projeto
resultado["avisos"]  # [{"campo": ..., "motivo": ...}]
```

---

## Estratégia de parsing por seção

| Seção | Fonte | Estratégia |
|---|---|---|
| Cabeçalho | texto | O PDF imprime **dois pares `Rótulo: valor` por linha**. O parser localiza as posições de todos os rótulos conhecidos e recorta o texto entre eles. `Médico Solicitante` é dividido em nome + CRM por regex de formato. Datas `DD/MM/AAAA` → ISO. |
| Sumário | tabela + texto | Contagens da tabela, mapeadas **pelo texto do cabeçalho de cada coluna**, não por posição fixa. Plataforma e cobertura por regex sobre a prosa. `Aviso Legal:` até o próximo título de seção. |
| Resultados | **texto** | Blocos delimitados por subtítulo numerado (`2.1`, `2.2`…). Dentro do bloco, a linha seguinte a `Nível de Risco` traz risco + categoria + marcadores. Parágrafos delimitados por `Descrição Técnica:` e `Recomendação Clínica:`. Percentil por regex `percentil (\d+)`. |
| Ancestralidade | tabela | Tabela de 3 colunas; percentuais em notação brasileira (`42,3%` → `42.3`). |
| Metodologia | tabela + texto | Tabela de etapas + regex para plataforma, cobertura e genoma de referência. |
| Rodapé | texto | Responsável, CRM, especialidade, laboratório, CNES, endereço, versão e data de emissão. |

### Por que os resultados vêm do texto e não da tabela

`extract_tables()` **trunca** a célula de marcadores no limite visual da coluna,
devolvendo `"alelo T"` no lugar de `"alelo T/T | RS12255372 (TCF7L2) — alelo T/G |
RS1801282 (PPARG) — alelo C/G"`. O `extract_text()` preserva a linha inteira. Por
isso a seção de resultados é parseada a partir do texto, enquanto ancestralidade e
metodologia — cujas tabelas extraem limpas — usam `extract_tables()`.

### Nada é inventado

Campo não encontrado sai como `None` e gera um aviso estruturado. O extrator nunca
preenche lacuna com valor plausível: um JSON visivelmente incompleto é melhor que
um silenciosamente errado.

---

## Validação contra o oráculo

O `dados_estruturados.json` foi produzido à mão na Sprint 1 a partir deste mesmo
PDF, o que o torna um oráculo objetivo. Resultado da comparação campo a campo:

| Classificação | Campos | |
|---|---:|---|
| **Exatos** | **155** | valor idêntico ao oráculo |
| Não extraíveis | 55 | conteúdo redigido fora do PDF |
| Divergentes | 17 | valor presente nos dois, mas diferente |
| **Total comparado** | **227** | |

**Precisão sobre o que de fato existe no PDF: 90,1 % (155 de 172).**

### As 17 divergências, uma a uma

| Qtd | Campo | Causa |
|---:|---|---|
| 7 | `descricao_tecnica` | O oráculo é uma **condensação humana** da prosa do PDF. Ex.: o PDF diz *"A análise identificou homozigose… do gene TCF7L2 (Transcription Factor 7-Like 2), variante com odds ratio…"*; o oráculo, *"Homozigose… do gene TCF7L2 (odds ratio…)"*. A extração devolve o texto do documento. |
| 4 | `recomendacao` | Mesma causa: reescrita editorial no oráculo. |
| 4 | `parametro_qualidade` | Duas por **corrupção de fonte** (ver abaixo) e duas por separador decimal — o oráculo normalizou `0,3` para `0.3`, a extração preserva a vírgula impressa. |
| 1 | `aviso_legal` | O oráculo **truncou** o parágrafo após a segunda frase; o PDF traz uma terceira. A extração é o superconjunto. |
| 1 | `alelo` (APOE) | Corrupção de fonte: `ε3/ε4` → `e3/e4`. |

### Corrupções de codepoint no PDF

A fonte embutida mapeia alguns símbolos para codepoints errados na extração:

| Extraído | Real | Reparado? |
|---|---|---|
| `‡` | `≥` | **Sim** — mapa de caractere, sem inferir valor |
| `ng/mL` | `ng/μL` | **Não** — exigiria adivinhar que o `m` era `μ` |
| `1×10nn` | `1×10⁻⁶` | **Não** — o expoente se perdeu na extração |
| `e3/e4` | `ε3/ε4` | **Não** — o épsilon não sobrevive à extração |

Reparar os três últimos exigiria conhecer o valor esperado, ou seja, copiar do
oráculo. Preferimos a divergência documentada.

### Campos que o PDF não contém

Os 55 campos "não extraíveis" foram redigidos depois da extração, por LLM ou por
pessoa: `descricao_simples`, `impacto_pratico`, `urgencia_medica`,
`relevancia_medico`, `fontes` (citações bibliográficas),
`marcadores[].observacao`, e no sumário `resumo_executivo_paciente`,
`principais_riscos_medico` e `recomendacoes_prioritarias`.

Dois casos merecem nota: o `escore_poligênico_percentil` das condições **2.6 e
2.7** existe no oráculo (12 e 35) e **não aparece em lugar nenhum do PDF** —
foram acrescentados à mão. O extrator devolve `None`, que é o comportamento
correto.

---

## Testes

```bash
pytest sprint1/extracao/ -v      # 31 testes
```

- **Parsing e robustez** (24 testes) usam fixtures **sintéticos** — identificadores
  inventados como `RS0000001 (GENEX)`, nunca valores do relatório. Rodam sempre,
  inclusive no CI em clone limpo, e provam que o parser é genérico.
- **Oráculo** (7 testes) precisam do PDF. A fixture usa o arquivo do disco; se não
  houver, tenta gerá-lo com `sprint1/gerar_pdf.py`; se `reportlab` não estiver
  instalado, **pula com mensagem explícita**. Nunca falham por ausência do insumo.

Robustez coberta: arquivo inexistente, diretório no lugar de arquivo, arquivo que
não é PDF, e PDF corrompido — todos levantam `ErroExtracao` com mensagem acionável.

---

## Limitações

**Este extrator foi desenvolvido e validado para o layout do relatório Genera
simulado.** Ele não é um extrator genérico de relatórios genéticos.

Depende de:

- rótulos impressos exatos (`Paciente:`, `Descrição Técnica:`, `Aviso Legal:`…);
- subtítulos de condição no formato `N.N Nome da Condição`;
- marcadores no formato `RS#### (GENE) — alelo X/Y`, separados por `|`;
- cabeçalhos de tabela com os textos usados como chave de busca;
- datas em `DD/MM/AAAA` e decimais com vírgula.

Outro laboratório, outro layout, ou uma mudança de template do próprio Genera
exigiriam ajuste dos parsers. O teste `test_nenhuma_falha_de_extracao` existe
justamente para quebrar de forma visível quando isso acontecer, em vez de produzir
um JSON silenciosamente incompleto.

**Não faz OCR.** O relatório é um PDF nativo. Um documento digitalizado levanta
`ErroExtracao` com mensagem explícita em vez de tentar adivinhar.
