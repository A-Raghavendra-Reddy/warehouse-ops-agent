# Warehouse Ops Agent

An AI agent that helps ICQA teams in fulfilment centres find inventory discrepancies, assess severity, and raise investigation tickets through natural conversation.

Built from my experience as an ICQA/Operations Associate at an Amazon fulfilment centre.

## What it does
- Looks up inventory by location
- Compares system quantity vs physical count to find discrepancies
- Assigns severity (LOW / MODERATE / CRITICAL) using deterministic business rules
- Creates investigation tickets on request
- Remembers context across the conversation

## Tech stack
Python · LangChain · LangGraph · OpenAI GPT-4o-mini · pandas

## Project structure
```
data/inventory.csv   Sample WMS-style export (system vs physical counts)
tools.py             Tools the agent can call
agent.py             Agent setup: model, tools, prompt, memory
main.py              Terminal chat loop
```

## Engineering note: moving business rules out of the prompt
In the first version, the severity rule lived in the system prompt. The agent correctly calculated a 16.67% shortfall but labelled it LOW instead of MODERATE.

Fix: severity is now calculated in Python inside the `find_discrepancies` tool, and the prompt tells the agent to use the tool's value. Result: correct severity on every run.

Lesson: LLMs handle language and decisions well, but calculations and business rules belong in deterministic code.

## Run it locally
```
git clone https://github.com/A-Raghavendra-Reddy/warehouse-ops-agent
cd warehouse-ops-agent
python -m venv venv
venv\Scripts\activate        # Mac: source venv/bin/activate
pip install -r requirements.txt
```
Create a `.env` file containing `OPENAI_API_KEY=your-key`, then run:
```
python main.py
```

## Example
```
You: any discrepancies?
Agent: Found 3 — Headphones (CRITICAL, 100% missing), Inbound Pallet (MODERATE, 16.7% missing), USB Cable (LOW, 4.2% missing)
You: create tickets for all of them
Agent: Created WH-1001, WH-1002, WH-1003
```

## Roadmap
- [ ] RAG over warehouse SOP documents
- [ ] Web interface
- [ ] Deployment on AWS 
