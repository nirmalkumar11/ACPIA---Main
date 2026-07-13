"""Tool: search previous cases in the mock case database."""

import json
from pathlib import Path

_DATA_PATH = Path(__file__).parent.parent / "mock_data" / "cases.json"


def find_similar_cases(location: str, case_type: str = "") -> dict:
    """Finds previous cases that share a location and, optionally, a case type.

    Use this to check whether a new complaint matches a pattern seen before
    (e.g. repeated missing-child reports from the same area).

    Args:
        location: The location mentioned in the complaint (e.g. "Chennai").
        case_type: Optional case type filter, one of: missing_child, abuse,
            trafficking, neglect, cyber_exploitation. Leave empty to match any type.

    Returns:
        A dict with a "matches" list of case records that matched.
    """
    with open(_DATA_PATH) as f:
        cases = json.load(f)

    matches = [
        c
        for c in cases
        if location.lower() in c["location"].lower()
        and (not case_type or case_type.lower() == c["case_type"].lower())
    ]
    return {"matches": matches, "count": len(matches)}
