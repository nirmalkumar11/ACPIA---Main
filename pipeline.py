"""Shared ACPIA pipeline runner.

Used by both main.py (CLI demo) and api_server.py (dashboard backend) so the
agent-running logic lives in exactly one place.
"""

import json
import logging
from datetime import datetime

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from orchestrator import root_agent
from tools.alert_tool import notify_officers

APP_NAME = "acpia"

logger = logging.getLogger("acpia")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S"))
    logger.handlers = [_handler]
    logger.propagate = False


def log_event(event) -> None:
    """Logs one ADK event: the acting agent, any tool calls/results, and any text."""
    author = getattr(event, "author", "unknown_agent")

    parts = []
    if getattr(event, "content", None) and event.content.parts:
        parts = event.content.parts

    for part in parts:
        fn_call = getattr(part, "function_call", None)
        if fn_call:
            logger.info(f"[{author}] -> calling tool `{fn_call.name}` with args={dict(fn_call.args or {})}")
            continue

        fn_response = getattr(part, "function_response", None)
        if fn_response:
            logger.info(f"[{author}] <- tool `{fn_response.name}` returned: {fn_response.response}")
            continue

        text = getattr(part, "text", None)
        if text:
            snippet = text.strip()
            if len(snippet) > 500:
                snippet = snippet[:500] + " ...[truncated]"
            logger.info(f"[{author}] output: {snippet}")


def _safe_json(value):
    """evidence_collection / entity_linking come back as JSON text from the LLM; parse if possible."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return {"raw": value}


async def run_pipeline(complaint_text: str, user_id: str = "officer_demo") -> dict:
    """Runs the full ACPIA pipeline for one complaint and returns a structured result.

    Also fires the immediate officer alert as soon as the Risk Assessment
    Agent flags the case URGENT, before the rest of the pipeline finishes.
    """
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=user_id)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    content = types.Content(role="user", parts=[types.Part(text=complaint_text)])
    logger.info(f"[intake] complaint received: {complaint_text}")

    alerted = False
    alert_info = None

    async for event in runner.run_async(
        user_id=user_id, session_id=session.id, new_message=content
    ):
        log_event(event)

        current_session = await session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session.id
        )
        state = current_session.state

        risk = state.get("risk_assessment")
        if risk and not alerted and risk.get("priority") == "URGENT":
            logger.info("[orchestrator] URGENT priority detected -> alerting officers now")
            alert_info = notify_officers(
                risk_score=risk["risk_score"],
                reason=risk["reason"],
                case_summary=risk["case_summary"],
            )
            alerted = True  # rest of the pipeline keeps running regardless

    final_session = await session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session.id
    )
    state = final_session.state

    risk_assessment = state.get("risk_assessment", {}) or {}
    evidence_collection = _safe_json(state.get("evidence_collection"))
    entity_linking = _safe_json(state.get("entity_linking"))
    final_summary = state.get("final_summary", "")

    priority = risk_assessment.get("priority", "STANDARD")
    disposition = "Sent to officers" if priority == "URGENT" else "Stored in database"

    return {
        "complaint_text": complaint_text,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "risk_assessment": risk_assessment,
        "evidence_collection": evidence_collection,
        "entity_linking": entity_linking,
        "final_summary": final_summary,
        "priority": priority,
        "disposition": disposition,
        "alerted": alerted,
        "alert_info": alert_info,
    }
