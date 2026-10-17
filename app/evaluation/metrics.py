"""Small, explainable metrics for source routing and grounded answers."""

import re


CITATION_PATTERN = re.compile(r"\[(?:D|S)\d+\]")


def evaluate_response(
    *,
    expected_source_type: list[str],
    expected_source_contains: str,
    response: dict,
) -> dict:
    """Score one answer using expected source type, source hit, and citation presence."""
    expected_marker = expected_source_contains.casefold()
    sources = response.get("sources", [])
    source_hit = any(
        expected_marker in str(source.get("title", "")).casefold()
        or expected_marker in str(source.get("source_path", "")).casefold()
        for source in sources
    )
    expected_types = set(expected_source_type)
    actual_types = set(response.get("source_type", []))
    routing_correct = expected_types == actual_types
    cited = bool(CITATION_PATTERN.search(str(response.get("answer", ""))))
    citations_present = cited if sources else not cited
    return {
        "expected_source_type": sorted(expected_types),
        "actual_source_type": sorted(actual_types),
        "expected_source_contains": expected_source_contains,
        "source_hit": source_hit,
        "routing_correct": routing_correct,
        "citations_present": citations_present,
        "pass": source_hit and routing_correct and citations_present,
    }


def summarize_evaluation(results: list[dict]) -> dict:
    """Return aggregate rates without hiding individual misses."""
    count = len(results)
    if not count:
        return {
            "case_count": 0,
            "source_hit_rate": 0.0,
            "routing_accuracy": 0.0,
            "citation_rate": 0.0,
            "pass_rate": 0.0,
        }
    return {
        "case_count": count,
        "source_hit_rate": round(sum(item["source_hit"] for item in results) / count, 3),
        "routing_accuracy": round(sum(item["routing_correct"] for item in results) / count, 3),
        "citation_rate": round(sum(item["citations_present"] for item in results) / count, 3),
        "pass_rate": round(sum(item["pass"] for item in results) / count, 3),
    }
