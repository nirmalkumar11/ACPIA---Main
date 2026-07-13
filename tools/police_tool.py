"""Tool: search mock police FIR (First Information Report) records."""

import json
from pathlib import Path

_DATA_PATH = Path(__file__).parent.parent / "mock_data" / "police_records.json"


def find_related_firs(location: str, suspect: str = "", phone: str = "") -> dict:
    """Finds police FIRs related to a location, and optionally a suspect or phone number.

    Args:
        location: The location to search near (e.g. "Chennai").
        suspect: Optional suspect name to match.
        phone: Optional phone number to match.

    Returns:
        A dict with a "records" list of matching FIRs.
    """
    with open(_DATA_PATH) as f:
        records = json.load(f)

    matches = []
    for r in records:
        location_match = location.lower() in r["location"].lower()
        suspect_match = (not suspect) or suspect.lower() == r["suspect"].lower()
        phone_match = (not phone) or phone == r["phone"]
        if location_match and suspect_match and phone_match:
            matches.append(r)

    return {"records": matches, "count": len(matches)}
