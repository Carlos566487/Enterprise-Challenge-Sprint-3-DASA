# Dados Simulados da Sprint 1 — Como Regenerar

Este documento explica por que o relatório em PDF **não é versionado** e como
qualquer integrante ou avaliador o regenera localmente em segundos.

---

## Por que o PDF não está no repositório

O `.gitignore` do projeto declara, na primeira regra:

```
# Arquivos PDF — política de privacidade: PDFs podem conter dados genéticos reais
# ou simulados. Nenhum PDF deve ser versionado.
*.pdf
```

O relatório usado no projeto é **sintético** — nenhum dado de pessoa real —, mas a
política vale para o formato, não para o conteúdo: um repositório que aceita PDF
versionado hoje aceita o PDF errado amanhã. Manter a regra sem exceções é o que
a torna verificável.

O efeito colateral seria perder a demonstrabilidade do pipeline, já que o PDF é o
insumo da etapa de extração. É isso que este gerador resolve: **o dado sintético
é produzido localmente, não distribuído**.

---

## Como regenerar

```bash
pip install reportlab          # dependência apenas deste gerador
cd sprint1
python gerar_pdf.py            # escreve relatorio_genera_simulado.pdf no diretório atual
```

Saída esperada:

```
PDF gerado com sucesso: relatorio_genera_simulado.pdf
```

O arquivo cai no diretório de onde o comando foi executado. Para colocá-lo onde o
restante do projeto espera, rode a partir de `sprint1/`.

> `reportlab` **não** está no `requirements.txt`: é necessário só para regenerar o
> dado de teste, não para rodar a aplicação. Quem apenas executa o dashboard não
> precisa dele.

---

## Equivalência verificada

O PDF regenerado é equivalente ao que foi usado durante todo o desenvolvimento.
Comparação feita em 21/08/2026, com `reportlab 4.4.10`:

| Métrica | Resultado |
|---|---|
| Páginas | 5 = 5 |
| Tabelas detectadas por `pdfplumber` | 10 = 10 |
| Caracteres de texto extraído | 9.513 = 9.513 |
| SHA-256 do texto extraído | **idêntico** |
| JSON produzido pelo extrator | **idêntico** (hash `99607f9f619d722e`) |

O tamanho em bytes difere levemente (13.840 vs 14.002) porque o PDF carrega
metadados de criação e a versão do `reportlab` varia — o conteúdo extraível, que é
o que o pipeline consome, é bit a bit o mesmo.

---

## Proveniência

`gerar_pdf.py` foi escrito na Sprint 1 (commit `d3f8387`) para produzir o relatório
simulado, e removido do repositório em `3db3b98` por ser considerado desnecessário
na época. Foi restaurado quando ficou claro que ele é justamente o que permite
manter a política de privacidade **e** a reprodutibilidade ao mesmo tempo.

O conteúdo do relatório — paciente, condições, marcadores, ancestralidade — é
inteiramente fictício, criado para exercitar o pipeline de extração.
