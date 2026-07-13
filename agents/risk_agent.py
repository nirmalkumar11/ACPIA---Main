"""Agent 1: Risk Assessment Agent.

Entry point for every complaint. Extracts key facts and produces a
risk score (0-100) and priority (URGENT / STANDARD), written to session
state under the key "risk_assessment" so downstream agents can read it.
"""

from typing import List

from google.adk.agents import Agent
from pydantic import BaseModel, Field


class RiskAssessment(BaseModel):
    victim_age: str = Field(description="Age of the victim mentioned in the complaint, or 'unknown'")
    location: str = Field(description="Location mentioned in the complaint, or 'unknown'")
    case_type: str = Field(
        description="One of: missing_child, abuse, trafficking, neglect, cyber_exploitation, other"
    )
    keywords: List[str] = Field(description="Key terms extracted from the complaint")
    risk_score: int = Field(description="Calculated risk score from 0 to 100", ge=0, le=100)
    priority: str = Field(description="'URGENT' if risk_score >= 70, otherwise 'STANDARD'")
    reason: List[str] = Field(description="Short bullet reasons supporting the score")
    case_summary: str = Field(description="One-sentence plain-language summary of the complaint")


risk_agent = Agent(
    name="risk_assessment_agent",
    model="gemini-2.5-flash",
    description="Assesses an incoming child protection complaint for urgency and risk.",
    instruction="""
You are the Risk Assessment Agent in a child protection investigation system.
You are the first agent to see every complaint.

Given the complaint text below, extract:
- victim_age, location, case_type, and relevant keywords
- a risk_score from 0-100
- priority: "URGENT" if risk_score >= 70, else "STANDARD"
- reason: a short list of concrete reasons for the score
- case_summary: one plain sentence describing the situation

Guidance for scoring (be conservative, err toward higher risk when unsure):
- Missing child, trafficking indicators, or signs of immediate danger => high score (80-100)
- Ongoing abuse or cyber exploitation with a known suspect => high-moderate score (60-85)
- Neglect or a single ambiguous concern with no immediate danger signal => moderate score (30-60)
- Vague or unverifiable reports with no urgency markers => lower score (0-30)

The complaint text is the user message in this conversation turn.

Respond only with the structured fields requested. Do not add commentary outside the schema.
""",
    output_schema=RiskAssessment,
    output_key="risk_assessment",
)
