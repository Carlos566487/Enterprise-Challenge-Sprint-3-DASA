"""
Validação do módulo de PLN — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Mede, sem opinar, a simplificação de linguagem de sprint3/nlp/nlp_simplificacao.py
(módulo da Tayná — NÃO é editado aqui, só chamado).

Entradas: textos reais e fixos de dados_estruturados.json — descricao_tecnica,
recomendacao e impacto_pratico das 7 condições (21 textos).

Medidas por texto:
  1. Legibilidade antes x depois
       • métricas do próprio módulo (calcular_metricas): palavras, frases,
         palavras/frase, caracteres/palavra;
       • Índice de Legibilidade de Flesch adaptado ao português
         (Martins et al., 1996): 248,835 − 1,015·(palavras/frase)
         − 84,6·(sílabas/palavra). Sílabas contadas por grupos vocálicos —
         aproximação documentada, não silabação exata;
       • densidade de termos técnicos: ocorrências do léxico técnico abaixo
         por 100 palavras.
  2. Ancoragem depois de simplificar — pelo MESMO mecanismo do
     adaptador_nlp.py: responder_com_linguagem_simples() com a busca
     devolvendo o chunk real que contém o texto e o LLM substituído pelo
     próprio texto do relatório (mecanismo, não qualidade de geração).
     Registra simplificacao.aplicada / motivo / termos_nao_ancorados.
  3. Erros introduzidos pela substituição termo a termo, por detectores
     objetivos (cada ocorrência gravada com o trecho, para auditoria):
       E1 substituição dentro de palavra maior (termo da regra colado a
          letra — ex.: 'alelo' dentro de 'alelos');
       E2 concordância: determinante masculino (singular ou plural) antes de expressão
          de substituição feminina ou plural (ex.: 'o versão');
       E3 duplicação: palavra ou par de palavras repetido em sequência.

Uso:
    python sprint4/avaliacao/avaliar_pln.py
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]
for _c in (RAIZ, RAIZ / "sprint3" / "nlp"):
    if str(_c) not in sys.path:
        sys.path.insert(0, str(_c))

from nlp_simplificacao import REGRAS_SIMPLIFICACAO, calcular_metricas, simplificar_texto  # noqa: E402
from sprint3.integracao import responder_com_linguagem_simples  # noqa: E402

CAMPOS = ("descricao_tecnica", "recomendacao", "impacto_pratico")

# Campo do JSON → seção do chunk que o contém (sprint2/embeddings/gerar_embeddings.py).
SECAO_DO_CAMPO = {
    "descricao_tecnica": "marcadores",
    "recomendacao": "recomendacao",
    "impacto_pratico": "resultado",
}

LEXICO_TECNICO = (
    "homozigose", "heterozigose", "homozigoto", "heterozigoto", "polimorfismo",
    "alelo", "genótipo", "fenótipo", "haplótipo", "variante", "penetrância",
    "odds ratio", "patogênica", "patogênico", "susceptibilidade", "herdabilidade",
    "mutação", "wild-type", "marcadores genéticos", "predisposição genética",
)

VOGAIS = re.compile(r"[aeiouáéíóúâêôãõàü]+", re.IGNORECASE)
PALAVRA = re.compile(r"\b\w+\b")

# Expressões de substituição (lado direito das regras) femininas ou plurais,
# e os determinantes que não concordam com elas.
SUBSTITUICOES_FEMININAS = (
    "versão de um gene", "variação comum no DNA", "alteração no DNA",
    "característica observável", "influência da genética", "maior chance",
    "chance maior", "chance menor", "características do DNA",
    "informações do DNA",
)
DETERMINANTES_MASC = (r"(o|um|do|no|ao|pelo|este|esse|seu|deste|desse"
                      r"|os|uns|dos|nos|aos|pelos|estes|esses|seus|dois)")


def flesch_pt(texto: str):
    palavras = PALAVRA.findall(texto)
    frases = [f for f in re.split(r"(?<=[.!?])\s+", texto.strip()) if f]
    if not palavras or not frases:
        return None
    silabas = sum(max(1, len(VOGAIS.findall(p))) for p in palavras)
    return round(248.835 - 1.015 * (len(palavras) / len(frases))
                 - 84.6 * (silabas / len(palavras)), 2)


def densidade_tecnica(texto: str) -> dict:
    minusculo = texto.lower()
    ocorrencias = {}
    for termo in LEXICO_TECNICO:
        n = len(re.findall(r"\b" + re.escape(termo) + r"\w*", minusculo))
        if n:
            ocorrencias[termo] = n
    palavras = len(PALAVRA.findall(texto))
    total = sum(ocorrencias.values())
    return {
        "ocorrencias": ocorrencias,
        "total": total,
        "por_100_palavras": round(100 * total / palavras, 2) if palavras else None,
    }


def _trecho(texto: str, inicio: int, fim: int, margem: int = 35) -> str:
    return "…" + texto[max(0, inicio - margem):min(len(texto), fim + margem)] + "…"


def detectar_e1(original: str) -> list:
    """Termo de regra casado DENTRO de palavra maior no texto de entrada."""
    achados = []
    for termo, _ in REGRAS_SIMPLIFICACAO:
        padrao = r"\s+".join(re.escape(p) for p in termo.split())
        for m in re.finditer(padrao, original, flags=re.IGNORECASE):
            antes = original[m.start() - 1] if m.start() > 0 else " "
            depois = original[m.end()] if m.end() < len(original) else " "
            if antes.isalpha() or depois.isalpha():
                palavra = re.search(r"\w*" + padrao + r"\w*",
                                    original[max(0, m.start() - 20):m.end() + 20],
                                    flags=re.IGNORECASE)
                achados.append({
                    "termo_da_regra": termo,
                    "palavra_atingida": palavra.group(0) if palavra else None,
                    "trecho_original": _trecho(original, m.start(), m.end()),
                })
    return achados


def detectar_e2(simplificado: str) -> list:
    achados = []
    for expr in SUBSTITUICOES_FEMININAS:
        padrao = r"\b" + DETERMINANTES_MASC + r"\s+" + re.escape(expr)
        for m in re.finditer(padrao, simplificado, flags=re.IGNORECASE):
            achados.append({
                "expressao": m.group(0),
                "trecho_simplificado": _trecho(simplificado, m.start(), m.end()),
            })
    return achados


def detectar_e3(simplificado: str) -> list:
    achados = []
    for m in re.finditer(r"\b(\w+(?:\s+\w+)?)\s+\1\b", simplificado, flags=re.IGNORECASE):
        achados.append({
            "repeticao": m.group(0),
            "trecho_simplificado": _trecho(simplificado, m.start(), m.end()),
        })
    return achados


def ancoragem_pelo_adaptador(texto: str, chunk: str, secao: str) -> dict:
    """Usa responder_com_linguagem_simples() com busca e LLM substituídos."""
    def busca(pergunta, top_k):
        return {"trechos": [{"conteudo": chunk, "secao": secao,
                             "fonte": "dados_estruturados.json", "similaridade": 1.0}]}

    def llm(pergunta, trechos, modo, api_key):
        return {"status": "respondido", "resposta": texto, "categoria": "resposta_rag"}

    r = responder_com_linguagem_simples(
        pergunta="Explique este trecho do meu relatório.", perfil="leigo_ansioso",
        usuario_id="avaliacao-pln", api_key=None, fn_buscar=busca, fn_llm=llm,
    )
    return {
        "ancoragem_original": r["ancoragem"],
        "simplificacao_aplicada": r["simplificacao"]["aplicada"],
        "motivo": r["simplificacao"]["motivo"],
        "termos_nao_ancorados_apos_simplificar":
            r["simplificacao"].get("termos_nao_ancorados", []),
        "texto_exibido": r["resposta_simplificada"],
    }


# Sondas SINTÉTICAS — não são texto do relatório e não entram nas médias.
# Existem só para confirmar se os defeitos conhecidos do mecanismo de
# substituição (sem limite de palavra; sem concordância) ainda ocorrem,
# com frases no estilo do que o LLM costuma produzir.
SONDAS = (
    ("plural_de_termo", "Foram encontrados dois alelos de risco."),
    ("termo_dentro_de_outra_palavra", "O resultado segue em paralelo ao exame anterior."),
    ("plural_de_polimorfismo", "Os polimorfismos avaliados são comuns."),
    ("artigo_masculino", "O genótipo APOE foi analisado."),
    ("duplicacao_por_contexto", "Foi encontrada uma variante genética no DNA do paciente."),
    ("duplicacao_por_contexto_2", "Os marcadores genéticos do DNA foram avaliados."),
)


def rodar_sondas() -> list:
    linhas = []
    for nome, entrada in SONDAS:
        saida = simplificar_texto(entrada)["texto_simplificado"]
        linhas.append({
            "sonda": nome,
            "entrada_sintetica": entrada,
            "saida": saida,
            "E1_dentro_de_palavra": detectar_e1(entrada),
            "E2_concordancia": detectar_e2(saida),
            "E3_duplicacao": detectar_e3(saida),
        })
    return linhas


def carregar_chunks() -> dict:
    import chromadb

    col = chromadb.PersistentClient(
        path=str(RAIZ / "sprint2" / "vetorial" / "base_vetorial")
    ).get_collection("genera_relatorio")
    dados = col.get(include=["documents", "metadatas"])
    return {m["secao"]: d for m, d in zip(dados["metadatas"], dados["documents"])}


def main() -> int:
    relatorio = json.loads((RAIZ / "dados_estruturados.json").read_text(encoding="utf-8"))
    chunks = carregar_chunks()

    linhas = []
    for resultado in relatorio["resultados"]:
        for campo in CAMPOS:
            original = resultado.get(campo) or ""
            if not original.strip():
                continue
            secao = f"{SECAO_DO_CAMPO[campo]}_{resultado['id']}"
            saida = simplificar_texto(original)
            simplificado = saida["texto_simplificado"]
            linhas.append({
                "condicao": resultado["id"],
                "doenca": resultado["doenca"],
                "campo": campo,
                "texto_original": original,
                "texto_simplificado": simplificado,
                "alterado": simplificado != saida["texto_original"],
                "metricas_modulo": {"original": saida["metricas_original"],
                                    "simplificado": saida["metricas_simplificado"]},
                "flesch_pt": {"original": flesch_pt(original),
                              "simplificado": flesch_pt(simplificado)},
                "densidade_tecnica": {"original": densidade_tecnica(original),
                                      "simplificado": densidade_tecnica(simplificado)},
                "erros": {"E1_dentro_de_palavra": detectar_e1(original),
                          "E2_concordancia": detectar_e2(simplificado),
                          "E3_duplicacao": detectar_e3(simplificado)},
                "adaptador": ancoragem_pelo_adaptador(original, chunks[secao], secao),
                "chunk_secao": secao,
            })

    def media(chave_fn):
        valores = [v for v in (chave_fn(l) for l in linhas) if v is not None]
        return round(sum(valores) / len(valores), 2) if valores else None

    campos_vazios = [
        f"{r['id']}.{c}" for r in relatorio["resultados"] for c in CAMPOS
        if not (r.get(c) or "").strip()
    ]
    sondas = rodar_sondas()

    resumo = {
        "textos": len(linhas),
        "campos_vazios_no_json": campos_vazios,
        "textos_alterados": sum(1 for l in linhas if l["alterado"]),
        "media_flesch_pt": {
            "original": media(lambda l: l["flesch_pt"]["original"]),
            "simplificado": media(lambda l: l["flesch_pt"]["simplificado"]),
        },
        "media_palavras_por_frase": {
            "original": media(lambda l: l["metricas_modulo"]["original"].get("media_palavras_por_frase")),
            "simplificado": media(lambda l: l["metricas_modulo"]["simplificado"].get("media_palavras_por_frase")),
        },
        "media_caracteres_por_palavra": {
            "original": media(lambda l: l["metricas_modulo"]["original"].get("media_caracteres_por_palavra")),
            "simplificado": media(lambda l: l["metricas_modulo"]["simplificado"].get("media_caracteres_por_palavra")),
        },
        "media_densidade_tecnica_por_100": {
            "original": media(lambda l: l["densidade_tecnica"]["original"]["por_100_palavras"]),
            "simplificado": media(lambda l: l["densidade_tecnica"]["simplificado"]["por_100_palavras"]),
        },
        "erros": {
            "E1_dentro_de_palavra": sum(len(l["erros"]["E1_dentro_de_palavra"]) for l in linhas),
            "E2_concordancia": sum(len(l["erros"]["E2_concordancia"]) for l in linhas),
            "E3_duplicacao": sum(len(l["erros"]["E3_duplicacao"]) for l in linhas),
            "textos_com_algum_erro": sum(1 for l in linhas if any(l["erros"].values())),
        },
        "adaptador": {
            "simplificacao_aplicada": sum(1 for l in linhas if l["adaptador"]["simplificacao_aplicada"]),
            "quebrou_ancoragem": sum(1 for l in linhas if l["adaptador"]["motivo"] == "quebrou_ancoragem"),
            "motivos": sorted({l["adaptador"]["motivo"] for l in linhas}),
            "ancoragem_original_falhou": sum(1 for l in linhas
                                             if l["adaptador"]["ancoragem_original"]["ancorado"] is False),
        },
    }

    saida = {
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "modulo_avaliado": "sprint3/nlp/nlp_simplificacao.py::simplificar_texto (não editado)",
        "entrada": "dados_estruturados.json — descricao_tecnica, recomendacao, impacto_pratico × 7 condições",
        "resumo": resumo,
        "textos": linhas,
        "sondas_sinteticas": {
            "aviso": "Entradas inventadas para testar o mecanismo; NÃO entram nas métricas acima.",
            "resultados": sondas,
        },
    }
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = DIR / "execucoes" / f"pln_{carimbo}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    for l in linhas:
        for tipo, achados in l["erros"].items():
            for a in achados:
                print(f"{l['condicao']} {l['campo']} {tipo}: {a}")
        if l["adaptador"]["motivo"] != "ok":
            print(f"{l['condicao']} {l['campo']} ADAPTADOR motivo={l['adaptador']['motivo']} "
                  f"{l['adaptador']['termos_nao_ancorados_apos_simplificar']}")
    for s in sondas:
        print(f"SONDA {s['sonda']}: '{s['entrada_sintetica']}' -> '{s['saida']}' "
              f"E1={len(s['E1_dentro_de_palavra'])} E2={len(s['E2_concordancia'])} "
              f"E3={len(s['E3_duplicacao'])}")
    print(f"[pln] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
