"""
Agente Especialista Genera AI

Responsável por orquestrar:
1. pergunta do usuário
2. validação por guardrails
3. contexto recuperado pelo RAG
4. construção do prompt final
5. resposta segura e rastreável
"""

from prompts import SYSTEM_PROMPT
from guardrails import verificar_guardrails, validar_contexto


def montar_contexto(trechos_recuperados: list) -> str:
    """
    Recebe uma lista de trechos recuperados pela busca semântica
    e transforma em um bloco único de contexto.
    """

    if not trechos_recuperados:
        return ""

    contexto = ""

    for i, trecho in enumerate(trechos_recuperados, start=1):
        contexto += f"\n[Fonte {i}]\n{trecho}\n"

    return contexto.strip()


def construir_prompt_final(pergunta: str, contexto: str, modo: str = "paciente") -> str:
    """
    Monta o prompt final enviado ao modelo de linguagem.
    """

    return f"""
{SYSTEM_PROMPT}

--------------------------------------------------
MODO ATUAL
--------------------------------------------------

Modo selecionado: {modo}

Se o modo for paciente:
- use linguagem simples
- explique termos difíceis
- evite excesso técnico

Se o modo for técnico:
- use linguagem mais detalhada
- mantenha precisão científica
- explique limitações da interpretação genética

--------------------------------------------------
CONTEXTO RECUPERADO DO RELATÓRIO
--------------------------------------------------

{contexto}

--------------------------------------------------
PERGUNTA DO USUÁRIO
--------------------------------------------------

{pergunta}

--------------------------------------------------
INSTRUÇÃO FINAL
--------------------------------------------------

Responda apenas com base no contexto recuperado.
Se a resposta não estiver no contexto, diga que não encontrou essa informação no relatório.
"""


def gerar_resposta_simulada(prompt_final: str) -> str:
    """
    Simula a resposta do LLM.

    Esta função existe para permitir testes sem depender de API externa.
    Na integração final, ela pode ser substituída por uma chamada real
    para OpenAI, Gemini ou outro modelo escolhido.
    """

    return """
Resumo:
Com base nos trechos recuperados do relatório, existe uma informação genética associada ao tema perguntado.

Explicação:
O relatório indica uma associação genética, mas isso não significa diagnóstico ou certeza de desenvolvimento de doença. Fatores como estilo de vida, histórico familiar e acompanhamento profissional também influenciam a interpretação.

Na prática:
Essa informação deve ser entendida como um indicativo de predisposição ou tendência, e não como uma conclusão médica definitiva.

Baseado em:
Trechos recuperados do relatório genético enviado.
"""


def responder(pergunta: str, trechos_recuperados: list, modo: str = "paciente") -> dict:
    """
    Função principal do agente.

    Retorna:
    - resposta
    - status
    - categoria
    - fontes
    """

    validacao_pergunta = verificar_guardrails(pergunta)

    if not validacao_pergunta["permitido"]:
        return {
            "status": "bloqueado",
            "categoria": validacao_pergunta["categoria"],
            "resposta": validacao_pergunta["mensagem"],
            "fontes": [],
        }

    contexto = montar_contexto(trechos_recuperados)

    validacao_contexto = validar_contexto(contexto)

    if not validacao_contexto["permitido"]:
        return {
            "status": "sem_contexto",
            "categoria": validacao_contexto["categoria"],
            "resposta": validacao_contexto["mensagem"],
            "fontes": [],
        }

    prompt_final = construir_prompt_final(
        pergunta=pergunta,
        contexto=contexto,
        modo=modo
    )

    resposta = gerar_resposta_simulada(prompt_final)

    return {
        "status": "respondido",
        "categoria": "resposta_rag",
        "resposta": resposta.strip(),
        "fontes": trechos_recuperados,
    }


if __name__ == "__main__":
    pergunta_teste = "O que meu relatório diz sobre ancestralidade?"

    trechos_teste = [
        "O relatório indica predominância de ancestralidade europeia, com contribuições menores de outras regiões.",
        "A análise de ancestralidade é baseada em marcadores genéticos comparados com populações de referência."
    ]

    resultado = responder(
        pergunta=pergunta_teste,
        trechos_recuperados=trechos_teste,
        modo="paciente"
    )

    print(resultado["resposta"])
