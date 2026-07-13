"""ACPIA Orchestrator.

Chains the four worker agents in the order defined in the project brief:
Risk Assessment -> Evidence Collection -> Entity Linking -> Summarization.

The "alert officers immediately for urgent cases" branch is NOT modeled as
part of this graph -- it happens as a side effect the moment the Risk
Assessment Agent's output lands in session state, so the alert fires
immediately while the rest of the pipeline keeps running in the background.
See main.py for that logic.
"""

from google.adk.agents import SequentialAgent

from agents.risk_agent import risk_agent
from agents.evidence_agent import evidence_agent
from agents.entity_linking_agent import entity_linking_agent
from agents.summary_agent import summary_agent

root_agent = SequentialAgent(
    name="acpia_orchestrator",
    description=(
        "Processes a child protection complaint end to end: risk scoring, "
        "evidence collection, entity linking, and final summarization."
    ),
    sub_agents=[risk_agent, evidence_agent, entity_linking_agent, summary_agent],
)
