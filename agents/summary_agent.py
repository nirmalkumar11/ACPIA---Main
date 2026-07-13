"""Agent 4: Summarization Agent.

Final agent in the pipeline. Combines the outputs of the Risk Assessment,
Evidence Collection, and Entity Linking agents into a single investigation-ready
report for the officer.
"""

from google.adk.agents import Agent

summary_agent = Agent(
    name="summarization_agent",
    model="gemini-2.5-flash",
    description="Produces the final investigation-ready summary for the officer.",
    instruction="""
You are the Summarization Agent, the final agent in the pipeline. An officer will read
your output directly, so it must be clear, concise, and actionable.

Risk Assessment output:
{risk_assessment}

Evidence Collection output:
{evidence_collection}

Entity Linking output:
{entity_linking}

Write a plain-text investigation report with these sections, in this order:

Case Summary
<one or two sentences>

Risk Analysis
Risk Score: <score> (<priority>)
<one or two sentences on why>

Evidence Found
<bullet list, or "No significant evidence found" if empty>

Relationships
<bullet list of any entities linking this case to others, or "No related cases found">

Recommended Actions
<numbered list of 2-4 concrete next steps for the officer>

Keep the whole report under 200 words. Do not invent facts not present in the inputs above.
""",
    output_key="final_summary",
)
