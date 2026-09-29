"""Testes das funções puras de curva_limiar.py, com rankings sintéticos."""

import sys
from pathlib import Path

_DIR = Path(__file__).resolve().parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

import curva_limiar as cl  # noqa: E402

PERGUNTAS = {
    "R": {"categoria": "risco", "comportamento_esperado": "respondido",
          "chunks_essenciais": ["a"], "chunks_aceitaveis": ["b"]},
    "S": {"categoria": "ausente", "comportamento_esperado": "sem_contexto",
          "chunks_essenciais": [], "chunks_aceitaveis": []},
    "G": {"categoria": "guardrail", "comportamento_esperado": "bloqueado",
          "chunks_essenciais": None, "chunks_aceitaveis": None},
}


def _res(r_rank, s_rank, g_rank=(("x", 0.9),)):
    return [{"id": "R", "top25": list(r_rank)}, {"id": "S", "top25": list(s_rank)},
            {"id": "G", "top25": list(g_rank)}]


def test_cortar_aplica_top_k_antes_do_limiar():
    ranking = [("a", 0.6), ("b", 0.55), ("c", 0.52), ("d", 0.51)]
    assert cl.cortar(ranking, 2, 0.5) == [("a", 0.6), ("b", 0.55)]
    assert cl.cortar(ranking, 4, 0.53) == [("a", 0.6), ("b", 0.55)]


def test_ponto_separa_ganho_custo_e_guardrail():
    res = _res([("z", 0.7), ("a", 0.6), ("b", 0.4)], [("q", 0.55)])
    p = cl.ponto(res, PERGUNTAS, 0.5, 3)
    assert p["respondiveis_com_essencial"] == 1
    assert p["irrelevantes_admitidos"] == 1          # "z"
    assert p["sem_resposta_com_trecho"] == ["S"]
    assert p["guardrail_com_trecho"] == ["G"]
    assert cl.ponto(res, PERGUNTAS, 0.56, 3)["sem_resposta_com_trecho"] == []


def test_separacao_detecta_sobreposicao_e_calcula_auc():
    sobrepostas = cl.separacao(_res([("a", 0.45)], [("q", 0.50)]), PERGUNTAS)
    assert sobrepostas["existe_limiar_que_separa"] is False
    assert sobrepostas["auc_separacao"] == 0.0
    separadas = cl.separacao(_res([("a", 0.70)], [("q", 0.50)]), PERGUNTAS)
    assert separadas["existe_limiar_que_separa"] is True
    assert separadas["auc_separacao"] == 1.0


def test_fronteira_descarta_ponto_dominado():
    base = {"sem_resposta_com_trecho": [], "irrelevantes_admitidos": 0}
    pontos = [
        dict(base, limiar=0.40, respondiveis_com_essencial=5, sem_resposta_com_trecho=["S"]),
        dict(base, limiar=0.45, respondiveis_com_essencial=4, sem_resposta_com_trecho=["S"]),  # dominado
        dict(base, limiar=0.50, respondiveis_com_essencial=4),
    ]
    limiares = [f["limiares"] for f in cl.fronteira(pontos)]
    assert limiares == ["0.40–0.40", "0.50–0.50"]


def test_qualidade_ranking_sem_limiar():
    res = _res([("z", 0.9), ("a", 0.8)], [("q", 0.5)])
    q = cl.qualidade_ranking(res, PERGUNTAS)
    assert q["posicao_melhor_essencial"] == {"R": 2}
    assert q["hits_at_1"] == 0 and q["hits_at_3"] == 1 and q["mrr"] == 0.5
