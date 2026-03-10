
import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_company_news(company_name: str, ticker: str) -> list[dict]:
    """

   Fetch recent news for a company using Tavily. Returns deduplicated results.
    
    """
    try:
        queries = [
            f"{company_name} latest news 2026",
            f"{ticker} stock earnings revenue forecast",
            f"{company_name} risks challenges competitors",
        ]

        all_results = []

        for query in queries:
            response = client.search(
                query=query,
                search_depth="basic",
                max_results=3
            )
            for r in response.get("results", []):
                all_results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:400],
                    "query_used": query
                })

        # Deduplicate by URL
        seen = set()
        unique_results = []
        for item in all_results:
            if item["url"] not in seen:
                seen.add(item["url"])
                unique_results.append(item)

        return unique_results

    except Exception as e:
        return [{"error": str(e)}]


def search_macro_context(sector: str) -> list[dict]:
    """
    Fetches macro/sector level context relevant to the company.
    Useful for the memo's market environment section.
    """
    try:
        query = f"{sector} sector outlook risks opportunities 2026"
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=4
        )
        return [
            {
                "title": r.get("title", ""),
                "content": r.get("content", "")[:400],
                "url": r.get("url", "")
            }
            for r in response.get("results", [])
        ]
    except Exception as e:
        return [{"error": str(e)}]



if __name__ == "__main__":
    print("=== COMPANY NEWS ===")
    news = search_company_news("NVIDIA", "NVDA")
    for i, item in enumerate(news[:3], 1):
        print(f"\n[{i}] {item['title']}")
        print(f"    {item['content'][:150]}")

    print("\n=== MACRO CONTEXT ===")
    macro = search_macro_context("Technology")
    for i, item in enumerate(macro[:2], 1):
        print(f"\n[{i}] {item['title']}")
        print(f"    {item['content'][:150]}")
