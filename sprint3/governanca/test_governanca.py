"""
sprint3/governanca/test_governanca.py
Genera AI · Dasa · FIAP Sprint 3

Testes unitários do módulo de governança — sem dependência de API key.

Execução:
    pytest sprint3/governanca/test_governanca.py -v
"""

import pytest
from sprint3.governanca.disclaimers import DISCLAIMERS, formatar_com_disclaimer
from sprint3.governanca.revisor_linguagem import (
    revisar_linguagem,
    auditar_resposta,
    RegrasAlarmismo,
)


# ===========================================================================
# Testes de disclaimers
# ===========================================================================

class TestDisclaimers:

    def test_todas_as_chaves_presentes(self):
        chaves_esperadas = {
            "banner",
            "sufixo_risco",
            "sidebar_privacidade",
            "bloqueio_diagnostico",
            "rodape_exportacao",
        }
        assert chaves_esperadas.issubset(set(DISCLAIMERS.keys()))

    def test_banner_menciona_medico(self):
        assert "médico" in DISCLAIMERS["banner"]

    def test_sufixo_risco_menciona_diagnostico(self):
        assert "diagnóstico" in DISCLAIMERS["sufixo_risco"]

    def test_formatar_com_disclaimer_anexa_sufixo(self):
        resposta = "Você tem predisposição a diabetes."
        resultado = formatar_com_disclaimer(resposta, "sufixo_risco")
        assert "não constituem diagnóstico" in resultado
        assert resposta in resultado

    def test_formatar_nao_duplica_aviso(self):
        resposta = "Texto que já contém: não constituem diagnóstico médico."
        resultado = formatar_com_disclaimer(resposta, "sufixo_risco")
        # O aviso não deve aparecer duas vezes
        assert resultado.count("não constituem diagnóstico") == 1

    def test_formatar_com_force_duplica(self):
        resposta = "Texto que já contém: não constituem diagnóstico médico."
        resultado = formatar_com_disclaimer(resposta, "sufixo_risco", force=True)
        assert resultado.count("não constituem diagnóstico") == 2

    def test_contexto_invalido_lanca_exception(self):
        with pytest.raises(ValueError, match="não reconhecido"):
            formatar_com_disclaimer("texto", "contexto_inexistente")


# ===========================================================================
# Testes do revisor de linguagem
# ===========================================================================

class TestRevisorLinguagem:

    def test_substitui_vai_desenvolver(self):
        texto = "Você vai desenvolver diabetes tipo 2."
        revisado, log = revisar_linguagem(texto)
        assert "vai desenvolver" not in revisado
        assert "predisposição" in revisado
        assert len(log) > 0

    def test_substitui_risco_altissimo(self):
        texto = "Há risco altíssimo de doença cardíaca."
        revisado, log = revisar_linguagem(texto)
        assert "altíssimo" not in revisado
        assert len(log) > 0

    def test_substitui_alto_risco(self):
        texto = "Este marcador indica alto risco para sua saúde."
        revisado, log = revisar_linguagem(texto)
        assert "alto risco" not in revisado

    def test_adiciona_contexto_quando_ausente(self):
        # Frase com "risco" mas sem nenhum contexto de especialista/predisposição
        texto = "O marcador SNP rs7903146 indica risco para diabetes."
        revisado, log = revisar_linguagem(texto)
        assert "consulte" in revisado.lower() or "especialista" in revisado.lower()

    def test_nao_adiciona_contexto_quando_presente(self):
        texto = (
            "Segundo o relatório, o marcador rs7903146 indica predisposição "
            "a diabetes. Consulte um especialista para avaliação clínica."
        )
        revisado, log = revisar_linguagem(texto)
        # Não deve ter o sufixo duplicado
        assert revisado.count("consulte um especialista") <= 1

    def test_texto_seguro_nao_alterado(self):
        texto = (
            "Segundo o relatório, você apresenta marcadores genéticos "
            "associados a maior predisposição a diabetes tipo 2. "
            "Consulte um médico geneticista para interpretação clínica."
        )
        revisado, log = revisar_linguagem(texto)
        assert log == [] or all("contexto" not in entry for entry in log)

    def test_idempotente(self):
        texto = "Você vai desenvolver diabetes com risco altíssimo."
        revisado1, _ = revisar_linguagem(texto)
        revisado2, log2 = revisar_linguagem(revisado1)
        # Segunda passagem não deve gerar mais alterações de alarmismo
        alarmismo_log2 = [e for e in log2 if "[alarmismo]" in e]
        assert alarmismo_log2 == []

    def test_auditoria_aprovado(self):
        texto = (
            "Segundo o relatório, você apresenta predisposição a hipertensão. "
            "Consulte um especialista."
        )
        relatorio = auditar_resposta(texto)
        assert relatorio["aprovado"] is True
        assert relatorio["numero_de_alteracoes"] == 0

    def test_auditoria_reprovado(self):
        texto = "Você vai desenvolver câncer com risco altíssimo."
        relatorio = auditar_resposta(texto)
        assert relatorio["aprovado"] is False
        assert relatorio["numero_de_alteracoes"] > 0
        assert len(relatorio["alteracoes"]) > 0
        assert relatorio["texto_revisado"] != texto

    def test_regras_customizadas(self):
        regras_customizadas = RegrasAlarmismo(substituicoes=[
            (r"perigo extremo", "atenção recomendada"),
        ])
        texto = "Este SNP representa perigo extremo."
        revisado, log = revisar_linguagem(texto, regras=regras_customizadas)
        assert "perigo extremo" not in revisado
        assert "atenção recomendada" in revisado
