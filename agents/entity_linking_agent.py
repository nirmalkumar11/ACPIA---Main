"""Agent 3: Entity Linking Agent.

The core intelligence agent. Looks at entities extracted by the Evidence
Collection Agent (phone numbers, addresses, suspect names) and discovers
which cases share those entities, storing the links in a graph store
(Neo4j, or an in-memory fallback for the hackathon MVP).
"""

from google.adk.agents import Agent

from tools.neo4j_tool import get_relationships, link_entity_to_cases

entity_linking_agent = Agent(
    name="entity_linking_agent",
    model="gemini-2.5-flash",
    description="Finds hidden relationships between cases via shared entities and stores them in the graph.",
    instruction="""
You are the Entity Linking Agent, the most important intelligence agent in this system.

Evidence gathered so far:
{evidence_collection}

Steps:
1. Look at extracted_entities and the case IDs present in similar_cases / related_firs.
2. For each suspect name, phone number, and address, work out which case IDs it appears in
   (cross-reference similar_cases and related_firs by matching on suspect/phone/address fields).
3. Call link_entity_to_cases once per entity that appears in 2 or more cases, passing the
   entity value and the list of case IDs it connects.
4. After linking everything, call get_relationships to retrieve the full picture.

Respond with ONLY a single JSON object (no markdown fences, no prose) in exactly this shape:

{{
  "relationships": [
    {{"entity": "<entity value>", "related_cases": ["CASE_ID", "CASE_ID"]}}
  ]
}}

If no entity connects two or more cases, return {{"relationships": []}}.
""",
    tools=[link_entity_to_cases, get_relationships],
    output_key="entity_linking",
)
