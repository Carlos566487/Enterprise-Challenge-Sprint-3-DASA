"""
Testes do extrator PDF → JSON — Sprint 1 / Genera AI / Dasa

Executar:
    pytest sprint1/extracao/ -v

Estratégia de dependência do PDF
────────────────────────────────────────────────────────────────────────────
O relatório em PDF não é versionado (política de privacidade, ver
sprint1/README_dados_simulados.md). Os testes lidam com isso assim:

  • Testes de parsing e de robustez usam fixtures SINTÉTICOS e rodam sempre,
    inclusive no CI em clone limpo.
  • Testes contra o oráculo precisam do PDF. A fixture tenta, nesta ordem:
        1. usar o PDF já presente no disco;
        2. gerar um com sprint1/gerar_pdf.py (exige reportlab);
        3. pular com mensagem explícita.
    Nunca falham por ausência do insumo — e nunca são removidos para o CI passar.

Os fixtures sintéticos usam identificadores inventados (RS0000001, GENEX...),
nunca valores do relatório real. Isso mantém a regra anti-trapaça e, de quebra,
prova que o parser é genérico e não foi ajustado a um conteúdo específico.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

_DIR = Path(__file__).resolve().parent
RAIZ = _DIR.parents[1]
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

from extrair_pdf import ErroExtracao, extrair_relatorio        # noqa: E402
from secoes import (                                            # noqa: E402
    _parse_linha_classificacao,
    _parse_marcador,
    data_iso,
    numero_br,
    parse_cabecalho,
    parse_resultados,
    percentual_br,
    reparar_codepoints,
)

PDF_REPO = RAIZ / "sprint1" / "relatorio_genera_simulado.pdf"
GERADOR = RAIZ / "sprint1" / "gerar_pdf.py"
ORACULO = RAIZ / "dados_estruturados.json"


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def caminho_pdf(tmp_path_factory):
    """
    Devolve um PDF do relatório, gerando-o se necessário.

    Ordem: PDF no disco → gerar com reportlab → skip explícito.
    """
    if PDF_REPO.exists():
        return PDF_REPO

    if not GERADOR.exists():
        pytest.skip(
            f"PDF ausente e gerador não encontrado em {GERADOR}. "
            "Ver sprint1/README_dados_simulados.md."
        )

    try:
        import reportlab  # noqa: F401
    except ImportError:
        pytest.skip(
            "PDF do relatório não está no repositório (política de privacidade) e "
            "reportlab não está instalado para regenerá-lo. "
            "Rode 'pip install reportlab' para habilitar os testes de oráculo — "
            "ver sprint1/README_dados_simulados.md."
        )

    destino = tmp_path_factory.mktemp("pdf")
    subprocess.run(
        [sys.executable, str(GERADOR)],
        cwd=str(destino), check=True, capture_output=True,
    )
    gerado = destino / "relatorio_genera_simulado.pdf"
    if not gerado.exists():
        pytest.skip("gerar_pdf.py rodou mas não produziu o PDF esperado")
    return gerado


@pytest.fixture(scope="session")
def extraido(caminho_pdf):
    """Resultado da extração sobre o PDF disponível."""
    return extrair_relatorio(caminho_pdf)


@pytest.fixture(scope="session")
def oraculo():
    """JSON de referência, produzido manualmente na Sprint 1."""
    if not ORACULO.exists():
        pytest.skip(f"oráculo não encontrado em {ORACULO}")
    with open(ORACULO, encoding="utf-8") as arquivo:
        return json.load(arquivo)


# ─────────────────────────────────────────────────────────────────────────────
# 1. PARSING — fixtures sintéticos, rodam sempre (sem PDF)
# ─────────────────────────────────────────────────────────────────────────────

def test_data_iso_converte_formato_brasileiro():
    assert data_iso("01/02/2003") == "2003-02-01"
    assert data_iso("texto sem data") is None
    assert data_iso("") is None


def test_numero_br_interpreta_milhar_e_decimal():
    assert numero_br("1.234") == 1234
    assert numero_br("12,5") == 12.5
    assert numero_br("7") == 7
    assert numero_br("abc") is None


def test_percentual_br():
    assert percentual_br("12,5%") == 12.5
    assert percentual_br("100%") == 100
    assert percentual_br("sem percentual") is None


def test_reparo_de_codepoint_corrompido():
    """A fonte do PDF renderiza ≥ como ‡; o reparo é de caractere, não de valor."""
    assert reparar_codepoints("valor ‡ 10") == "valor ≥ 10"


@pytest.mark.parametrize("fragmento,esperado", [
    ("RS0000001 (GENEX) — alelo A/B",
     {"id_snp": "RS0000001", "gene": "GENEX", "alelo": "A/B"}),
    ("RS0000002 (GENEY) — alelo C/D (qualificador)",
     {"id_snp": "RS0000002", "gene": "GENEY", "alelo": "C/D"}),
    ("RS0000003 (GENEZ — nome extenso) — alelo E/F",
     {"id_snp": "RS0000003", "gene": "GENEZ", "alelo": "E/F"}),
    ("RS0000004 (GENEW) — variante descritiva x.123del",
     {"id_snp": "RS0000004", "gene": "GENEW", "alelo": "variante descritiva x.123del"}),
    ("RS0000005 (GENEV) — alelo positivo",
     {"id_snp": "RS0000005", "gene": "GENEV", "alelo": "positivo"}),
])
def test_parse_marcador_formatos(fragmento, esperado):
    marcador = _parse_marcador(fragmento)
    assert marcador is not None
    for chave, valor in esperado.items():
        assert marcador[chave] == valor
    assert marcador["observacao"] is None


def test_parse_marcador_rejeita_fragmento_invalido():
    assert _parse_marcador("texto que não é marcador") is None


def test_parse_linha_classificacao_separa_tres_partes():
    linha = "ALTO Categoria Inventada RS0000001 (GENEX) — alelo A/B | RS0000002 (GENEY) — alelo C/D"
    risco, categoria, marcadores = _parse_linha_classificacao(linha)
    assert risco == "ALTO"
    assert categoria == "Categoria Inventada"
    assert [m["id_snp"] for m in marcadores] == ["RS0000001", "RS0000002"]


def test_parse_cabecalho_associa_rotulos_em_duas_colunas():
    texto = (
        "Paciente: Fulano de Tal ID Relatório: XXX-0000-00000\n"
        "Data de Nascimento: 01/02/2003 Data do Exame: 04/05/2006\n"
        "CPF: ***.***.***-** Data de Emissão: 07/08/2009\n"
        "Médico Solicitante: Dra. Beltrana CRM/XX 00000 Laboratório: Lab Fictício\n"
    )
    dados, avisos = parse_cabecalho(texto)
    assert dados["nome"] == "Fulano de Tal"
    assert dados["id_relatorio"] == "XXX-0000-00000"
    assert dados["data_nascimento"] == "2003-02-01"
    assert dados["data_exame"] == "2006-05-04"
    assert dados["data_emissao"] == "2009-08-07"
    assert dados["medico_solicitante"] == "Dra. Beltrana"
    assert dados["crm_medico"] == "CRM/XX 00000"
    assert avisos == []


def test_parse_cabecalho_avisa_campo_ausente():
    dados, avisos = parse_cabecalho("Paciente: Fulano de Tal\n")
    assert dados["nome"] == "Fulano de Tal"
    assert dados["id_relatorio"] is None
    assert any(a["campo"] == "paciente.id_relatorio" for a in avisos)


def test_parse_resultados_bloco_sintetico():
    texto = (
        "9.1 Condição Inventada\n"
        "Nível de Risco Categoria Marcadores Principais\n"
        "MÉDIO Especialidade Fictícia RS0000001 (GENEX) — alelo A/B\n"
        "Descrição Técnica:\n"
        "Texto técnico qualquer. Escore poligênico: percentil 42.\n"
        "Recomendação Clínica:\n"
        "Texto de recomendação qualquer.\n"
    )
    resultados, _ = parse_resultados(texto)
    assert len(resultados) == 1
    r = resultados[0]
    assert r["id"] == "9.1"
    assert r["doenca"] == "Condição Inventada"
    assert r["risco"] == "Médio"
    assert r["categoria"] == "Especialidade Fictícia"
    assert r["escore_poligênico_percentil"] == 42
    assert r["descricao_tecnica"].startswith("Texto técnico")
    assert r["recomendacao"] == "Texto de recomendação qualquer."


def test_campos_derivados_saem_nulos():
    """O extrator nunca inventa o que não está no PDF."""
    texto = (
        "9.1 Condição Inventada\n"
        "Nível de Risco Categoria Marcadores Principais\n"
        "BAIXO Especialidade RS0000001 (GENEX) — alelo A/B\n"
        "Descrição Técnica:\nTexto.\nRecomendação Clínica:\nTexto.\n"
    )
    resultados, _ = parse_resultados(texto)
    r = resultados[0]
    for campo in ("descricao_simples", "impacto_pratico", "urgencia_medica",
                  "relevancia_medico", "fontes"):
        assert r[campo] is None, f"{campo} deveria sair nulo"


# ─────────────────────────────────────────────────────────────────────────────
# 2. ROBUSTEZ — rodam sempre (sem PDF)
# ─────────────────────────────────────────────────────────────────────────────

def test_arquivo_inexistente():
    with pytest.raises(ErroExtracao, match="não encontrado"):
        extrair_relatorio("caminho/que/nao/existe.pdf")


def test_diretorio_em_vez_de_arquivo(tmp_path):
    with pytest.raises(ErroExtracao, match="não é um arquivo"):
        extrair_relatorio(tmp_path)


def test_arquivo_que_nao_e_pdf(tmp_path):
    falso = tmp_path / "relatorio.pdf"
    falso.write_text("isto é texto puro, não um PDF", encoding="utf-8")
    with pytest.raises(ErroExtracao, match="Não foi possível ler o PDF"):
        extrair_relatorio(falso)


def test_pdf_corrompido(tmp_path):
    corrompido = tmp_path / "corrompido.pdf"
    corrompido.write_bytes(b"%PDF-1.4\n" + b"\x00\xff" * 200)
    with pytest.raises(ErroExtracao):
        extrair_relatorio(corrompido)


# ─────────────────────────────────────────────────────────────────────────────
# 3. ORÁCULO — exigem o PDF (skip explícito quando indisponível)
# ─────────────────────────────────────────────────────────────────────────────

def test_paciente_bate_com_oraculo(extraido, oraculo):
    obtido = extraido["dados"]["paciente"]
    esperado = oraculo["paciente"]
    for campo in esperado:
        assert obtido[campo] == esperado[campo], f"paciente.{campo}"


def test_ancestralidade_bate_com_oraculo(extraido, oraculo):
    obtido = extraido["dados"]["ancestralidade"]
    esperado = oraculo["ancestralidade"]
    assert len(obtido) == len(esperado)
    for o, e in zip(obtido, esperado):
        assert o["regiao"] == e["regiao"]
        assert o["percentual"] == e["percentual"]
        assert o["intervalo_confianca_95"] == e["intervalo_confianca_95"]


def test_sumario_contagens_batem(extraido, oraculo):
    obtido = extraido["dados"]["sumario"]
    esperado = oraculo["sumario"]
    for campo in ("total_condicoes_analisadas", "condicoes_alto_risco",
                  "condicoes_medio_risco", "condicoes_baixo_risco",
                  "cobertura_genomica_snps", "plataforma_genotipagem"):
        assert obtido[campo] == esperado[campo], f"sumario.{campo}"


def test_aviso_legal_e_superconjunto_do_oraculo(extraido, oraculo):
    """
    A extração traz o parágrafo COMPLETO do PDF; o oráculo foi truncado à mão.

    Divergência conhecida a favor da extração: o oráculo corta o aviso legal
    após a segunda frase, enquanto o PDF traz uma terceira sobre fatores
    ambientais. Forçar a igualdade exigiria descartar texto real do documento.
    """
    obtido = extraido["dados"]["sumario"]["aviso_legal"]
    esperado = oraculo["sumario"]["aviso_legal"]
    assert obtido.startswith(esperado)
    assert len(obtido) > len(esperado)


def test_resultados_identificacao_bate(extraido, oraculo):
    obtido = extraido["dados"]["resultados"]
    esperado = oraculo["resultados"]
    assert len(obtido) == len(esperado)
    for o, e in zip(obtido, esperado):
        assert o["id"] == e["id"]
        assert o["doenca"] == e["doenca"]
        assert o["categoria"] == e["categoria"]
        assert o["risco"] == e["risco"]


def test_percentil_bate_quando_o_pdf_informa(extraido, oraculo):
    """
    O percentil é extraído do texto da descrição técnica ("percentil NN").

    Duas condições do oráculo trazem percentil que NÃO aparece em lugar nenhum
    do PDF — foram acrescentados por quem montou o JSON à mão. Para essas, o
    comportamento correto do extrator é devolver None, e é isso que se verifica.
    """
    sem_percentil_no_pdf = []
    for o, e in zip(extraido["dados"]["resultados"], oraculo["resultados"]):
        if o["escore_poligênico_percentil"] is None:
            if e["escore_poligênico_percentil"] is not None:
                sem_percentil_no_pdf.append(
                    (o["id"], e["escore_poligênico_percentil"])
                )
        else:
            assert o["escore_poligênico_percentil"] == e["escore_poligênico_percentil"], o["id"]

    # Limitação documentada: valores presentes só no oráculo, não no documento.
    assert len(sem_percentil_no_pdf) == 2, sem_percentil_no_pdf


def test_marcadores_snp_e_gene_batem(extraido, oraculo):
    """
    id_snp e gene batem em 100% dos marcadores.

    O alelo é verificado à parte porque há um caso conhecido de divergência
    de codificação de fonte — ver test_alelo_divergencia_conhecida.
    """
    for o, e in zip(extraido["dados"]["resultados"], oraculo["resultados"]):
        assert len(o["marcadores_geneticos"]) == len(e["marcadores_geneticos"]), o["id"]
        for mo, me in zip(o["marcadores_geneticos"], e["marcadores_geneticos"]):
            assert mo["id_snp"] == me["id_snp"]
            assert mo["gene"] == me["gene"]


def test_metodologia_bate(extraido, oraculo):
    obtido = extraido["dados"]["metodologia"]
    esperado = oraculo["metodologia"]
    assert obtido["plataforma"] == esperado["plataforma"]
    assert obtido["cobertura_snps"] == esperado["cobertura_snps"]
    assert obtido["genoma_referencia"] == esperado["genoma_referencia"]
    assert len(obtido["etapas"]) == len(esperado["etapas"])
    for o, e in zip(obtido["etapas"], esperado["etapas"]):
        assert o["etapa"] == e["etapa"]
        assert o["ferramenta"] == e["ferramenta"]


def test_metadata_rodape_bate(extraido, oraculo):
    obtido = extraido["dados"]["metadata"]
    esperado = oraculo["metadata"]
    for campo in ("versao_relatorio", "laboratorio", "cnes_laboratorio",
                  "endereco_laboratorio", "responsavel_tecnico",
                  "crm_responsavel", "especialidade_responsavel",
                  "data_processamento"):
        assert obtido[campo] == esperado[campo], f"metadata.{campo}"


def test_derivados_saem_nulos_com_aviso(extraido):
    """Campos redigidos fora do PDF saem nulos e são registrados em avisos."""
    dados = extraido["dados"]
    for campo in ("resumo_executivo_paciente", "principais_riscos_medico",
                  "recomendacoes_prioritarias"):
        assert dados["sumario"][campo] is None
    campos_avisados = {a["campo"] for a in extraido["avisos"]}
    assert "sumario.resumo_executivo_paciente" in campos_avisados


def test_nenhuma_falha_de_extracao(extraido):
    """
    Avisos devem ser apenas de campos derivados, nunca de falha de parsing.

    Se um rótulo do PDF deixar de ser encontrado, isto quebra — é o sinal de
    que o layout mudou.
    """
    falhas = [
        a for a in extraido["avisos"]
        if "derivad" not in a["motivo"] and "fora do PDF" not in a["motivo"]
    ]
    assert falhas == [], f"falhas de extração: {falhas}"


def test_alelo_divergencia_conhecida(extraido, oraculo):
    """
    Documenta a única divergência real de conteúdo entre extração e oráculo.

    O PDF grafa o alelo de APOE com a letra latina 'e'; o oráculo usa a letra
    grega 'ε'. A fonte embutida no PDF não preserva o épsilon, então a extração
    honesta devolve o que está no documento. Reparar exigiria adivinhar o valor.
    """
    divergentes = []
    for o, e in zip(extraido["dados"]["resultados"], oraculo["resultados"]):
        for mo, me in zip(o["marcadores_geneticos"], e["marcadores_geneticos"]):
            if mo["alelo"] != me["alelo"]:
                divergentes.append((mo["id_snp"], me["alelo"], mo["alelo"]))

    # Toda divergência de alelo deve ser explicada por perda do épsilon.
    for id_snp, esperado, obtido in divergentes:
        assert esperado.replace("ε", "e") == obtido, (
            f"divergência não explicada em {id_snp}: "
            f"esperado {esperado!r}, obtido {obtido!r}"
        )
