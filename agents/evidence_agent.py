"""Agent 2: Evidence Collection Agent.

Acts as a researcher: uses tools to pull similar past cases, missing-child
registry matches, and related police FIRs. Writes its findings to session
state under "evidence_collection" as JSON text for downstream agents.

Note: this agent uses tools, so it does not use output_schema (ADK does not
allow both on the same agent turn) -- instead it's instructed to return JSON.
"""

from google.adk.agents import Agent

from tools.case_search_tool import find_similar_cases
from tools.missing_child_tool import search_missing_child_records
from tools.police_tool import find_related_firs

evidence_agent = Agent(
    name="evidence_collection_agent",
    model="gemini-2.5-flash",
    description="Collects supporting evidence: similar cases, missing-child records, and FIRs.",
    instruction="""
You are the Evidence Collection Agent. You act as a researcher for the case below.

Case context (from the Risk Assessment Agent):
{risk_assessment}

Using the tools available to you:
1. Call find_similar_cases with the case's location (and case_type if known) to find similar past cases.
2. Call search_missing_child_records with the location if this looks like a missing-child case.
3. Call find_related_firs with the location, and with any suspect name or phone number you
   discover from the similar cases, to find related police FIRs.

After gathering results, respond with ONLY a single JSON object (no markdown fences, no prose)
in exactly this shape:

{{
  "similar_cases": [...],
  "missing_child_records": [...],
  "related_firs": [...],
  "extracted_entities": {{
    "suspects": [...],
    "phones": [...],
    "addresses": [...]
  }}
}}

extracted_entities should list every distinct suspect name, phone number, and address you
encountered across all tool results, so the next agent can cross-reference them.
""",
    tools=[find_similar_cases, search_missing_child_records, find_related_firs],
    output_key="evidence_collection",
)
