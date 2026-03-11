import sys
from agents.financial_agents import run_financials_agent
from agents.news_agents import run_news_agent
from agents.sentiment_agents import run_sentiment_agent
from agents.memo_writer_agent import run_memo_writer_agent

def run_research_pipeline(ticker: str, company_name: str) -> None:
    """
    Orchestrates all 4 agents in sequence to produce
    a complete investment research memo.
    """

    print(f"\n{'='*60}")
    print(f"MULTI-AGENT RESEARCH SYSTEM")
    print(f"   Researching: {company_name} ({ticker})")
    print(f"{'='*60}")

    # Step 1 — Financials Agent
    print("\n[1/4] Running Financials Agent...")
    financials = run_financials_agent(ticker)
    if financials["status"] == "error":
        print(f"Financials Agent failed: {financials['message']}")
        return

    # Step 2 — News Agent
    print("\n[2/4] Running News Agent...")
    news = run_news_agent(ticker, company_name, financials["sector"])
    if news["status"] == "error":
        print(f" News Agent failed: {news['message']}")
        return

    # Step 3 — Sentiment Agent
    print("\n[3/4] Running Sentiment Agent...")
    sentiment = run_sentiment_agent(ticker, company_name)
    if sentiment["status"] == "error":
        print(f"Sentiment Agent failed: {sentiment['message']}")
        return

    # Step 4 — Memo Writer Agent
    print("\n[4/4] Running Memo Writer Agent...")
    memo = run_memo_writer_agent(financials, news, sentiment)
    if memo["status"] == "error":
        print(f"Memo Writer failed: {memo['message']}")
        return

    # Done!
    print(f"\n{'='*60}")
    print(f"RESEARCH COMPLETE — {company_name} ({ticker})")
    print(f"{'='*60}")
    print(f"\n{memo['memo']}")
    print(f"\n Full memo saved to: {memo['saved_to']}")


if __name__ == "__main__":
    # Default to NVDA or accept command line argument
    if len(sys.argv) == 3:
        ticker = sys.argv[1].upper()
        company = sys.argv[2]
    else:
        ticker = "NVDA"
        company = "NVIDIA"

    run_research_pipeline(ticker, company)
