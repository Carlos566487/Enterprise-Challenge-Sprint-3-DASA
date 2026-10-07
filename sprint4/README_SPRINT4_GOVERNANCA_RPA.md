# Sprint 4 — Governança & RPA

## Controles implementados
- trilha de auditoria JSONL com `event_id`, `request_id`, timestamp UTC e sessão pseudonimizada;
- hashes SHA-256 de pergunta, resposta e fontes por padrão (conteúdo sensível não é persistido);
- modo de demonstração com conteúdo somente mediante `GOVERNANCE_LOG_CONTENT=true` e dados simulados;
- latência e status das interações RAG;
- métricas de execução em memória;
- alerta estruturado para latência anormal;
- automação monitorada do pipeline de embeddings/indexação, com alerta de falha;
- logs excluídos do Git;
- Política de Governança e Matriz de Riscos.

## Executar RPA monitorado
```bash
python sprint4/rpa/executar_pipeline_monitorado.py
```

## Testar controles
```bash
pytest sprint4/governanca/test_observabilidade.py -q
```

## Evidências recomendadas
1. execução bem-sucedida do RPA;
2. `audit.jsonl` mostrando IDs/timestamp/status sem conteúdo sensível;
3. falha controlada usando caminho JSON inexistente e registro em `alerts.jsonl`;
4. interação RAG exibindo `request_id` e latência;
5. `.gitignore` comprovando que logs, PDFs, uploads e segredos não são versionados.

> Para demonstrar pergunta/trechos/resposta literalmente, use exclusivamente dados simulados e execute com `GOVERNANCE_LOG_CONTENT=true`. Em produção, mantenha `false`.
