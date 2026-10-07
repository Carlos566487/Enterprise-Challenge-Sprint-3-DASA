"""RPA monitorado para reindexação do relatório — Sprint 4."""

from pathlib import Path
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from sprint4.governanca.observabilidade import audit_event, alert
from sprint2.pipeline.pipeline_completo import executar_pipeline


def executar(caminho: Path):
    caminho = Path(caminho)
    rid = str(uuid.uuid4())
    start = time.perf_counter()

    try:
        # Validação da entrada antes de executar o pipeline
        if not caminho.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {caminho}"
            )

        audit_event(
            event_type="rpa_job",
            request_id=rid,
            status="started",
            details={"input_file": caminho.name}
        )

        executar_pipeline(caminho)

        audit_event(
            event_type="rpa_job",
            request_id=rid,
            status="success",
            duration_ms=(time.perf_counter() - start) * 1000
        )

        return 0

    except Exception as exc:
        duration_ms = (time.perf_counter() - start) * 1000

        audit_event(
            event_type="rpa_job",
            request_id=rid,
            status="failed",
            duration_ms=duration_ms,
            details={
                "input_file": caminho.name,
                "error_type": type(exc).__name__,
                "error_message": str(exc)
            }
        )

        alert(
            "RPA_PIPELINE_FAILURE",
            "critical",
            "Falha na automação de embeddings/indexação",
            rid,
            {"error_type": type(exc).__name__}
        )

        raise


if __name__ == "__main__":
    caminho = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else ROOT / "dados_estruturados.json"
    )

    executar(caminho)