"""
Auditoria de cobertura da base vetorial — Sprint 4 / Genera AI / Dasa
Engenheiro de IA & PLN — Avaliação e Validação

Para cada valor folha de dados_estruturados.json, verifica se ele aparece
literalmente em algum dos chunks da base vetorial. Campos ausentes são
informação que existe no relatório mas que o RAG nunca consegue recuperar —
qualquer resposta que os contenha foi inventada pelo modelo.

Regras de comparação (documentadas para auditoria):
  • texto: substring exata, sem diferenciar maiúsculas;
  • número: forma do JSON (ex.: 42.3) ou com vírgula decimal (42,3), com
    limite numérico dos dois lados (não casa dentro de outro número);
  • listas: cada elemento é auditado separadamente;
  • valores vazios ('' ou null) são registrados à parte, não como ausentes.

Não altera nada: gerar_embeddings.py fica como está (decisão registrada no
relatório — corrigir o chunking invalidaria o baseline e a pergunta R2).

Uso:
    python sprint4/avaliacao/auditar_cobertura_base.py
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parents[1]


def folhas(obj, caminho=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from folhas(v, f"{caminho}.{k}" if caminho else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from folhas(v, f"{caminho}[{i}]")
    else:
        yield caminho, obj


def variantes(valor) -> list:
    if isinstance(valor, bool):
        return [str(valor)]
    if isinstance(valor, (int, float)):
        texto = str(valor)
        return [texto, texto.replace(".", ",")]
    return [str(valor)]


def _contem(base: str, valor: str, numerico: bool) -> bool:
    """
    Números exigem limite numérico dos dois lados: sem isso, '89' casaria
    dentro de 'RS28897696' e o percentil pareceria presente na base.
    """
    import re
    if not numerico:
        return valor.lower() in base
    return re.search(r"(?<![\d.,])" + re.escape(valor) + r"(?![\d])", base) is not None


def campo_generico(caminho: str) -> str:
    """resultados[3].marcadores_geneticos[1].gene -> resultados[].marcadores_geneticos[].gene"""
    import re
    return re.sub(r"\[\d+\]", "[]", caminho)


def main() -> int:
    import chromadb

    relatorio = json.loads((RAIZ / "dados_estruturados.json").read_text(encoding="utf-8"))
    col = chromadb.PersistentClient(
        path=str(RAIZ / "sprint2" / "vetorial" / "base_vetorial")
    ).get_collection("genera_relatorio")
    base = " \n ".join(col.get(include=["documents"])["documents"]).lower()

    presentes, ausentes, vazios = [], [], []
    for caminho, valor in folhas(relatorio):
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            vazios.append(caminho)
            continue
        achou = any(_contem(base, v, numerico=isinstance(valor, (int, float))
                            and not isinstance(valor, bool))
                    for v in variantes(valor))
        (presentes if achou else ausentes).append({"campo": caminho, "valor": valor})

    ausentes_por_campo = defaultdict(list)
    for a in ausentes:
        ausentes_por_campo[campo_generico(a["campo"])].append(a)

    resumo_campos = []
    total_por_campo = defaultdict(int)
    for caminho, valor in folhas(relatorio):
        total_por_campo[campo_generico(caminho)] += 1
    for campo, itens in sorted(ausentes_por_campo.items()):
        resumo_campos.append({
            "campo": campo,
            "ausentes": len(itens),
            "ocorrencias_no_json": total_por_campo[campo],
            "exemplos": [{"campo": i["campo"], "valor": i["valor"]} for i in itens[:3]],
        })

    saida = {
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base": "sprint2/vetorial/base_vetorial (25 chunks)",
        "folhas_total": len(presentes) + len(ausentes) + len(vazios),
        "presentes": len(presentes),
        "ausentes": len(ausentes),
        "vazios_no_json": vazios,
        "ausentes_por_campo": resumo_campos,
        "ausentes_detalhe": ausentes,
    }
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = DIR / "execucoes" / f"cobertura_base_{carimbo}.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=2, default=str),
                       encoding="utf-8")

    print(f"folhas={saida['folhas_total']} presentes={saida['presentes']} "
          f"ausentes={saida['ausentes']} vazios={len(vazios)}")
    for c in resumo_campos:
        print(f"  {c['campo']}: {c['ausentes']}/{c['ocorrencias_no_json']}  ex={c['exemplos'][0]['valor']!r}")
    print(f"[cobertura] {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
