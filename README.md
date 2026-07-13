# ACPIA — Agentic Child Protection Investigation Assistant

Hackathon MVP built on **Google's Agent Development Kit (ADK)**. Four
specialized agents collaborate to triage a complaint, gather evidence,
link related cases, and produce an investigation-ready summary — with all
data backed by **mock datasets**, not real government systems.

## Architecture

```
Complaint
    │
    ▼
Risk Assessment Agent  ──URGENT?──▶ notify_officers() fires immediately
    │                                (pipeline keeps running either way)
    ▼
Evidence Collection Agent   (tools: case search, missing-child registry, FIRs)
    │
    ▼
Entity Linking Agent        (tool: graph store — Neo4j or in-memory)
    │
    ▼
Summarization Agent
    │
    ▼
Final report → officers (URGENT) or database (STANDARD)
```

## Setup

```bash
cd acpia
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

You'll need a Gemini API key available to ADK (e.g. `export GOOGLE_API_KEY=...`
or configure Vertex AI credentials — see the ADK docs for your environment).

## Run it

**Programmatic, single complaint (recommended for a demo):**
```bash
python main.py
```
This runs the sample complaint in `main.py`, prints the immediate alert (if
urgent) to the console, then the final report and disposition.

**Interactive CLI:**
```bash
adk run .
```

**Web UI** (lets you inspect each agent's reasoning, tool calls, and state):
```bash
adk web .
```

## Project structure

```
acpia/
├── agent.py                  # exposes root_agent for `adk run` / `adk web`
├── orchestrator.py           # SequentialAgent chaining all 4 agents
├── main.py                   # programmatic runner with alert-on-urgent logic
├── agents/
│   ├── risk_agent.py         # Agent 1: scores + prioritizes
│   ├── evidence_agent.py     # Agent 2: researches similar cases/records/FIRs
│   ├── entity_linking_agent.py  # Agent 3: finds shared-entity relationships
│   └── summary_agent.py      # Agent 4: writes the final report
├── tools/
│   ├── case_search_tool.py
│   ├── missing_child_tool.py
│   ├── police_tool.py
│   ├── neo4j_tool.py         # graph link/query tool used by Agent 3
│   └── alert_tool.py         # notify_officers(), used by main.py
├── database/
│   └── neo4j.py              # in-memory graph by default; real Neo4j if configured
├── mock_data/
│   ├── cases.json
│   ├── missing_children.json
│   └── police_records.json
└── requirements.txt
```

## Notes on scope (MVP, not production)

- All evidence sources (case history, missing-child registry, FIRs) are
  **mock JSON files**, not real government or police integrations.
- The graph store defaults to a simple **in-memory** dict; set
  `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` env vars to point it at a
  real Neo4j instance instead — the interface is identical either way.
- `notify_officers()` currently just logs to console. Swap in a real
  paging/SMS/dashboard integration before this touches real cases.
- **This system is decision support, not a decision-maker.** Every output
  is meant to help a human officer triage faster — final judgment and any
  action on a real complaint should always go through a person. Keep that
  boundary explicit if you extend this beyond the hackathon demo.

## Extending it

- Swap `InMemorySessionService` for a persistent session service to keep
  case history across runs.
- Add a `ParallelAgent` if you want Evidence Collection to query multiple
  tools concurrently rather than sequentially within one agent turn.
- Wire a real dashboard (the brief mentions: case submission, risk score,
  related cases, knowledge graph, generated summary) on top of `main.py`'s
  `process_complaint()` function — it returns everything the UI needs via
  session state.
