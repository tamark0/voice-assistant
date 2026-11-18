from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import ToolContext
from . import db
from .config import OLLAMA_MODEL

def get_vocabulary() -> dict:
    """Return the list of sign glosses that are available in the database."""
    return {"glosses": db.vocabulary()}

def lookup_signs(glosses: list[str], tool_context: ToolContext) -> dict:
    """Fetch sign videos for an ordered list of glosses and store them for the UI.

    Args:
        glosses: Ordered ASL glosses taken from get_vocabulary().
    Returns:
        Which glosses were found and which are missing.
    """
    found, missing = [], []
    for g in glosses:
        row = db.find(g)
        (found if row else missing).append(row if row else g)
    tool_context.state["signs"] = [{"gloss": g, "video": v} for g, v in found]
    tool_context.state["missing"] = missing
    return {"found": [g for g, _ in found], "missing": missing}

INSTRUCTION = """/no_think
You convert English sentences into an ordered sequence of ASL glosses.
Steps:
1. Call get_vocabulary to see the available glosses.
2. Map the user's sentence to glosses using ONLY words from that list, in
   a natural signing order. Drop filler words (a, the, is, are).
3. Call lookup_signs exactly once with the resulting list.
4. Reply with one short line listing the glosses used.
Never invent glosses that are not in the vocabulary."""

root_agent = Agent(
    name="sign_agent",
    model=LiteLlm(model=OLLAMA_MODEL, temperature=0.1),
    description="Maps English sentences to ASL glosses from a local vocabulary.",
    instruction=INSTRUCTION,
    tools=[get_vocabulary, lookup_signs],
)