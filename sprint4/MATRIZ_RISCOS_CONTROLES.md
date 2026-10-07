# Matriz de Riscos e Controles — Genera AI

| Risco | Impacto | Controle | Evidência |
|---|---|---|---|
| Exposição de dado genético em log | Alto | Conteúdo desabilitado por padrão; hashes e pseudonimização | `observabilidade.py` + audit log |
| Alucinação | Alto | RAG + guardrails + validação de ancoragem | testes Sprint 2/3 + fontes |
| Falha do pipeline | Alto | captura de exceção + alerta estruturado | `alerts.jsonl` |
| Latência anormal | Médio | medição por execução + limiar de alerta | métricas/audit log |
| Vazamento de API key | Alto | `.env` ignorado pelo Git | `.gitignore` |
| Falta de rastreabilidade | Alto | request/event IDs, UTC, sessão pseudonimizada | `audit.jsonl` |
| Base vetorial ausente/corrompida | Médio | tratamento de falha + pipeline reproduzível | pipeline + alerta |
