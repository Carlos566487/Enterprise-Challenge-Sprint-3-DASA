"""
sprint3/governanca/disclaimers.py
Genera AI · Dasa · FIAP Sprint 3

Disclaimers fixos de comunicação responsável.

Estes textos são exibidos:
  1. Como banner permanente no topo da interface (Streamlit).
  2. Anexados automaticamente a respostas que envolvam risco ou predisposição.
  3. Na sidebar, ao carregar qualquer relatório.

Decisão de design (Carlos Eduardo — Governança):
  Optou-se por disclaimers contextuais em vez de um aviso genérico único,
  pois o usuário-alvo pode ser leigo e tende a ignorar avisos repetitivos.
  Cada contexto exibe apenas o aviso mais relevante, reduzindo o ruído sem
  abrir mão da proteção.
"""

# ---------------------------------------------------------------------------
# Textos canônicos
# ---------------------------------------------------------------------------

DISCLAIMERS: dict[str, str] = {
    # Exibido como banner fixo no topo da interface em toda sessão
    "banner": (
        "⚠️ Este assistente é informativo e não substitui avaliação médica. "
        "As respostas são baseadas exclusivamente no relatório genético carregado. "
        "Consulte sempre um médico geneticista."
    ),

    # Sufixo automático em qualquer resposta que mencione risco ou predisposição
    "sufixo_risco": (
        "\n\n---\n"
        "_Os dados acima refletem predisposições genéticas descritas no seu "
        "relatório — não constituem diagnóstico médico. Os percentuais e "
        "marcadores indicam tendências estatísticas populacionais. "
        "Consulte um profissional de saúde habilitado para interpretação clínica._"
    ),

    # Exibido na sidebar ao carregar um relatório
    "sidebar_privacidade": (
        "🔒 Seus dados são processados localmente e não são armazenados "
        "permanentemente. Apenas os trechos relevantes do relatório são "
        "enviados à API OpenAI para geração da resposta. Nenhuma informação "
        "pessoal é salva além da sessão ativa."
    ),

    # Resposta padrão quando o agente detecta pergunta diagnóstica
    "bloqueio_diagnostico": (
        "Não posso fornecer diagnósticos médicos. "
        "Este assistente explica os dados do seu relatório genético em "
        "linguagem acessível, mas a interpretação clínica deve ser feita "
        "por um médico geneticista. "
        "Posso te ajudar a entender o que o relatório diz sobre este tema?"
    ),

    # Rodapé de relatório exportado (PDF/texto)
    "rodape_exportacao": (
        "Gerado pelo Genera AI — ferramenta educativa. "
        "Não constitui laudo médico. Data: {data}. "
        "Relatório original: {nome_arquivo}."
    ),
}


def formatar_com_disclaimer(
    resposta: str,
    contexto: str = "sufixo_risco",
    force: bool = False,
) -> str:
    """
    Anexa o disclaimer adequado a uma resposta do agente.

    Args:
        resposta:  Texto gerado pelo LLM ou pelo agente.
        contexto:  Chave em DISCLAIMERS a ser usada como sufixo.
                   Padrão: "sufixo_risco".
        force:     Se True, anexa o disclaimer mesmo que a resposta já
                   contenha a palavra "predisposição" ou "consulte".
                   Útil para testes unitários.

    Returns:
        Texto da resposta com o disclaimer concatenado.

    Exemplo:
        >>> from sprint3.governanca import formatar_com_disclaimer
        >>> texto = formatar_com_disclaimer("Você tem predisposição a diabetes tipo 2.")
        >>> assert "não constituem diagnóstico" in texto
    """
    if contexto not in DISCLAIMERS:
        raise ValueError(
            f"Contexto '{contexto}' não reconhecido. "
            f"Opções: {list(DISCLAIMERS.keys())}"
        )

    disclaimer = DISCLAIMERS[contexto]

    # Evita duplicar o aviso se já foi incluído nesta resposta
    if not force and "não constituem diagnóstico" in resposta:
        return resposta

    return resposta + disclaimer
