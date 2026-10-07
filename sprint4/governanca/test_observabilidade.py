from sprint4.governanca import observabilidade as o


def test_pseudonymization_deterministic_and_not_plain():
    a = o.pseudonymize("sessao-123")
    b = o.pseudonymize("sessao-123")

    assert a == b
    assert a != "sessao-123"
    assert len(a) == 16


def test_content_disabled_by_default():
    assert o._safe_content("dado genetico") is None


def test_metrics():
    before = o.metrics_snapshot()["executions"]

    o.record_execution("respondido", 100)

    metrics = o.metrics_snapshot()

    assert metrics["executions"] == before + 1
    assert metrics["success"] >= 1


def test_audit_has_trace_fields(tmp_path):
    original_audit_file = o.AUDIT_FILE

    try:
        o.AUDIT_FILE = tmp_path / "audit.jsonl"

        event = o.audit_event(
            event_type="test",
            session_id="abc",
            request_id="req",
            question="q",
            response="r",
            sources=["fonte"],
        )

        assert event["event_id"]
        assert event["timestamp_utc"]
        assert event["session_pseudonym"] != "abc"

        # Privacy by design:
        # conteúdo sensível não deve aparecer em texto puro no log padrão.
        assert event["question"] is None
        assert event["question_sha256"]

        # O evento precisa realmente ter sido persistido.
        assert o.AUDIT_FILE.exists()

        with o.AUDIT_FILE.open("r", encoding="utf-8") as file:
            persisted_event = file.readline()

        assert event["event_id"] in persisted_event

    finally:
        o.AUDIT_FILE = original_audit_file