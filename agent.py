from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from tools import get_location_inventory, find_discrepancies, create_ticket

load_dotenv()

SYSTEM_PROMPT = """You are an ICQA assistant at an Amazon fulfilment centre.
Use tools for any inventory data. Never guess numbers.
Always use the severity value returned by find_discrepancies. Never calculate severity yourself.
Only create tickets when the user asks you to."""


def build_agent():
    llm = ChatOpenAI(model="gpt-4o-mini")
    return create_agent(
        model=llm,
        tools=[get_location_inventory, find_discrepancies, create_ticket],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )
