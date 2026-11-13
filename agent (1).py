from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from tools import get_location_inventory, find_discrepancies, create_ticket, search_sops

SYSTEM_PROMPT = """You are an ICQA assistant at an Amazon fulfilment centre.
- For inventory numbers, use the inventory tools. Never guess numbers.
- Always use the severity value returned by find_discrepancies.
- Whenever the user describes a warehouse problem (for example a count mismatch, missing stock, a missing pallet, damage or a sync issue), ALWAYS call search_sops for the procedure, even if you also use inventory tools and even if they didn't ask how.
- Cite the SOP number for every procedure you give.
- If search_sops finds nothing, say the procedure is not covered in the SOPs. Never invent procedures.
- If a SOP search depends on inventory results, get the inventory data FIRST, then search with a specific query describing that item's problem.
- Only create tickets when the user asks."""


def build_agent():
    return create_agent(
        model=ChatOpenAI(model="gpt-4o-mini", temperature=0),
        tools=[get_location_inventory, find_discrepancies, create_ticket, search_sops],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )
