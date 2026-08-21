"""
Histórico de Interações — Sprint 3 / Genera AI / Dasa
Cientista de IA — Personalização & RAG

⚠️  PONTO DE TROCA PARA A PERSISTÊNCIA REAL (Integrante 1)
─────────────────────────────────────────────────────────────────────────────
A persistência real de histórico é responsabilidade do Integrante 1 e ainda
não existe. Este módulo entrega duas implementações provisórias
(memória e JSON local) por trás de uma interface estável.

Quando a persistência real ficar pronta, NADA neste diretório precisa mudar
além desta linha de decisão: basta a classe do Integrante 1 implementar os
quatro métodos de RepositorioHistorico e ser passada como parâmetro
`historico=` para responder_personalizado().

    # hoje
    responder_personalizado(..., historico=HistoricoMemoria())

    # depois, sem tocar em personalizador.py
    responder_personalizado(..., historico=HistoricoPostgres(conn))

Contrato mínimo esperado da implementação real:
    registrar(usuario_id, pergunta, perfil, secoes_citadas) -> None
    listar(usuario_id, limite=None)                         -> list[dict]
    resumir(usuario_id)                                     -> dict
    limpar(usuario_id)                                      -> None

Nota de privacidade (LGPD Art. 11):
    Estas implementações gravam a PERGUNTA e as SEÇÕES citadas, mas nunca o
    texto completo da resposta nem dados genéticos brutos. A implementação
    real deve manter no mínimo essa restrição, com criptografia em repouso.
"""

import json
from abc import ABC, abstractmethod
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────────────────────────────────────

class RepositorioHistorico(ABC):
    """
    Interface que qualquer backend de histórico deve implementar.

    A camada de personalização depende APENAS desta interface — nunca de uma
    implementação concreta. É isso que torna a troca pela persistência real
    do Integrante 1 uma mudança de uma linha.
    """

    @abstractmethod
    def registrar(
        self,
        usuario_id: str,
        pergunta: str,
        perfil: str,
        secoes_citadas: list,
    ) -> None:
        """Grava uma interação. Não grava o texto da resposta (privacidade)."""

    @abstractmethod
    def listar(self, usuario_id: str, limite: int = None) -> list:
        """Retorna as interações do usuário, da mais antiga para a mais recente."""

    @abstractmethod
    def resumir(self, usuario_id: str) -> dict:
        """Retorna um resumo agregado usado para personalizar a resposta."""

    @abstractmethod
    def limpar(self, usuario_id: str) -> None:
        """Apaga o histórico do usuário (direito de exclusão — LGPD)."""


def _agora_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _resumir_interacoes(interacoes: list) -> dict:
    """
    Agrega uma lista de interações em um resumo.

    O resumo carrega apenas metadados (contagens, seções, perfis) — nunca
    conteúdo clínico. É o que a personalização usa para decidir se aplica a
    diretiva de continuidade.
    """
    if not interacoes:
        return {
            "total_interacoes": 0,
            "primeira_interacao": None,
            "ultima_interacao": None,
            "secoes_recorrentes": [],
            "perfil_predominante": None,
            "usuario_recorrente": False,
        }

    secoes = Counter()
    perfis = Counter()

    for item in interacoes:
        for secao in item.get("secoes_citadas", []):
            secoes[secao] += 1
        perfil = item.get("perfil")
        if perfil:
            perfis[perfil] += 1

    return {
        "total_interacoes": len(interacoes),
        "primeira_interacao": interacoes[0].get("timestamp"),
        "ultima_interacao": interacoes[-1].get("timestamp"),
        "secoes_recorrentes": [s for s, _ in secoes.most_common(5)],
        "perfil_predominante": perfis.most_common(1)[0][0] if perfis else None,
        "usuario_recorrente": len(interacoes) > 0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# IMPLEMENTAÇÃO 1 — MEMÓRIA (padrão; some ao fim do processo)
# ─────────────────────────────────────────────────────────────────────────────

class HistoricoMemoria(RepositorioHistorico):
    """
    Histórico em memória. Padrão da camada de personalização.

    Adequado para: testes, sessão única do Streamlit, demonstração.
    Não adequado para: continuidade entre sessões (some ao reiniciar).
    """

    def __init__(self):
        self._dados = {}

    def registrar(self, usuario_id, pergunta, perfil, secoes_citadas):
        self._dados.setdefault(usuario_id, []).append({
            "usuario_id": usuario_id,
            "pergunta": pergunta,
            "perfil": perfil,
            "secoes_citadas": list(secoes_citadas),
            "timestamp": _agora_iso(),
        })

    def listar(self, usuario_id, limite=None):
        itens = list(self._dados.get(usuario_id, []))
        return itens[-limite:] if limite else itens

    def resumir(self, usuario_id):
        return _resumir_interacoes(self.listar(usuario_id))

    def limpar(self, usuario_id):
        self._dados.pop(usuario_id, None)


# ─────────────────────────────────────────────────────────────────────────────
# IMPLEMENTAÇÃO 2 — JSON LOCAL (simula persistência entre sessões)
# ─────────────────────────────────────────────────────────────────────────────

class HistoricoJSON(RepositorioHistorico):
    """
    Histórico persistido em um arquivo JSON local.

    Existe para simular continuidade entre sessões enquanto a persistência
    real não chega. NÃO é adequada para produção: sem criptografia, sem
    controle de concorrência, sem isolamento entre usuários no disco.

    O arquivo padrão fica em sprint3/rag_personalizacao/dados/historico.json
    e está coberto pelo .gitignore do diretório.
    """

    def __init__(self, caminho=None):
        if caminho is None:
            caminho = Path(__file__).parent / "dados" / "historico.json"
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)

    def _carregar(self) -> dict:
        if not self.caminho.exists():
            return {}
        try:
            with open(self.caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # Arquivo corrompido não pode derrubar a resposta ao usuário:
            # trata como histórico vazio e segue.
            return {}

    def _salvar(self, dados: dict) -> None:
        with open(self.caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def registrar(self, usuario_id, pergunta, perfil, secoes_citadas):
        dados = self._carregar()
        dados.setdefault(usuario_id, []).append({
            "usuario_id": usuario_id,
            "pergunta": pergunta,
            "perfil": perfil,
            "secoes_citadas": list(secoes_citadas),
            "timestamp": _agora_iso(),
        })
        self._salvar(dados)

    def listar(self, usuario_id, limite=None):
        itens = self._carregar().get(usuario_id, [])
        return itens[-limite:] if limite else itens

    def resumir(self, usuario_id):
        return _resumir_interacoes(self.listar(usuario_id))

    def limpar(self, usuario_id):
        dados = self._carregar()
        dados.pop(usuario_id, None)
        self._salvar(dados)
