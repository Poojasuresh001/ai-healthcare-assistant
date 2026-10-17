"""Evaluate synthetic source routing, retrieval hits and citation coverage."""

import json
from pathlib import Path
import sys

from app.agents.graph import AssistantService
from app.config import PROJECT_ROOT
from app.evaluation.metrics import evaluate_response, summarize_evaluation
from app.services.dependencies import get_chat_service


CASES_FILE = PROJECT_ROOT / "evaluations" / "rag_cases.json"
REPORT_FILE = PROJECT_ROOT / "reports" / "rag_evaluation.json"


def main() -> int:
    cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    service: AssistantService = get_chat_service()
    results = []

    for index, case in enumerate(cases, start=1):
        response = service.ask(
            case["question"],
            session_id=f"evaluation-{index}",
            document_type=case.get("document_type"),
        )
        score = evaluate_response(
            expected_source_type=case["expected_source_type"],
            expected_source_contains=case["expected_source_contains"],
            response=response,
        )
        results.append(
            {
                "question": case["question"],
                "answer": response["answer"],
                "sources": response["sources"],
                **score,
            }
        )

    report = {"summary": summarize_evaluation(results), "cases": results}
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary = report["summary"]
    print(f"Evaluation cases: {summary['case_count']}")
    print(f"Source hit rate: {summary['source_hit_rate']:.0%}")
    print(f"Routing accuracy: {summary['routing_accuracy']:.0%}")
    print(f"Citation coverage: {summary['citation_rate']:.0%}")
    print(f"Pass rate: {summary['pass_rate']:.0%}")
    print(f"Report written to: {REPORT_FILE}")
    return 0 if summary["pass_rate"] == 1.0 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(
            f"Evaluation failed ({type(error).__name__}). Verify the Chroma index and local Gemini configuration.",
            file=sys.stderr,
        )
        raise SystemExit(1)
