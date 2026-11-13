# Warehouse Ops Agent

An AI agent for fulfilment centre ICQA teams. It finds inventory discrepancies, assigns severity, raises tickets, and answers procedure questions from SOP documents, combining live data and documented knowledge in one conversation.

Built from my experience as an ICQA/Operations Associate at an Amazon fulfilment centre. All data and SOPs in this repo are simplified samples.

## What it does
- Looks up inventory by location
- Compares system quantity vs physical count to find discrepancies
- Assigns severity (LOW / MODERATE / CRITICAL) using deterministic business rules
- Answers procedure questions from SOP documents using RAG, citing the SOP number
- Refuses to answer when no SOP covers the question
- Creates investigation tickets on request
- Remembers context across the conversation

## Architecture
```
User ──> Agent (GPT-4o-mini + LangGraph)
            │
            ├── get_location_inventory ─┐
            ├── find_discrepancies ─────┼── data/inventory.csv
            ├── create_ticket           ┘
            └── search_sops ──> Chroma vector store ──> data/sops.txt
```
The agent decides which tools to call and in what order (agentic RAG), so one question can combine inventory numbers with the relevant procedure.

## Tech stack
Python · LangChain · LangGraph · OpenAI (GPT-4o-mini, text-embedding-3-small) · Chroma · pandas

## Project structure
```
data/inventory.csv   Sample WMS-style export (system vs physical counts)
data/sops.txt        Sample standard operating procedures
knowledge.py         SOP loading, chunking, vector store and retrieval
tools.py             Tools the agent can call
agent.py             Agent setup: model, tools, prompt, memory
main.py              Terminal chat loop
```

## Engineering notes

**1. Business rules belong in code, not prompts.**
With the severity rule in the system prompt, the agent calculated a 16.67% shortfall correctly but labelled it LOW instead of MODERATE. Severity is now calculated in Python inside `find_discrepancies`, and the agent uses the returned value.

**2. Check retrieval before blaming the LLM.**
A hazmat question returned "not covered" even though an SOP answered it. The vector store's default distance metric produced out-of-range relevance scores, so the right chunk fell below the threshold. Switching the collection to cosine similarity fixed it.

**3. Structure-aware chunking.**
Fixed-size chunking created a chunk containing only the document title, which scored as "relevant" to many questions. The SOPs are now split at each SOP heading, so every chunk is exactly one complete procedure, tagged with its SOP ID.

**4. Parallel vs sequential tool calls.**
The agent searched SOPs with a generic query at the same time as fetching inventory, before knowing which item was worst. A prompt rule now makes it fetch inventory first, then search with a query based on the result.

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
You: any discrepancies, and what should I do about the worst one?
Agent: Headphones in zone-c are CRITICAL (60 of 60 missing). Per SOP-01, recount the bin
       and check Product History before adjusting. Per SOP-06, flag it to the incoming
       lead at handover.

You: how do I book annual leave?
Agent: That procedure is not covered in the SOPs.
```

## Roadmap
- [x] v1: tools, memory, rule-based severity
- [x] v2: agentic RAG over SOP documents
- [ ] Evaluation set to measure answer quality
- [ ] Web interface
- [ ] Deployment on AWS

## Evaluation
`evaluate.py` runs 10 test questions covering every SOP, inventory-only questions, combined tool use and refusals. Each test checks which SOPs the answer must and must not cite.

```
python evaluate.py
```

| Run | Score | Change |
|---|---|---|
| Baseline | 6/10 | — |
| Retrieval fix | 7/10 | Absolute floor + relative margin on similarity scores |
| Tool selection fix | 8/10 | Docstring and prompt: always search SOPs when a problem is described; temperature 0 |
| Test corrections | 10/10 | Refusal check accepts any clear refusal; documented expectation change |

**5. Evals catch what spot-checks miss.** The baseline exposed four different failure types: irrelevant SOPs passing retrieval, a threshold broken by a chunking change, the agent not calling the search tool, and tests too strict on refusal wording. Each was diagnosed from traces and fixed separately, re-running the full set after every change.
