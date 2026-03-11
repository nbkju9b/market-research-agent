import os
import anthropic
import openai
from openai import OpenAI
from dotenv import load_dotenv
from tools.finance_tools import get_company_financials, get_recent_price_history
from tools.llm_client import call_llm

load_dotenv()

#api_key=os.getenv("OPENAI_API_KEY")

openrouter_api_key=os.getenv("OPENROUTER_API_KEY")

#client = OpenAI()

# client = OpenAI(
#     api_key=openrouter_api_key,
#     base_url="https://openrouter.ai/api/v1",
# )

def run_financials_agent(ticker: str) -> dict:
    """
    Financials Agent — fetches raw financial data and uses Claude
    to interpret it like a senior analyst would.
    Returns structured analysis ready for the memo writer.
    """

    print(f"\n Financials Agent starting for {ticker}...")

    # Step 1 — Fetch raw data using our tools
    financials = get_company_financials(ticker)
    price_history = get_recent_price_history(ticker)
    if financials["status"] == "error":
        return {"status": "error", "message": financials["message"]}

    # Step 2 — Build a rich prompt for Claude to analyze
    prompt = f"""
You are a senior equity analyst at a top-tier hedge fund.
Analyze the following financial data for {financials['ticker']} and provide 
a concise but sharp analyst-grade assessment.
## COMPANY OVERVIEW
Name: {financials['company']['name']}
Sector: {financials['company']['sector']}
Industry: {financials['company']['industry']}
Employees: {financials['company']['employees']}
Description: {financials['company']['description']}   

## VALUATION METRICS
Market Cap: ${financials['valuation']['market_cap_B']}B
Trailing P/E: {financials['valuation']['pe_ratio']}
Forward P/E: {financials['valuation']['forward_pe']}
Price/Book: {financials['valuation']['pb_ratio']}
EV/EBITDA: {financials['valuation']['ev_ebitda']}

## FINANCIAL HEALTH
Revenue: ${financials['financials']['revenue_B']}B
Gross Margin: {financials['financials']['gross_margin_pct']}%
Operating Margin: {financials['financials']['operating_margin_pct']}%
Profit Margin: {financials['financials']['profit_margin_pct']}%
Debt/Equity: {financials['financials']['debt_to_equity']}
Current Ratio: {financials['financials']['current_ratio']}
Free Cash Flow: ${financials['financials']['free_cashflow_B']}B

## PRICE PERFORMANCE
Current Price: ${financials['price']['current_price']}
52W High: ${financials['price']['52w_high']}
52W Low: ${financials['price']['52w_low']}
Beta: {financials['price']['beta']}
Recent Trend: {price_history}

## ANALYST CONSENSUS
Recommendation: {financials['analyst']['recommendation']}
Mean Price Target: ${financials['analyst']['target_price']}
Number of Analysts: {financials['analyst']['num_analysts']}

---
Provide your analysis in the following structure:

### VALUATION ASSESSMENT
(Is the stock cheap, fair, or expensive? Compare key ratios vs typical sector benchmarks. 2-3 sentences.)

### FINANCIAL QUALITY
(Assess margins, cash flow, and balance sheet strength. Any red flags or standout strengths? 2-3 sentences.)

### PRICE MOMENTUM
(What does recent price action tell us? How does it trade vs 52W range? 1-2 sentences.)

### ANALYST SENTIMENT
(What is the street saying? Is the consensus bullish, neutral, or bearish? 1-2 sentences.)

### KEY RISKS
(List 3 specific financial risks for this company based on the data above.)

### KEY STRENGTHS  
(List 3 specific financial strengths based on the data above.)

### ANALYST VERDICT
(One sharp paragraph summarizing your overall financial view — as if presenting to a PM at a hedge fund.)

Be specific, use the actual numbers, and avoid generic statements.
"""


# Step 3 — Claude analyzes the data
    # response = client.messages.create(
    #     model="claude-sonnet-4-20260514",
    #     max_tokens=1500,
    #     messages=[{"role": "user", "content": prompt}]
    # )

    #analysis = response.content[0].text

    # OpenAI model, not Claude[web:244][web:247]
    # response = client.responses.create(
    # model="gpt-4.1-mini",              
    # input=prompt)    

    # response = client.chat.completions.create(
    #     model="openrouter/free",   # or a specific free model id from the Free Models collection
    #     messages=[
    #         {"role": "system", "content": "You are a highly skilled equity analyst."},
    #         {"role": "user", "content": prompt},
    #     ],
    # )
    analysis = call_llm(prompt)

    #analysis = response.choices[0].message.content              
      
    #analysis = response.output[0].content[0].text
    print(f"Financials Agent complete for {ticker}")

    return {
        "ticker": ticker,
        "company_name": financials['company']['name'],
        "sector": financials['company']['sector'],
        "raw_data": financials,
        "price_history": price_history,
        "analysis": analysis,
        "status": "success"
    }

    # Quick test
if __name__ == "__main__":
    result = run_financials_agent("NVDA")
    if result["status"] == "success":
        print(f"\n{'='*60}") #banner looks nice
        print(f"FINANCIALS ANALYSIS — {result['company_name']}")
        print(f"{'='*60}") #banner looks nice
        print(result["analysis"])
    else:
        print(f"Error: {result['message']}")