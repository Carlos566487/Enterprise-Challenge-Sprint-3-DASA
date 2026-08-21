# RAG Personalização — Sprint 3

## Cientista de IA · Personalização & RAG · Genera AI / Dasa / FIAP

Camada que adapta as respostas do pipeline RAG ao **perfil** e ao **histórico**
do usuário, sem permitir que o agente extrapole o conteúdo verificável do
relatório genético.

Esta camada **envolve** a Sprint 2 — não a modifica. Nenhum arquivo em
`sprint2/` foi alterado.

---

## 1. Princípio central

> A personalização atua sobre a **forma** da resposta.
> Nunca sobre o **conteúdo**.

| ✅ Pode variar por perfil | ❌ Nunca varia |
|---|---|
| Tom (acolhedor, didático, objetivo) | Fatos do relatório (doença, categoria, risco) |
| Profundidade da explicação | Valores numéricos (percentis, escores, percentuais) |
| Vocabulário (simples × técnico) | Marcadores genéticos (SNPs, genes, alelos) |
| Quantidade de trechos recuperados (`top_k`) | Veredito dos guardrails médicos |
| Ordem de apresentação | Limiar de similaridade da busca |
| Omitir introduções já vistas (continuidade) | Exigência de ancoragem no relatório |

Essas listas vivem em código (`perfis.PODE_VARIAR` / `perfis.NUNCA_VARIA`) e a
garantia de que os fatos não mudam entre perfis é verificada por teste
(`test_perfis_recebem_os_mesmos_fatos`).

---

## 2. Perfis suportados

| Perfil | `modo` no agente | `top_k` | Direção da personalização |
|---|---|---|---|
| `leigo_ansioso` | `paciente` | 3 | Tom calmo, frases curtas, risco contextualizado como tendência estatística, sem alarmismo |
| `leigo_curioso` | `paciente` | 4 | Linguagem simples com explicação do mecanismo biológico; recuperação um pouco mais ampla |
| `medico` | `tecnico` | 5 | Linguagem técnica, marcadores e escores exatamente como constam no relatório |

---

## 3. Arquitetura

```
pergunta + perfil + usuario_id
      ↓
[1] guardrails sobre a pergunta CRUA      sprint2/agente/guardrails.py
      ↓  bloqueado → retorna sem buscar e sem gastar token
[2] busca semântica (top_k do perfil)     sprint2/vetorial/buscar.py
      ↓  sem trechos → "sem_contexto"
[3] pergunta personalizada  (diretiva de forma + continuidade do histórico)
      ↓
[4] responder_com_llm()             sprint2/interface/llm_connector.py
      ↓   ← SEMPRE o caminho real (GPT-4.1 Mini). Nunca gerar_resposta_simulada()
[5] validação de ancoragem                ancoragem.py
      ↓
[6] registro no histórico                 historico.py
      ↓
contrato de saída estável (v1.0)
```

### Por que os guardrails rodam na pergunta crua

A personalização é injetada anexando uma diretiva de estilo à pergunta. Os
guardrails da Sprint 2 fazem *matching por substring*, então uma diretiva mal
redigida (contendo "tratamento", "dose", "diagnóstico"…) transformaria uma
pergunta legítima em bloqueada — um falso positivo silencioso.

Duas defesas:

1. O veredito de segurança é calculado sobre o **texto original do usuário**,
   antes de qualquer personalização.
2. `perfis.validar_diretivas()` verifica programaticamente que nenhuma diretiva
   contém termo das listas de guardrail, e dois testes travam isso como
   regressão (`test_diretivas_nao_contem_termos_de_guardrail`,
   `test_personalizacao_nao_altera_veredito_do_guardrail`).

---

## 4. Validação de ancoragem (fidelidade ao relatório)

`ancoragem.validar_ancoragem(resposta, trechos)` opera em duas camadas.

**Regra dura — decide `ancorado`.** Todo elemento factual verificável da
resposta precisa aparecer nos trechos recuperados:

- números e percentuais (`89`, `42,3%`, `1.37`)
- identificadores de SNP (`RS7903146`)
- símbolos de gene (`TCF7L2`, `BRCA2`)

São exatamente os elementos que uma alucinação inventa e que um leitor tomaria
como verdade clínica. Marcadores de lista (`1.`, `2)`) são removidos antes da
extração para não virarem falso positivo.

**Score suave — apenas informativo.** Proporção de palavras de conteúdo da
resposta presentes no contexto. Nunca decide bloqueio: o system prompt da
Sprint 2 *obriga* o agente a contextualizar risco e orientar acompanhamento
profissional, e esse texto de enquadramento legitimamente não aparece nos
trechos.

### Política de ancoragem

| Valor | Comportamento |
|---|---|
| `"sinalizar"` (padrão) | Devolve a resposta com `ancoragem.ancorado = False` e a lista de termos órfãos. O dashboard decide como exibir. |
| `"bloquear"` | Substitui a resposta por uma mensagem segura e retorna `status = "nao_ancorado"`. |

O padrão é `"sinalizar"` para não descartar respostas corretas por falso
positivo. Para uso clínico real, `"bloquear"` é a postura defensável — a
escolha fica explícita no contrato em vez de escondida no código.

---

## 5. Contrato público (v1.0)

```python
from sprint3.rag_personalizacao import responder_personalizado

resultado = responder_personalizado(
    pergunta="Eu tenho risco de diabetes?",
    perfil="leigo_ansioso",        # leigo_ansioso | leigo_curioso | medico
    usuario_id="paciente-001",
    api_key=OPENAI_API_KEY,
    historico=None,                 # default: HistoricoMemoria()
    politica_ancoragem="sinalizar", # sinalizar | bloquear
)
```

### Saída

```python
{
  "versao_contrato": "1.0",
  "pergunta": str,
  "perfil": str,
  "modo_efetivo": "paciente" | "tecnico",
  "status": "respondido" | "bloqueado" | "sem_contexto" | "nao_ancorado",
  "categoria": str,              # resposta_rag | diagnostico | prescricao | ...
  "resposta": str,
  "fontes": [                    # trechos ricos, prontos para exibição
    {"conteudo": str, "secao": str, "fonte": str, "similaridade": float}
  ],
  "ancoragem": {
    "ancorado": bool | None,
    "termos_nao_ancorados": [str],
    "score_sobreposicao": float, # 0.0–1.0
    "politica": str,
  },
  "historico_resumo": {
    "total_interacoes": int,
    "primeira_interacao": str | None,
    "ultima_interacao": str | None,
    "secoes_recorrentes": [str],
    "perfil_predominante": str | None,
    "usuario_recorrente": bool,
  },
}
```

**Garantias.** As chaves de primeiro nível são estáveis em todos os caminhos —
bloqueio, sem contexto, resposta e falha de ancoragem devolvem o mesmo formato
(travado por `test_contrato_estavel_em_todos_os_caminhos`). Mudança de formato
implica subir `versao_contrato`.

**Erros.** `ValueError` para perfil desconhecido, pergunta vazia ou política
inválida — falha explícita, sem fallback silencioso.

**Custo.** Perguntas bloqueadas por guardrail não chamam a busca nem a API.

---

## 6. Histórico — ponto de troca para o Integrante 1

A persistência real é responsabilidade do Integrante 1 e **ainda não existe**.
Esta camada entrega duas implementações provisórias por trás de uma interface
estável (`historico.RepositorioHistorico`):

| Implementação | Uso |
|---|---|
| `HistoricoMemoria` (padrão) | Testes, sessão única do Streamlit, demonstração |
| `HistoricoJSON` | Simula continuidade entre sessões; grava em `dados/historico.json` (git-ignored) |

Quando a persistência real ficar pronta, **nada neste diretório muda**. Basta a
classe do Integrante 1 implementar os quatro métodos e ser injetada:

```python
# hoje
responder_personalizado(..., historico=HistoricoMemoria())

# depois, sem tocar em personalizador.py
responder_personalizado(..., historico=HistoricoPostgres(conn))
```

Métodos exigidos:

```python
registrar(usuario_id, pergunta, perfil, secoes_citadas) -> None
listar(usuario_id, limite=None)                         -> list[dict]
resumir(usuario_id)                                     -> dict
limpar(usuario_id)                                      -> None   # LGPD: exclusão
```

**Privacidade.** As implementações atuais gravam pergunta, perfil e seções
citadas — **nunca** o texto da resposta nem dados genéticos brutos. A
implementação real deve manter no mínimo essa restrição, com criptografia em
repouso (LGPD Art. 11). Travado por `test_historico_nao_grava_texto_da_resposta`.

**Como o histórico personaliza.** Apenas continuidade: quando há interação
anterior, a diretiva `[Continuidade]` pede para não repetir introduções.
Nenhum fato do histórico entra no prompt — o único conteúdo factual permitido
vem dos trechos recuperados da base vetorial.

---

## 7. Relação com `sprint3/nlp/`

`sprint3/nlp/` é uma **integração paralela, ainda não coordenada** — não é
dependência desta camada. Este pacote não importa nada de lá, e o contrato
acima não contém nenhuma chave daquele módulo (`resposta_final`, `metricas_*`,
`resumo_interacoes`) — travado por
`test_contrato_nao_depende_do_formato_do_sprint3_nlp`.

Dois pontos em aberto para alinhar com a autora daquele módulo:

1. **`sprint3/nlp/integracao/agente_nlp.py` chama `agente_sprint2.responder()`
   diretamente**, ou seja, opera sobre `gerar_resposta_simulada()` — texto de
   placeholder — e não sobre a resposta real do GPT-4.1 Mini que a interface já
   usa via `llm_connector.responder_com_llm()`. Esta camada usa o caminho real.
2. **Existem hoje dois formatos de saída concorrentes** para o dashboard. Falta
   decidir qual é a fonte de verdade, ou compor as duas camadas explicitamente
   (a simplificação de linguagem poderia consumir o `resposta` deste contrato).

---

## 8. Como executar

```bash
# testes (não exigem OPENAI_API_KEY nem base vetorial)
pytest sprint3/rag_personalizacao/ -v

# base vetorial, para o teste de integração real deixar de ser pulado
python sprint2/pipeline/pipeline_completo.py
```

## 9. Estrutura

```
sprint3/rag_personalizacao/
├── __init__.py                     superfície pública do pacote
├── perfis.py                       perfis + regras de personalização
├── historico.py                    interface + backends (ponto de troca)
├── ancoragem.py                    validação de fidelidade ao relatório
├── personalizador.py               orquestração + contrato
├── test_personalizacao.py          32 testes
└── README_rag_personalizacao.md    este arquivo
```
