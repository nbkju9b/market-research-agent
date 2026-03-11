import os
from dotenv import load_dotenv
from tools.search_tools import search_company_news, search_macro_context
from tools.llm_client import call_llm

load_dotenv()

def run_news_agent(ticker: str, company_name: str, sector: str) -> dict:
    """
    News Agent — fetches live news and macro context, then uses
    the LLM to extract key themes, events, and risks like a
    senior analyst reading the morning briefing.
    """
    print(f"\n News Agent starting for {company_name} ({ticker})...")

    # Step 1 — Fetch live news and macro context
    news_items = search_company_news(company_name, ticker)
    macro_items = search_macro_context(sector)

    if not news_items or "error" in news_items[0]:
        return {"status": "error", "message": "Failed to fetch news"}

    # Step 2 — Format news for the prompt
    news_text = ""
    for i, item in enumerate(news_items, 1):
        news_text += f"\n[{i}] {item['title']}\n{item['content']}\n"

    macro_text = ""
    for i, item in enumerate(macro_items, 1):
        macro_text += f"\n[{i}] {item['title']}\n{item['content']}\n"

# Step 3 — LLM extracts insights like an analyst
    prompt = f"""
You are a senior analyst at a top hedge fund reading the morning news briefing.
Analyze the following news for {company_name} ({ticker}) and provide a sharp, 
concise intelligence report.

## COMPANY NEWS
{news_text}

## MACRO & SECTOR CONTEXT
{macro_text}

---
Provide your analysis in the following structure:

### HEADLINE SUMMARY
(2-3 sentences capturing the most important thing happening with this company right now.)

### KEY EVENTS & CATALYSTS
(List 3-4 specific recent events or upcoming catalysts that could move the stock.
Be specific — reference actual news items above.)

### EMERGING RISKS
(List 3 specific risks visible from the news — regulatory, competitive, macro, or operational.)

### MACRO TAILWINDS & HEADWINDS
(Based on sector context, what macro forces are helping or hurting this company? 2-3 sentences.)

### NEWS SENTIMENT SCORE
(Give an overall news sentiment score from 1-10, where:
1-3 = Very Negative, 4-5 = Negative, 6 = Neutral, 7-8 = Positive, 9-10 = Very Positive
Format: SCORE: X/10 — one sentence justification.)

### ANALYST WATCH POINTS
(What are the 2-3 most important things to monitor in the next 30-90 days based on this news?)

Be specific, reference actual news items, and avoid generic statements.
"""

    analysis = call_llm(prompt)

    print(f"✅ News Agent complete for {company_name}")

    return {
        "ticker": ticker,
        "company_name": company_name,
        "sector": sector,
        "raw_news": news_items,
        "raw_macro": macro_items,
        "analysis": analysis,
        "status": "success"
    }

   
if __name__ == "__main__":
    result = run_news_agent("NVDA", "NVIDIA", "Technology")
    if result["status"] == "success":
        print(f"\n{'='*60}")
        print(f"NEWS ANALYSIS — {result['company_name']}")
        print(f"{'='*60}")
        print(result["analysis"])
    else:
        print(f"Error: {result['message']}")