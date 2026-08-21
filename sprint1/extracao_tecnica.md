# Definição da Técnica de Extração de Dados — PDF → Estruturado

---

## 1. O que é Extração de Texto de PDF

Extração de texto de PDF é o processo de recuperar o conteúdo textual e estrutural de um arquivo PDF de forma programática, transformando um documento visual em dados manipuláveis por código.

Um PDF não armazena texto como um arquivo `.txt` — ele armazena instruções de renderização (posição, fonte, tamanho de cada caractere na página). Por isso, extrair texto de PDF exige ferramentas especializadas que interpretam essas instruções e reconstroem o fluxo de leitura.

---

## 2. Tipos de PDF: Nativo vs. Escaneado

### PDF Nativo (texto selecionável)

- O texto está embutido no arquivo como dados vetoriais
- É possível selecionar, copiar e pesquisar o texto diretamente no leitor
- Gerado por softwares como Word, LaTeX, ReportLab, sistemas hospitalares digitais
- **Extração direta:** bibliotecas como PyMuPDF e pdfplumber conseguem extrair o texto com alta fidelidade

**Exemplo:** O `relatorio_genera_simulado.pdf` deste projeto é um PDF nativo.

### PDF Escaneado (imagem)

- O documento é uma fotografia ou digitalização de papel impresso
- Não há texto embutido — apenas pixels
- Comum em documentos antigos, receitas médicas físicas, laudos impressos digitalizados
- **Extração via OCR:** é necessário usar Reconhecimento Óptico de Caracteres (OCR) para "ler" a imagem e converter em texto

### Comparativo

| Característica              | PDF Nativo           | PDF Escaneado                             |
| --------------------------- | -------------------- | ----------------------------------------- |
| Texto selecionável          | Sim                  | Não                                       |
| Qualidade da extração       | Alta                 | Variável (depende da qualidade da imagem) |
| Ferramenta necessária       | PyMuPDF / pdfplumber | Tesseract OCR + pdf2image                 |
| Velocidade de processamento | Rápida               | Lenta                                     |
| Sensibilidade a ruídos      | Baixa                | Alta                                      |
| Custo computacional         | Baixo                | Alto                                      |

---

## 3. Ferramentas Disponíveis

### PyMuPDF (fitz)

- Biblioteca Python baseada na engine MuPDF
- Extrai texto, imagens, tabelas e metadados com alta performance
- Suporta extração por bloco, linha e caractere individual
- Mantém informações de posição (coordenadas x, y) — útil para identificar colunas de tabelas
- **Instalação:** `pip install pymupdf`

```python
import fitz  # PyMuPDF
doc = fitz.open("relatorio_genera_simulado.pdf")
for page in doc:
    texto = page.get_text("text")
    print(texto)
```

### pdfplumber

- Construído sobre pdfminer, com foco em extração de tabelas
- Excelente para PDFs com tabelas complexas — detecta bordas e células automaticamente
- API intuitiva para extrair tabelas como listas de listas
- **Instalação:** `pip install pdfplumber`

```python
import pdfplumber
with pdfplumber.open("relatorio_genera_simulado.pdf") as pdf:
    for page in pdf.pages:
        tabelas = page.extract_tables()
        texto = page.extract_text()
```

### pdfminer.six

- Biblioteca de baixo nível para análise detalhada de PDFs
- Oferece controle granular sobre o layout (LTPage, LTTextBox, LTChar)
- Mais verbosa e complexa de usar, mas poderosa para casos específicos
- Base sobre a qual o pdfplumber é construído
- **Instalação:** `pip install pdfminer.six`

### Tesseract OCR

- Motor de OCR open-source mantido pelo Google
- Necessário para PDFs escaneados (imagens)
- Usado em conjunto com `pdf2image` (converte páginas do PDF em imagens) e `pytesseract` (wrapper Python)
- Suporta mais de 100 idiomas, incluindo português
- **Instalação:** requer instalação do binário Tesseract + `pip install pytesseract pdf2image`

```python
from pdf2image import convert_from_path
import pytesseract

imagens = convert_from_path("relatorio_escaneado.pdf")
for img in imagens:
    texto = pytesseract.image_to_string(img, lang='por')
```

---

## 4. Ferramenta Escolhida para Este Projeto

### Escolha: **pdfplumber** (extração principal) + **PyMuPDF** (fallback e metadados)

### Justificativa

O relatório Genera é um **PDF nativo** gerado por sistemas digitais do laboratório. Portanto, OCR não é necessário na maioria dos casos.

A escolha do **pdfplumber** como ferramenta principal se justifica por:

1. **Extração de tabelas superior:** O relatório Genera contém múltiplas tabelas (dados do paciente, sumário, resultados por condição, ancestralidade, metodologia). O pdfplumber detecta e extrai tabelas como estruturas de dados diretamente, sem necessidade de parsing manual de texto posicional.

2. **Integração com pandas:** As tabelas extraídas podem ser convertidas diretamente em DataFrames, facilitando a limpeza e transformação dos dados.

3. **Manutenção ativa e documentação clara:** Biblioteca amplamente usada em projetos de ciência de dados com saúde no Brasil.

O **PyMuPDF** é usado como complemento para:

- Extração de metadados do documento (autor, data de criação, versão)
- Extração de texto de seções sem tabela (descrições técnicas, recomendações)
- Fallback quando o pdfplumber não detecta corretamente o layout

Para relatórios escaneados (caso o paciente envie uma foto ou scan do PDF impresso), o pipeline inclui uma etapa de **detecção automática**: se `pdfplumber` retornar texto vazio ou com menos de 100 caracteres por página, o sistema ativa automaticamente o pipeline OCR com Tesseract.

---

## 5. Processo de Limpeza do Texto Extraído

Após a extração bruta, o texto passa por um pipeline de limpeza antes de ser estruturado em JSON.

### 5.1 Problemas Comuns no Texto Bruto

```
# Exemplo de texto bruto extraído (com ruídos):
"DASA | GENERA\nRelatório de Análise Genômica Personalizada\n\n\nPaciente:\nCarlos Eduardo Mendes\n
ID Relatório:\nGEN-2024-00847\n\n2.1 Diabetes Mellitus Tipo 2\nNível de Risco\nCategoria\n
Marcadores Principais\nALTO\nMetabolismo e Endocrinologia\nRS7903146 (TCF7L2) — alelo T/T | ...\n
Página 1 de 4\n\nDASA | GENERA\nRelatório de Análise Genômica..."
```

### 5.2 Etapas de Limpeza

| Etapa                                | Problema                                                | Solução                                             |
| ------------------------------------ | ------------------------------------------------------- | --------------------------------------------------- |
| Remoção de cabeçalhos repetidos      | "DASA \| GENERA" aparece no topo de cada página         | Detectar padrão e remover duplicatas                |
| Remoção de rodapés                   | "Página X de Y", dados do laboratório repetidos         | Regex: `r'Página \d+ de \d+'`                       |
| Normalização de quebras de linha     | `\n\n\n` excessivos entre seções                        | Substituir múltiplos `\n` por separador único       |
| Limpeza de espaços                   | Espaços duplos, tabulações irregulares                  | `re.sub(r'\s+', ' ', texto)`                        |
| Normalização de caracteres especiais | `ε`, `μ`, `≥`, `×` podem virar `?` em encodings errados | Forçar UTF-8 na leitura; mapeamento de substituição |
| Separação de marcadores genéticos    | `RS7903146 (TCF7L2) — alelo T/T \| RS12255372...`       | Split por `\|` e strip de espaços                   |
| Normalização de percentuais          | `42,3%` (vírgula decimal BR)                            | Substituir `,` por `.` em contexto numérico         |
| Identificação de seções              | Subtítulos como `2.1`, `2.2`                            | Regex: `r'^\d+\.\d+\s+[A-Z]'`                       |

### 5.3 Pseudocódigo do Pipeline de Limpeza

```python
import re
import pdfplumber

def extrair_e_limpar(caminho_pdf: str) -> dict:
    with pdfplumber.open(caminho_pdf) as pdf:
        paginas_texto = []
        paginas_tabelas = []

        for page in pdf.pages:
            # Extração
            texto_bruto = page.extract_text() or ""
            tabelas = page.extract_tables() or []

            # Limpeza do texto
            texto = remover_cabecalho_rodape(texto_bruto)
            texto = re.sub(r'\n{3,}', '\n\n', texto)       # quebras excessivas
            texto = re.sub(r'[ \t]{2,}', ' ', texto)        # espaços duplos
            texto = texto.strip()

            paginas_texto.append(texto)
            paginas_tabelas.append(tabelas)

    return estruturar_dados(paginas_texto, paginas_tabelas)

def remover_cabecalho_rodape(texto: str) -> str:
    # Remove cabeçalho repetido
    texto = re.sub(r'DASA \| GENERA\n.*?\n', '', texto)
    # Remove numeração de página
    texto = re.sub(r'Página \d+ de \d+', '', texto)
    return texto
```

---

## 6. Diagrama do Pipeline de Extração

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENTRADA                                  │
│              Upload do PDF pelo usuário                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DETECÇÃO DO TIPO DE PDF                       │
│   pdfplumber tenta extrair texto                                │
│   ├── texto encontrado (> 100 chars/página) → PDF NATIVO        │
│   └── texto vazio ou insuficiente → PDF ESCANEADO               │
└──────────┬──────────────────────────────┬───────────────────────┘
           │ PDF Nativo                   │ PDF Escaneado
           ▼                             ▼
┌──────────────────────┐    ┌────────────────────────────────────┐
│  pdfplumber          │    │  pdf2image → imagens por página    │
│  + PyMuPDF           │    │  Tesseract OCR (lang=por)          │
│  Extração direta     │    │  Texto bruto com possíveis ruídos  │
└──────────┬───────────┘    └──────────────┬─────────────────────┘
           │                               │
           └───────────────┬───────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LIMPEZA DO TEXTO                            │
│  • Remoção de cabeçalhos/rodapés repetidos                      │
│  • Normalização de quebras de linha e espaços                   │
│  • Tratamento de caracteres especiais (UTF-8)                   │
│  • Separação de marcadores genéticos                            │
│  • Normalização de percentuais (vírgula → ponto)                │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   IDENTIFICAÇÃO DE SEÇÕES                       │
│  • Regex para detectar subtítulos numerados (2.1, 2.2...)       │
│  • Separação de blocos: paciente, sumário, resultados,          │
│    ancestralidade, metodologia, rodapé                          │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ESTRUTURAÇÃO EM JSON                          │
│  • Mapeamento campo a campo                                     │
│  • Validação de tipos (string, number, array)                   │
│  • Geração do arquivo dados_estruturados.json                   │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SAÍDA PARA A IA                              │
│  JSON estruturado → LLM / RAG pipeline                          │
└─────────────────────────────────────────────────────────────────┘
```
