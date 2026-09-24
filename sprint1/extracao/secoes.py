"""
Parsers por seção do relatório Genera — Sprint 1 / Genera AI / Dasa

Cada função recebe o conteúdo já extraído do PDF (texto e/ou tabelas) e devolve
uma tupla `(dados, avisos)`. Nenhuma delas inventa valor: quando um campo não é
encontrado, o campo sai como None e um aviso estruturado é registrado.

Princípio de projeto
────────────────────────────────────────────────────────────────────────────
O código conhece apenas a ESTRUTURA do documento — rótulos impressos
("Paciente:", "Descrição Técnica:"), cabeçalhos de tabela e formatos
(datas, percentuais, identificadores de SNP). Nenhum valor do relatório
(nome do paciente, doenças, genes, percentis, textos clínicos) aparece
neste arquivo.
"""

import re
import unicodedata

# ── Rótulos impressos no cabeçalho do relatório ──────────────────────────────
ROTULOS_CABECALHO = [
    "Paciente",
    "ID Relatório",
    "Data de Nascimento",
    "Data do Exame",
    "CPF",
    "Data de Emissão",
    "Médico Solicitante",
    "Laboratório",
]

# Classificações de risco impressas na tabela de cada condição.
NIVEIS_RISCO = ["ALTO", "MÉDIO", "BAIXO"]

# Rótulos que delimitam os parágrafos de cada condição.
ROTULO_DESCRICAO = "Descrição Técnica:"
ROTULO_RECOMENDACAO = "Recomendação Clínica:"
ROTULO_AVISO = "Aviso Legal:"
ROTULO_RESPONSAVEL = "Responsável Técnico:"
ROTULO_CNES = "CNES:"
ROTULO_VERSAO = "Versão do relatório:"
ROTULO_EMISSAO = "Emitido em:"
ROTULO_ESPECIALISTA = "Especialista em "

# Cabeçalho da tabela que precede a linha de dados de cada condição.
CABECALHO_TABELA_CONDICAO = "Nível de Risco"

# ── Reparo de codepoints corrompidos na extração ─────────────────────────────
# A fonte embutida no PDF mapeia alguns símbolos para codepoints errados.
# Isto repara o CARACTERE, não o valor: nenhum dado do relatório é inferido.
# Ver "Limitações" no README — repairs que exigiriam adivinhar o valor
# (μ virando m, expoente perdido) NÃO são feitos de propósito.
REPAROS_CODEPOINT = {
    "‡": "≥",  # ‡ renderizado no lugar de ≥
}

RE_DATA_BR = re.compile(r"\b(\d{2})/(\d{2})/(\d{4})\b")
RE_CRM = re.compile(r"\bCRM/[A-Z]{2}\s*\d+\b")
RE_SNP = re.compile(r"^(RS\d+)\s*\(([^)]+)\)\s*[—-]\s*(.+)$", re.IGNORECASE)
RE_INICIO_CONDICAO = re.compile(r"^(\d\.\d)\s+(.+)$")
RE_PERCENTIL = re.compile(r"percentil\s+(\d+)", re.IGNORECASE)
RE_NUMERO_BR = re.compile(r"^-?\d{1,3}(?:\.\d{3})*(?:,\d+)?$")
RE_PERCENTUAL = re.compile(r"^(-?[\d.,]+)\s*%$")
RE_PLATAFORMA_SUMARIO = re.compile(
    r"plataforma de genotipagem[^(]*\(([^,]+),\s*cobertura de ([\d.]+)\s*SNPs\)",
    re.IGNORECASE,
)
RE_PLATAFORMA_METODO = re.compile(
    r"plataforma de genotipagem\s+(.+?),\s*com\s*\n?\s*cobertura de\s+([\d.]+)",
    re.IGNORECASE,
)
RE_GENOMA = re.compile(r"genoma humano\s*\(([^)]+)\)", re.IGNORECASE)
RE_PARENTESE_FINAL = re.compile(r"\s*\([^)]*\)\s*$")


def reparar_codepoints(texto: str) -> str:
    """Aplica os reparos de caractere conhecidos e normaliza para NFC."""
    if not texto:
        return texto
    for errado, certo in REPAROS_CODEPOINT.items():
        texto = texto.replace(errado, certo)
    return unicodedata.normalize("NFC", texto)


def _limpar(texto: str) -> str:
    """Colapsa espaços e quebras de linha em espaço único."""
    if texto is None:
        return None
    return re.sub(r"\s+", " ", texto).strip()


def data_iso(texto: str):
    """Converte DD/MM/AAAA para AAAA-MM-DD. Devolve None se não casar."""
    if not texto:
        return None
    m = RE_DATA_BR.search(texto)
    if not m:
        return None
    dia, mes, ano = m.groups()
    return f"{ano}-{mes}-{dia}"


def numero_br(texto: str):
    """
    Converte número em notação brasileira para int ou float.

    '1.234' -> 1234   |   '9,5' -> 9.5   |   inválido -> None
    """
    if texto is None:
        return None
    bruto = texto.strip()
    if not RE_NUMERO_BR.match(bruto):
        return None
    normalizado = bruto.replace(".", "").replace(",", ".")
    valor = float(normalizado)
    return int(valor) if valor.is_integer() and "," not in bruto else valor


def percentual_br(texto: str):
    """Converte '9,5%' para 9.5. Devolve None se não casar."""
    if not texto:
        return None
    m = RE_PERCENTUAL.match(texto.strip())
    if not m:
        return None
    return numero_br(m.group(1))


# ─────────────────────────────────────────────────────────────────────────────
# SEÇÃO 0 — CABEÇALHO / IDENTIFICAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def _pares_rotulo_valor(linhas: list) -> dict:
    """
    Extrai pares 'Rótulo: valor' de linhas que contêm DOIS pares cada.

    O PDF imprime duas colunas por linha, por exemplo:
        Paciente: <nome>   ID Relatório: <id>
    A associação é feita localizando as posições de todos os rótulos
    conhecidos na linha e recortando o texto entre eles.
    """
    padrao = re.compile(
        r"(" + "|".join(re.escape(r) for r in ROTULOS_CABECALHO) + r")\s*:\s*"
    )
    encontrados = {}
    for linha in linhas:
        marcas = list(padrao.finditer(linha))
        for i, marca in enumerate(marcas):
            fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(linha)
            valor = _limpar(linha[marca.end():fim])
            if valor:
                encontrados[marca.group(1)] = valor
    return encontrados


def parse_cabecalho(texto: str):
    """Extrai os dados de identificação do paciente e do relatório."""
    avisos = []
    campos = _pares_rotulo_valor(texto.split("\n"))

    medico_bruto = campos.get("Médico Solicitante")
    medico = crm = None
    if medico_bruto:
        m = RE_CRM.search(medico_bruto)
        if m:
            crm = _limpar(m.group(0))
            medico = _limpar(medico_bruto[:m.start()])
        else:
            medico = medico_bruto
            avisos.append({
                "campo": "paciente.crm_medico",
                "motivo": "CRM não encontrado no valor de 'Médico Solicitante'",
            })

    dados = {
        "nome": campos.get("Paciente"),
        "data_nascimento": data_iso(campos.get("Data de Nascimento")),
        "cpf": campos.get("CPF"),
        "id_relatorio": campos.get("ID Relatório"),
        "data_exame": data_iso(campos.get("Data do Exame")),
        "data_emissao": data_iso(campos.get("Data de Emissão")),
        "medico_solicitante": medico,
        "crm_medico": crm,
    }

    for chave, valor in dados.items():
        if valor is None and chave != "crm_medico":
            avisos.append({
                "campo": f"paciente.{chave}",
                "motivo": "rótulo não encontrado no cabeçalho do PDF",
            })
    return dados, avisos


# ─────────────────────────────────────────────────────────────────────────────
# SEÇÃO 1 — SUMÁRIO EXECUTIVO
# ─────────────────────────────────────────────────────────────────────────────

# Cabeçalhos da tabela de contagens -> chave de saída.
COLUNAS_SUMARIO = {
    "Condições Analisadas": "total_condicoes_analisadas",
    "Risco Alto": "condicoes_alto_risco",
    "Risco Médio": "condicoes_medio_risco",
    "Risco Baixo": "condicoes_baixo_risco",
    "Cobertura Genômica": "cobertura_genomica_snps",
}


def parse_sumario(texto: str, tabelas: list):
    """
    Extrai as contagens consolidadas, a plataforma e o aviso legal.

    As contagens vêm da tabela de resumo, mapeadas pelo texto do cabeçalho de
    cada coluna — não por posição fixa.
    """
    avisos = []
    dados = {chave: None for chave in COLUNAS_SUMARIO.values()}
    dados["plataforma_genotipagem"] = None
    dados["aviso_legal"] = None

    tabela = _achar_tabela(tabelas, list(COLUNAS_SUMARIO)[0])
    if tabela and len(tabela) >= 2:
        cabecalho, linha = tabela[0], tabela[1]
        for titulo, valor in zip(cabecalho, linha):
            chave = COLUNAS_SUMARIO.get(_limpar(titulo))
            if chave:
                dados[chave] = numero_br(_limpar(valor).split()[0]) if valor else None
    else:
        avisos.append({
            "campo": "sumario.contagens",
            "motivo": "tabela de resumo não localizada no PDF",
        })

    m = RE_PLATAFORMA_SUMARIO.search(texto)
    if m:
        dados["plataforma_genotipagem"] = _limpar(m.group(1))
        if dados["cobertura_genomica_snps"] is None:
            dados["cobertura_genomica_snps"] = numero_br(m.group(2))
    else:
        avisos.append({
            "campo": "sumario.plataforma_genotipagem",
            "motivo": "trecho de plataforma/cobertura não encontrado no texto",
        })

    aviso = _texto_apos_rotulo(texto, ROTULO_AVISO)
    if aviso:
        dados["aviso_legal"] = aviso
    else:
        avisos.append({
            "campo": "sumario.aviso_legal",
            "motivo": f"rótulo '{ROTULO_AVISO}' não encontrado",
        })

    return dados, avisos


# Título de seção de topo do relatório ("1. SUMÁRIO EXECUTIVO", "2. RESULTADOS...").
RE_SECAO_TOPO = re.compile(r"^\d+\.\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ]", re.MULTILINE)


def _texto_apos_rotulo(texto: str, rotulo: str):
    """
    Devolve o parágrafo que segue um rótulo, parando no próximo título de seção.

    Sem esse limite o parágrafo se estenderia até o fim do documento, já que as
    páginas são concatenadas e não há linha em branco separando as seções.
    """
    idx = texto.find(rotulo)
    if idx < 0:
        return None
    inicio = idx + len(rotulo)
    proxima = RE_SECAO_TOPO.search(texto, inicio)
    fim = proxima.start() if proxima else len(texto)
    return _limpar(texto[inicio:fim])


def _achar_tabela(tabelas: list, titulo_primeira_coluna: str):
    """Localiza a tabela cujo cabeçalho começa com o título informado."""
    for tabela in tabelas:
        if not tabela or not tabela[0]:
            continue
        primeira = _limpar(tabela[0][0] or "")
        if primeira.startswith(titulo_primeira_coluna):
            return tabela
    return None


# ─────────────────────────────────────────────────────────────────────────────
# SEÇÃO 2 — RESULTADOS DAS ANÁLISES GENÉTICAS
# ─────────────────────────────────────────────────────────────────────────────

def _parse_marcador(fragmento: str):
    """
    Converte 'RS#### (GENE) — alelo X/Y' no dict de marcador.

    Regras derivadas do formato impresso:
      • o gene é o conteúdo dos parênteses, cortado no travessão quando o PDF
        acrescenta o nome extenso;
      • o alelo é o que segue o travessão, sem o prefixo 'alelo' e sem o
        parêntese qualificador final.
    """
    m = RE_SNP.match(fragmento.strip())
    if not m:
        return None
    id_snp, gene_bruto, resto = m.groups()

    gene = re.split(r"\s+[—-]\s+", gene_bruto)[0].strip()

    alelo = resto.strip()
    alelo = re.sub(r"^alelo\s+", "", alelo, flags=re.IGNORECASE)
    alelo = RE_PARENTESE_FINAL.sub("", alelo).strip()

    return {
        "id_snp": id_snp.upper(),
        "gene": gene,
        "alelo": alelo,
        "observacao": None,
    }


def _parse_linha_classificacao(linha: str):
    """
    Separa a linha 'RISCO Categoria RS#### (...) | ...' em três partes.

    O risco é o primeiro token; a categoria vai até o primeiro identificador
    de SNP; o restante são os marcadores separados por barra vertical.
    """
    linha = linha.strip()
    risco = None
    for nivel in NIVEIS_RISCO:
        if linha.upper().startswith(nivel):
            risco = nivel
            linha = linha[len(nivel):].strip()
            break
    if risco is None:
        return None, None, []

    corte = re.search(r"\bRS\d+\b", linha, re.IGNORECASE)
    if not corte:
        return risco, _limpar(linha), []

    categoria = _limpar(linha[:corte.start()])
    marcadores = [
        p for p in (_parse_marcador(f) for f in linha[corte.start():].split("|"))
        if p
    ]
    return risco, categoria, marcadores


def parse_resultados(texto: str):
    """
    Extrai a lista de condições genéticas.

    Cada bloco começa por um subtítulo numerado (2.1, 2.2, ...). Dentro dele,
    a linha seguinte ao cabeçalho da tabela carrega risco, categoria e
    marcadores; os parágrafos são delimitados pelos rótulos impressos.
    """
    avisos = []
    linhas = texto.split("\n")

    inicios = [
        (i, m.group(1), _limpar(m.group(2)))
        for i, linha in enumerate(linhas)
        for m in [RE_INICIO_CONDICAO.match(linha.strip())]
        if m
    ]
    if not inicios:
        return [], [{"campo": "resultados", "motivo": "nenhum bloco numerado encontrado"}]

    resultados = []
    for pos, (indice, ident, doenca) in enumerate(inicios):
        fim = inicios[pos + 1][0] if pos + 1 < len(inicios) else len(linhas)
        bloco = linhas[indice + 1:fim]
        bloco_texto = "\n".join(bloco)

        risco = categoria = None
        marcadores = []
        for j, linha in enumerate(bloco):
            if linha.strip().startswith(CABECALHO_TABELA_CONDICAO) and j + 1 < len(bloco):
                risco, categoria, marcadores = _parse_linha_classificacao(bloco[j + 1])
                break

        if risco is None:
            avisos.append({
                "campo": f"resultados[{ident}].risco",
                "motivo": "linha de classificação não localizada no bloco",
            })
        if not marcadores:
            avisos.append({
                "campo": f"resultados[{ident}].marcadores_geneticos",
                "motivo": "nenhum marcador reconhecido no formato RS#### (GENE) — alelo",
            })

        descricao = _entre_rotulos(bloco_texto, ROTULO_DESCRICAO, ROTULO_RECOMENDACAO)
        recomendacao = _entre_rotulos(bloco_texto, ROTULO_RECOMENDACAO, None)

        if descricao is None:
            avisos.append({
                "campo": f"resultados[{ident}].descricao_tecnica",
                "motivo": f"rótulo '{ROTULO_DESCRICAO}' não encontrado",
            })
        if recomendacao is None:
            avisos.append({
                "campo": f"resultados[{ident}].recomendacao",
                "motivo": f"rótulo '{ROTULO_RECOMENDACAO}' não encontrado",
            })

        percentil = None
        if descricao:
            m = RE_PERCENTIL.search(descricao)
            if m:
                percentil = int(m.group(1))

        resultados.append({
            "id": ident,
            "doenca": doenca,
            "categoria": categoria,
            "risco": risco.capitalize() if risco else None,
            "marcadores_geneticos": marcadores,
            "escore_poligênico_percentil": percentil,
            "descricao_tecnica": descricao,
            "descricao_simples": None,
            "recomendacao": recomendacao,
            "impacto_pratico": None,
            "urgencia_medica": None,
            "relevancia_medico": None,
            "fontes": None,
        })

    return resultados, avisos


def _entre_rotulos(texto: str, inicio: str, fim):
    """Devolve o texto entre dois rótulos impressos (ou até o fim do bloco)."""
    i = texto.find(inicio)
    if i < 0:
        return None
    i += len(inicio)
    if fim:
        j = texto.find(fim, i)
        if j >= 0:
            return _limpar(texto[i:j])
    return _limpar(texto[i:])


# ─────────────────────────────────────────────────────────────────────────────
# SEÇÃO 3 — ANCESTRALIDADE
# ─────────────────────────────────────────────────────────────────────────────

TITULO_TABELA_ANCESTRALIDADE = "Região de Ancestralidade"


def parse_ancestralidade(tabelas: list):
    """Extrai as proporções de ancestralidade a partir da tabela de 3 colunas."""
    avisos = []
    tabela = _achar_tabela(tabelas, TITULO_TABELA_ANCESTRALIDADE)
    if not tabela or len(tabela) < 2:
        return [], [{
            "campo": "ancestralidade",
            "motivo": f"tabela '{TITULO_TABELA_ANCESTRALIDADE}' não localizada",
        }]

    itens = []
    for linha in tabela[1:]:
        if len(linha) < 3:
            continue
        regiao = _limpar(linha[0])
        percentual = percentual_br(_limpar(linha[1]))
        intervalo = _limpar(linha[2])
        if percentual is None:
            avisos.append({
                "campo": f"ancestralidade[{regiao}].percentual",
                "motivo": "percentual fora do formato numérico esperado",
            })
        itens.append({
            "regiao": regiao,
            "percentual": percentual,
            "intervalo_confianca_95": intervalo.replace(",", ".") if intervalo else None,
        })
    return itens, avisos


# ─────────────────────────────────────────────────────────────────────────────
# SEÇÃO 4 — METODOLOGIA
# ─────────────────────────────────────────────────────────────────────────────

TITULO_TABELA_METODOLOGIA = "Etapa"


def parse_metodologia(texto: str, tabelas: list):
    """Extrai plataforma, cobertura, genoma de referência e etapas do pipeline."""
    avisos = []
    dados = {
        "plataforma": None,
        "cobertura_snps": None,
        "genoma_referencia": None,
        "etapas": [],
    }

    m = RE_PLATAFORMA_METODO.search(texto)
    if m:
        dados["plataforma"] = _limpar(m.group(1))
        dados["cobertura_snps"] = numero_br(m.group(2))
    else:
        avisos.append({
            "campo": "metodologia.plataforma",
            "motivo": "trecho de plataforma/cobertura não encontrado na seção",
        })

    g = RE_GENOMA.search(texto)
    if g:
        dados["genoma_referencia"] = _limpar(g.group(1))
    else:
        avisos.append({
            "campo": "metodologia.genoma_referencia",
            "motivo": "referência de genoma não encontrada",
        })

    tabela = _achar_tabela(tabelas, TITULO_TABELA_METODOLOGIA)
    if tabela and len(tabela) >= 2:
        for linha in tabela[1:]:
            if len(linha) < 3:
                continue
            dados["etapas"].append({
                "etapa": _limpar(linha[0]),
                "ferramenta": _limpar(linha[1]),
                "parametro_qualidade": _limpar(linha[2]),
            })
    else:
        avisos.append({
            "campo": "metodologia.etapas",
            "motivo": f"tabela '{TITULO_TABELA_METODOLOGIA}' não localizada",
        })

    return dados, avisos


# ─────────────────────────────────────────────────────────────────────────────
# SEÇÃO 5 — RODAPÉ / METADADOS
# ─────────────────────────────────────────────────────────────────────────────

def parse_metadata(texto: str):
    """Extrai os metadados do rodapé: responsável, laboratório, versão e emissão."""
    avisos = []
    dados = {
        "versao_relatorio": None,
        "laboratorio": None,
        "cnes_laboratorio": None,
        "endereco_laboratorio": None,
        "responsavel_tecnico": None,
        "crm_responsavel": None,
        "especialidade_responsavel": None,
        "data_processamento": None,
    }

    linha_resp = _linha_com(texto, ROTULO_RESPONSAVEL)
    if linha_resp:
        corpo = linha_resp.split(ROTULO_RESPONSAVEL, 1)[1]
        partes = [p.strip() for p in re.split(r"\s+—\s+", corpo) if p.strip()]
        if partes:
            dados["responsavel_tecnico"] = partes[0]
        for parte in partes[1:]:
            if RE_CRM.search(parte):
                dados["crm_responsavel"] = _limpar(RE_CRM.search(parte).group(0))
            elif parte.startswith(ROTULO_ESPECIALISTA):
                dados["especialidade_responsavel"] = parte[len(ROTULO_ESPECIALISTA):].strip()
    else:
        avisos.append({
            "campo": "metadata.responsavel_tecnico",
            "motivo": f"rótulo '{ROTULO_RESPONSAVEL}' não encontrado no rodapé",
        })

    linha_lab = _linha_com(texto, ROTULO_CNES)
    if linha_lab:
        partes = [p.strip() for p in linha_lab.split("|")]
        if partes:
            dados["laboratorio"] = _limpar(re.sub(r"\s*Laborat[óo]rio\s*$", "", partes[0]))
        for parte in partes[1:]:
            if parte.startswith(ROTULO_CNES):
                dados["cnes_laboratorio"] = parte[len(ROTULO_CNES):].strip()
            else:
                dados["endereco_laboratorio"] = _limpar(parte)
    else:
        avisos.append({
            "campo": "metadata.laboratorio",
            "motivo": f"rótulo '{ROTULO_CNES}' não encontrado no rodapé",
        })

    linha_versao = _linha_com(texto, ROTULO_VERSAO)
    if linha_versao:
        m = re.search(re.escape(ROTULO_VERSAO) + r"\s*([^\s|]+)", linha_versao)
        if m:
            dados["versao_relatorio"] = m.group(1).strip()
        dados["data_processamento"] = data_iso(
            linha_versao.split(ROTULO_EMISSAO, 1)[1]
            if ROTULO_EMISSAO in linha_versao else ""
        )
    else:
        avisos.append({
            "campo": "metadata.versao_relatorio",
            "motivo": f"rótulo '{ROTULO_VERSAO}' não encontrado no rodapé",
        })

    return dados, avisos


def _linha_com(texto: str, marcador: str):
    """Devolve a primeira linha que contém o marcador informado."""
    for linha in texto.split("\n"):
        if marcador in linha:
            return linha.strip()
    return None
