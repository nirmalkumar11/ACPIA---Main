"""Tool: notify officers immediately for urgent cases.

For the hackathon MVP this just logs the alert. Swap the body of
notify_officers() for a real integration (SMS gateway, dashboard push,
email, etc.) when moving past the demo stage.
"""

from datetime import datetime


def notify_officers(risk_score: int, reason: list[str], case_summary: str) -> dict:
    """Sends an immediate alert to on-duty officers for an urgent case.

    Args:
        risk_score: The calculated risk score (0-100).
        reason: List of short reasons the case was flagged urgent.
        case_summary: A one-line description of the complaint.

    Returns:
        A dict confirming the alert was dispatched, with a timestamp.
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    print(
        f"\n[ALERT {timestamp}] URGENT CASE (risk_score={risk_score})\n"
        f"  Summary: {case_summary}\n"
        f"  Reasons: {', '.join(reason)}\n"
        f"  -> Officers notified.\n"
    )
    return {"alert_sent": True, "timestamp": timestamp}
