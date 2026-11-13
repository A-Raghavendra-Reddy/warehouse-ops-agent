import re
from dotenv import load_dotenv
load_dotenv()

from agent import build_agent
REFUSAL_PHRASES = ["not covered", "can't assist", "cannot assist", "don't have", "do not have", "unable to"]

TEST_CASES = [
    {"question": "A trailer came in but we can't find the goods. What do I do?",
     "must_cite": ["SOP-02"], "must_not_cite": ["SOP-03", "SOP-04"]},

    {"question": "How do I handle a damaged item?",
     "must_cite": ["SOP-03"], "must_not_cite": ["SOP-04"]},

    {"question": "An item has no hazmat classification. Can I stow it?",
     "must_cite": ["SOP-04"], "must_not_cite": ["SOP-03"]},

    {"question": "A PO isn't showing up in the WMS. What should I do?",
     "must_cite": ["SOP-05"]},

    {"question": "What should I do before I go home at the end of my shift?",
     "must_cite": ["SOP-06"]},

    {"question": "My cycle count doesn't match the system quantity.",
     "must_cite": ["SOP-01"], "must_not_cite": ["SOP-02"]},

    # SOP-06 (handover) is a useful extra here, but SOP-01 is the actual procedure,
    # so only SOP-01 is required.
    {"question": "Any discrepancies, and what should I do about the worst one?",
     "must_cite": ["SOP-01"], "must_contain": ["Headphones"]},

    {"question": "What's stored in zone-a?",
     "cite_nothing": True, "must_contain": ["Phone Case", "USB Cable"]},

    {"question": "How do I book annual leave?",
     "cite_nothing": True, "must_contain_any": REFUSAL_PHRASES},

    {"question": "What's on the canteen menu today?",
     "cite_nothing": True, "must_contain_any": REFUSAL_PHRASES},
]


def cited_sops(answer):
    return set(re.findall(r"SOP-\d+", answer))


def check(case, answer):
    problems = []
    cited = cited_sops(answer)

    for sop in case.get("must_cite", []):
        if sop not in cited:
            problems.append(f"missing {sop}")

    for sop in case.get("must_not_cite", []):
        if sop in cited:
            problems.append(f"wrongly cited {sop}")

    if case.get("cite_nothing") and cited:
        problems.append(f"should cite no SOP, cited {sorted(cited)}")

    for text in case.get("must_contain", []):
        if text.lower() not in answer.lower():
            problems.append(f"missing '{text}'")
            
    phrases = case.get("must_contain_any")
    if phrases:
        normalised = answer.lower().replace("’", "'")
        if not any(p in normalised for p in phrases):
            problems.append("did not clearly refuse")
            

    return problems


def run_eval():
    agent = build_agent()
    passed = 0

    for i, case in enumerate(TEST_CASES, 1):
        config = {"configurable": {"thread_id": f"eval-{i}"}}
        result = agent.invoke({"messages": [{"role": "user", "content": case["question"]}]}, config)
        answer = result["messages"][-1].content

        problems = check(case, answer)
        if problems:
            print(f"❌ {i}. {case['question']}\n      " + "; ".join(problems))
            print(f"      ANSWER: {answer[:300]}\n")
        else:
            passed += 1
            print(f"✅ {i}. {case['question']}")

    print(f"\nScore: {passed}/{len(TEST_CASES)}")


if __name__ == "__main__":
    run_eval()
