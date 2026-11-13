from dotenv import load_dotenv
load_dotenv()  # load the API key before anything that needs it

from agent import build_agent


def main():
    agent = build_agent()
    config = {"configurable": {"thread_id": "cli-session"}}
    print("Warehouse Ops Agent ready. Type 'quit' to exit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ("quit", "exit"):
            break
        if not question:
            continue
        result = agent.invoke({"messages": [{"role": "user", "content": question}]}, config)
        print(f"\nAgent: {result['messages'][-1].content}\n")


if __name__ == "__main__":
    main()
