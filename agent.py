"""Entry point ADK's CLI/Web UI looks for: exposes root_agent.

Run with:
    adk web .        # from inside the acpia/ folder, launches the web UI
    adk run .        # interactive CLI
"""

from orchestrator import root_agent  # noqa: F401
