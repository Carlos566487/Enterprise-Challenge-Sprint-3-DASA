"""
sprint3/governanca — Módulo de Governança e Comunicação Responsável
Genera AI · Dasa · FIAP Sprint 3

Autor: Carlos Eduardo (RM566487)
Responsabilidade: Governança, Comunicação Responsável & Documentação

Exporta:
  - DISCLAIMERS            dict com textos de aviso por contexto
  - revisar_linguagem()    pós-processador que aplica as regras de linguagem responsável
  - formatar_com_disclaimer()  utilitário de integração para o agente/interface
"""

from .disclaimers import DISCLAIMERS, formatar_com_disclaimer
from .revisor_linguagem import revisar_linguagem

__all__ = ["DISCLAIMERS", "formatar_com_disclaimer", "revisar_linguagem"]
