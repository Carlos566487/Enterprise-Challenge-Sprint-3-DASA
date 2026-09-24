"""
Extrator PDF → JSON estruturado — Sprint 1 / Genera AI / Dasa

Fecha a única etapa do pipeline que existia apenas em documentação: transformar
o relatório genético em PDF no `dados_estruturados.json` que alimenta a busca
semântica, o agente e as interfaces.

Uso via linha de comando:
    python sprint1/extracao/extrair_pdf.py <entrada.pdf> [saida.json]

Uso como biblioteca:
    from extrair_pdf import extrair_relatorio
    resultado = extrair_relatorio("sprint1/relatorio_genera_simulado.pdf")
    resultado["dados"]   # dict no schema do projeto
    resultado["avisos"]  # lista de campos não extraídos, com motivo

Honestidade sobre lacunas
────────────────────────────────────────────────────────────────────────────
Campos que não existem no PDF — porque foram redigidos depois, por LLM ou por
pessoa — saem como None e aparecem em `avisos`. O extrator nunca preenche
lacuna com valor inventado: um JSON visivelmente incompleto é preferível a um
JSON silenciosamente errado.

São eles: descricao_simples, impacto_pratico, urgencia_medica,
relevancia_medico, fontes, marcadores[].observacao,
sumario.resumo_executivo_paciente, sumario.principais_riscos_medico e
sumario.recomendacoes_prioritarias.
"""

import json
import sys
import time
from pathlib import Path

_DIR = Path(__file__).resolve().parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

from secoes import (                                             # noqa: E402
    parse_ancestralidade,
    parse_cabecalho,
    parse_metadata,
    parse_metodologia,
    parse_resultados,
    parse_sumario,
    reparar_codepoints,
)

FONTE_EXTRACAO = "pdfplumber"

# Campos do schema que o PDF não contém. Emitidos como None, com aviso.
CAMPOS_DERIVADOS_RESULTADO = (
    "descricao_simples",
    "impacto_pratico",
    "urgencia_medica",
    "relevancia_medico",
    "fontes",
)
CAMPOS_DERIVADOS_SUMARIO = (
    "resumo_executivo_paciente",
    "principais_riscos_medico",
    "recomendacoes_prioritarias",
)


class ErroExtracao(Exception):
    """Falha que impede a extração de prosseguir."""


def _abrir_pdf(caminho: Path):
    """
    Abre o PDF e devolve (texto_completo, tabelas).

    Levanta ErroExtracao com mensagem explícita para arquivo ausente, formato
    inválido ou conteúdo ilegível — nunca devolve dados parciais silenciosos.
    """
    try:
        import pdfplumber
    except ImportError as erro:  # pragma: no cover - depende do ambiente
        raise ErroExtracao(
            "pdfplumber não está instalado. Rode: pip install -r requirements.txt"
        ) from erro

    if not caminho.exists():
        raise ErroExtracao(f"Arquivo não encontrado: {caminho}")
    if not caminho.is_file():
        raise ErroExtracao(f"O caminho não é um arquivo: {caminho}")

    try:
        with pdfplumber.open(str(caminho)) as pdf:
            paginas = []
            tabelas = []
            for pagina in pdf.pages:
                paginas.append(pagina.extract_text() or "")
                tabelas.extend(pagina.extract_tables() or [])
    except ErroExtracao:
        raise
    except Exception as erro:
        raise ErroExtracao(
            f"Não foi possível ler o PDF ({caminho.name}): {erro}. "
            "Verifique se o arquivo é um PDF válido e não está corrompido."
        ) from erro

    texto = reparar_codepoints("\n".join(paginas))
    tabelas = [
        [[reparar_codepoints(c) if c else c for c in linha] for linha in tabela]
        for tabela in tabelas
    ]

    if not texto.strip():
        raise ErroExtracao(
            f"O PDF '{caminho.name}' não contém texto extraível. "
            "Pode ser um documento digitalizado — este extrator não faz OCR."
        )
    return texto, tabelas


def _contar_campos(objeto) -> int:
    """Conta folhas não nulas do dict, para telemetria honesta."""
    if isinstance(objeto, dict):
        return sum(_contar_campos(v) for v in objeto.values())
    if isinstance(objeto, list):
        return sum(_contar_campos(v) for v in objeto)
    return 0 if objeto is None else 1


def extrair_relatorio(caminho_pdf) -> dict:
    """
    Extrai o relatório genético de um PDF nativo.

    Args:
        caminho_pdf: caminho do arquivo PDF.

    Returns:
        {
          "dados":  dict no schema do projeto,
          "avisos": [{"campo": str, "motivo": str}, ...],
          "tempo_segundos": float,
        }

    Raises:
        ErroExtracao: arquivo ausente, formato inválido ou PDF sem texto.
    """
    inicio = time.time()
    caminho = Path(caminho_pdf)
    texto, tabelas = _abrir_pdf(caminho)

    avisos = []

    paciente, av = parse_cabecalho(texto)
    avisos.extend(av)

    sumario, av = parse_sumario(texto, tabelas)
    avisos.extend(av)

    resultados, av = parse_resultados(texto)
    avisos.extend(av)

    ancestralidade, av = parse_ancestralidade(tabelas)
    avisos.extend(av)

    metodologia, av = parse_metodologia(texto, tabelas)
    avisos.extend(av)

    metadata, av = parse_metadata(texto)
    avisos.extend(av)

    # Campos redigidos depois da extração: presentes no schema, vazios aqui.
    for campo in CAMPOS_DERIVADOS_SUMARIO:
        sumario[campo] = None
        avisos.append({
            "campo": f"sumario.{campo}",
            "motivo": "conteúdo redigido fora do PDF (derivado); não extraível",
        })
    for resultado in resultados:
        for campo in CAMPOS_DERIVADOS_RESULTADO:
            avisos.append({
                "campo": f"resultados[{resultado['id']}].{campo}",
                "motivo": "conteúdo redigido fora do PDF (derivado); não extraível",
            })
        for marcador in resultado["marcadores_geneticos"]:
            avisos.append({
                "campo": f"resultados[{resultado['id']}]"
                         f".marcadores_geneticos[{marcador['id_snp']}].observacao",
                "motivo": "interpretação redigida fora do PDF; não extraível",
            })

    duracao = round(time.time() - inicio, 2)

    metadata["tipo_pdf"] = "nativo"
    metadata["fonte_extracao"] = FONTE_EXTRACAO
    metadata["tempo_processamento_segundos"] = duracao

    dados = {
        "paciente": paciente,
        "sumario": sumario,
        "resultados": resultados,
        "ancestralidade": ancestralidade,
        "metodologia": metodologia,
        "metadata": metadata,
    }
    metadata["campos_extraidos_total"] = _contar_campos(dados)

    return {"dados": dados, "avisos": avisos, "tempo_segundos": duracao}


def _resumo_console(resultado: dict) -> None:
    """Imprime um resumo legível do que foi e do que não foi extraído."""
    dados = resultado["dados"]
    print("=" * 66)
    print("EXTRAÇÃO CONCLUÍDA")
    print("=" * 66)
    print(f"  Paciente          : {dados['paciente'].get('nome')}")
    print(f"  Condições         : {len(dados['resultados'])}")
    print(f"  Ancestralidade    : {len(dados['ancestralidade'])} regiões")
    print(f"  Etapas do método  : {len(dados['metodologia']['etapas'])}")
    print(f"  Campos preenchidos: {dados['metadata']['campos_extraidos_total']}")
    print(f"  Tempo             : {resultado['tempo_segundos']}s")

    avisos = resultado["avisos"]
    derivados = [a for a in avisos if "derivad" in a["motivo"] or "fora do PDF" in a["motivo"]]
    falhas = [a for a in avisos if a not in derivados]

    print(f"\n  Campos não extraíveis (redigidos fora do PDF): {len(derivados)}")
    print(f"  Falhas de extração                           : {len(falhas)}")
    for aviso in falhas:
        print(f"    ! {aviso['campo']}: {aviso['motivo']}")
    print("=" * 66)


def main(argv=None) -> int:
    """CLI: recebe o PDF de entrada e, opcionalmente, o JSON de saída."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0 if argv else 2

    entrada = Path(argv[0])
    saida = Path(argv[1]) if len(argv) > 1 else None

    try:
        resultado = extrair_relatorio(entrada)
    except ErroExtracao as erro:
        print(f"[ERRO] {erro}", file=sys.stderr)
        return 1

    _resumo_console(resultado)

    if saida:
        saida.parent.mkdir(parents=True, exist_ok=True)
        with open(saida, "w", encoding="utf-8") as arquivo:
            json.dump(resultado["dados"], arquivo, ensure_ascii=False, indent=2)
        print(f"\n[OK] JSON salvo em: {saida}")
        caminho_avisos = saida.with_suffix(".avisos.json")
        with open(caminho_avisos, "w", encoding="utf-8") as arquivo:
            json.dump(resultado["avisos"], arquivo, ensure_ascii=False, indent=2)
        print(f"[OK] Avisos salvos em: {caminho_avisos}")
    else:
        print("\n(nenhum arquivo de saída informado — JSON não foi gravado)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
