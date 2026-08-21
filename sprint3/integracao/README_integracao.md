# Integração RAG Personalizado + NLP — Sprint 3

## Cientista de IA · Personalização & RAG · Genera AI / Dasa / FIAP

Este módulo compõe duas camadas que já existiam separadas no repositório,
**sem modificar nenhuma das duas**:

| Camada | Origem | O que entrega |
|---|---|---|
| Personalização + RAG | `sprint3/rag_personalizacao/` | Resposta **real** do GPT-4.1 Mini, personalizada por perfil, validada contra o relatório |
| Simplificação de linguagem | `sprint3/nlp/nlp_simplificacao.py` | Função **pura**: texto técnico → texto simples + métricas |

---

## 1. Por que este módulo mora aqui, e não dentro dos outros dois

O contrato de `sprint3/rag_personalizacao/` tem a independência de
`sprint3/nlp/` como garantia explícita, travada pelo teste
`test_contrato_nao_depende_do_formato_do_sprint3_nlp`. Colocar o adaptador lá
dentro criaria exatamente a dependência que aquele pacote promete não ter.

A dependência aponta em uma direção só:

```
sprint3/integracao/  --depende-->  sprint3/rag_personalizacao/
                     --depende-->  sprint3/nlp/  (apenas a função pura)
```

Nenhum dos dois depende deste módulo. Apagar este diretório não afeta nenhum
dos outros dois.

**`sprint3/nlp/` não é modificado em nada.** Importamos apenas
`simplificar_texto`, exatamente como `sprint3/interface/app.py:117` já faz.

---

## 2. As três regras de segurança

### Regra 1 — Nunca simplifica mensagem de guardrail

A simplificação só roda quando `status == "respondido"`. As mensagens de
recusa (`bloqueado`, `sem_contexto`, `nao_ancorado`) são texto aprovado por
governança; parafraseá-las seria adulterar conteúdo revisado.

### Regra 2 — Nunca simplifica para o perfil médico

Quando `modo_efetivo == "tecnico"`, a resposta passa intacta. Trocar
"genótipo" por "informações do DNA" destrói a precisão de que o profissional
precisa.

### Regra 3 — Revalida a ancoragem depois de simplificar

Este é o ganho central do adaptador. A simplificação reescreve termos **depois**
da validação original — ou seja, sem esta regra, **o texto exibido ao usuário
não é o texto que foi validado**.

O adaptador roda `validar_ancoragem()` novamente sobre o texto já simplificado.
Se a reescrita perder ou inventar número, SNP ou gene, o adaptador **devolve o
texto original** e registra `motivo: "quebrou_ancoragem"`.

---

## 3. Contrato

```python
from sprint3.integracao import responder_com_linguagem_simples

resultado = responder_com_linguagem_simples(
    pergunta="Eu tenho risco de diabetes?",
    perfil="leigo_ansioso",          # leigo_ansioso | leigo_curioso | medico
    usuario_id="paciente-001",
    api_key=OPENAI_API_KEY,
    historico=None,                   # default: HistoricoMemoria()
    politica_ancoragem="sinalizar",   # sinalizar | bloquear
)

texto_para_exibir = resultado["resposta_simplificada"]
```

### Saída

Todas as chaves do contrato v1.0 de `responder_personalizado()` são
**preservadas sem alteração** (`status`, `categoria`, `resposta`, `fontes`,
`ancoragem`, `historico_resumo`, `perfil`, `modo_efetivo`, `pergunta`,
`versao_contrato`), mais:

```python
{
  "versao_contrato_integracao": "1.0",

  "resposta_simplificada": str,
  # Texto pronto para exibição. Quando a simplificação não é aplicada, é
  # IGUAL a "resposta" — o consumidor pode sempre renderizar este campo
  # sem verificar nada antes.

  "simplificacao": {
    "aplicada": bool,
    "motivo": str,
    "metricas_original": dict,      # palavras, frases, médias
    "metricas_simplificado": dict,
    # "termos_nao_ancorados": [str]  ← presente só quando motivo == "quebrou_ancoragem"
  },
}
```

### Valores de `motivo`

| Valor | Significado |
|---|---|
| `ok` | Simplificação aplicada e revalidada |
| `perfil_tecnico` | Perfil médico — regra 2 |
| `status_nao_respondido` | Guardrail, sem contexto ou não ancorado — regra 1 |
| `quebrou_ancoragem` | Reescrita alterou os fatos — regra 3, fallback aplicado |
| `nlp_indisponivel` | `sprint3/nlp/` não importável — degrada sem quebrar |
| `texto_vazio` | Texto de entrada ou saída vazio |

---

## 4. Testes

```bash
pytest sprint3/integracao/ -v      # 19 testes
```

Cobrem os 3 perfis, pergunta bloqueada por guardrail, `sem_contexto`,
`nao_ancorado`, fallback de ancoragem quebrada, indisponibilidade do NLP,
estabilidade do contrato em todos os caminhos e integração com a função real
de `sprint3/nlp/`.

Nenhum teste exige `OPENAI_API_KEY` ou base vetorial — busca, LLM e
simplificador são injetáveis (`fn_buscar`, `fn_llm`, `fn_simplificar`).

---

## 5. Estado da adoção

O dashboard `sprint3/interface/app.py` (Integrante 1) **ainda não consome este
módulo** — ele chama `responder_com_llm()` diretamente e aplica a
simplificação por conta própria, sem personalização por perfil e sem
revalidação de ancoragem.

Adotar este adaptador daria ao dashboard, sem outras mudanças:

- perfis de usuário (hoje só há o modo binário paciente/técnico);
- validação de que a resposta não extrapola o relatório;
- garantia de que o texto **exibido** — e não só o gerado — foi validado;
- histórico por usuário através de uma interface trocável.

A decisão de adotar é do Integrante 1.
