# Política de Governança de IA — Genera AI (Sprint 4)

## 1. Objetivo e escopo
Esta política governa o fluxo de IA do Genera AI, do recebimento da pergunta à recuperação RAG, geração, guardrails/NLP e resposta. O objetivo é assegurar rastreabilidade, explicabilidade, segurança e tratamento responsável de dados.

## 2. Dados e LGPD
O projeto pode tratar dados genéticos e de saúde, portanto adota minimização e privacy by design. PDFs, uploads, `.env`, base vetorial e logs não são versionados. A aplicação deve processar somente dados necessários à finalidade educacional/demonstrativa. Dados reais só devem ser usados com base legal e controles adequados; para demonstração e evidências, usar dados simulados.

### Ciclo de vida
1. **Coleta:** entrada do relatório/pergunta estritamente necessária.
2. **Processamento:** extração, embeddings, recuperação semântica e geração.
3. **Armazenamento:** artefatos locais necessários; segredos em variáveis de ambiente.
4. **Observabilidade:** por padrão, logs persistem hashes, IDs pseudonimizados, status, fontes por hash, latência e erros — não o conteúdo sensível.
5. **Retenção/descarte:** uploads e logs devem ser removidos ao fim da finalidade ou conforme política operacional definida pelo controlador.

## 3. Rastreabilidade e logging
Cada execução recebe `request_id`, `event_id`, timestamp UTC e pseudônimo de sessão. São registrados status, duração, hashes da pergunta/resposta e hashes das fontes recuperadas. O conteúdo integral é desabilitado por padrão (`GOVERNANCE_LOG_CONTENT=false`). Para evidências acadêmicas com dados simulados, pode ser habilitado explicitamente.

## 4. Explicabilidade
A resposta é vinculada aos trechos recuperados pelo RAG. A trilha registra a quantidade e hashes das fontes, permitindo verificar quais evidências participaram da geração sem expor conteúdo sensível no log padrão. A aplicação já possui validação de ancoragem para bloquear fatos não sustentados pelo contexto.

## 5. Monitoramento e alertas
São acompanhados: execuções, sucessos, falhas, bloqueios, taxa de sucesso, latência média, última execução e último erro. Falhas do pipeline e latência acima do limiar geram alertas estruturados em `alerts.jsonl`.

## 6. Segurança
Chaves de API devem permanecer em `.env`/variáveis de ambiente e nunca no Git. Logs e bases locais não devem ser versionados. Exceções expostas ao usuário devem evitar segredos e detalhes internos.

## 7. Automação/RPA
O pipeline de embeddings e indexação é uma automação reproduzível. A Sprint 4 acrescenta rastreabilidade de início, conclusão, duração, volume de chunks e falhas, permitindo operação monitorada.

## 8. Incidentes
Falhas são registradas e classificadas. Em incidente envolvendo dados, interromper o processamento quando necessário, preservar evidências técnicas sem ampliar exposição, revogar/rotacionar credenciais afetadas e avaliar as obrigações aplicáveis de comunicação.

## 9. Limitações e supervisão humana
O Genera AI é informativo e não substitui aconselhamento médico ou genético profissional. Respostas dependem do relatório e da recuperação de contexto. Resultados de alto impacto devem ser revisados por pessoa qualificada.

## 10. Responsabilidades
Governança/RPA mantém política, trilha, monitoramento e evidências; IA/PLN avalia qualidade e consistência; Deploy protege configuração e disponibilidade; Documentação consolida README, vídeo e entrega.
