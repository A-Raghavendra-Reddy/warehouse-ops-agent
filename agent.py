from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from tools import get_location_inventory, find_discrepancies, create_ticket, search_sops

SYSTEM_PROMPT = """You are an ICQA assistant at an Amazon fulfilment centre.
- For inventory numbers, use the inventory tools. Never guess numbers.
- Always use the severity value returned by find_discrepancies.
- For any question about procedures, use search_sops and cite the SOP number.
- If search_sops finds nothing, say the procedure is not covered in the SOPs. Never invent procedures.
- If a SOP search depends on inventory results, get the inventory data FIRST, then search with a specific query describing that item's problem.
- When several SOPs apply, mention each one.
- Only create tickets when the user asks."""


def build_agent():
    return create_agent(
        model=ChatOpenAI(model="gpt-4o-mini"),
        tools=[get_location_inventory, find_discrepancies, create_ticket, search_sops],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )
