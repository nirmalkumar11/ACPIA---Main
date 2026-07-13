"""Tool: link entities (phone, address, suspect) across cases and query relationships."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from database.neo4j import graph_store  # noqa: E402


def link_entity_to_cases(entity: str, case_ids: list[str]) -> dict:
    """Records that an entity (a suspect name, phone number, or address) appears in given cases.

    Call this once per entity you find while cross-referencing evidence, so the
    system can later tell you which other cases share that same entity.

    Args:
        entity: The entity value, e.g. "John" or "9876543210" or "12 XYZ Street, Chennai".
        case_ids: List of case IDs this entity was found in (e.g. ["CASE101", "CASE305"]).

    Returns:
        A dict confirming what was linked.
    """
    for case_id in case_ids:
        graph_store.link(entity, case_id)
    return {"entity": entity, "linked_cases": case_ids}


def get_relationships() -> dict:
    """Returns every entity that connects two or more cases, and which cases it connects.

    Call this after linking entities to retrieve the full relationship picture
    for the summarization step.

    Returns:
        A dict mapping each shared entity to the list of case IDs it appears in.
    """
    return graph_store.all_links()
