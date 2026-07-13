"""Tool: search the mock missing-child registry."""

import json
from pathlib import Path

_DATA_PATH = Path(__file__).parent.parent / "mock_data" / "missing_children.json"


def search_missing_child_records(location: str, status: str = "missing") -> dict:
    """Searches the missing-child registry for records near a given location.

    Args:
        location: The location to search near (e.g. "Chennai").
        status: Record status to filter by, "missing" or "found". Defaults to "missing".

    Returns:
        A dict with a "records" list of matching missing-child entries.
    """
    with open(_DATA_PATH) as f:
        records = json.load(f)

    matches = [
        r
        for r in records
        if location.lower() in r["last_seen_location"].lower()
        and r["status"].lower() == status.lower()
    ]
    return {"records": matches, "count": len(matches)}
