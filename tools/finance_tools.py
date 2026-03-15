import yfinance as yf
import pandas as pd
from typing import Any

def get_company_financials(ticker: str) -> dict[str, Any]:
    """
    Fetch key financial data for a given stock ticker.
    Returns a structured dict ready for the agent to consume.
    Includes retry logic with exponential backoff on rate limit.
    """
    
    for attempt in range(3):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            if not info or len(info) < 5:
                raise ValueError("Empty response from Yahoo Finance")

            # Core company info
            company_data = {
                "name": info.get("longName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "description": info.get("longBusinessSummary", "N/A")[:500],
                "employees": info.get("fullTimeEmployees", "N/A"),
                "country": info.get("country", "N/A"),
            }

            # Valuation metrics
            valuation = {
                "market_cap_B": round(info.get("marketCap", 0) / 1e9, 2),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "forward_pe": info.get("forwardPE", "N/A"),
                "pb_ratio": info.get("priceToBook", "N/A"),
                "ev_ebitda": info.get("enterpriseToEbitda", "N/A"),
            }

            # Financial health
            financials = {
                "revenue_B": round(info.get("totalRevenue", 0) / 1e9, 2),
                "gross_margin_pct": round(info.get("grossMargins", 0) * 100, 2),
                "operating_margin_pct": round(info.get("operatingMargins", 0) * 100, 2),
                "profit_margin_pct": round(info.get("profitMargins", 0) * 100, 2),
                "debt_to_equity": info.get("debtToEquity", "N/A"),
                "current_ratio": info.get("currentRatio", "N/A"),
                "free_cashflow_B": round(info.get("freeCashflow", 0) / 1e9, 2),
            }

            # Price performance
            price = {
                "current_price": info.get("currentPrice", "N/A"),
                "52w_high": info.get("fiftyTwoWeekHigh", "N/A"),
                "52w_low": info.get("fiftyTwoWeekLow", "N/A"),
                "50d_avg": info.get("fiftyDayAverage", "N/A"),
                "200d_avg": info.get("twoHundredDayAverage", "N/A"),
                "beta": info.get("beta", "N/A"),
            }

            # Analyst sentiment
            analyst = {
                "recommendation": info.get("recommendationKey", "N/A"),
                "target_price": info.get("targetMeanPrice", "N/A"),
                "num_analysts": info.get("numberOfAnalystOpinions", "N/A"),
            }

            return {
                "ticker": ticker.upper(),
                "company": company_data,
                "valuation": valuation,
                "financials": financials,
                "price": price,
                "analyst": analyst,
                "status": "success"
            }

        except Exception as e:
            if "rate" in str(e).lower() or "429" in str(e):
                wait = (attempt + 1) * 5  # 5s, 10s, 15s
                print(f"Rate limited. Attempt {attempt + 1}/3. Waiting {wait}s...")
                time.sleep(wait)
            else:
                return {"ticker": ticker, "status": "error", "message": str(e)}

    return {
        "ticker": ticker,
        "status": "error",
        "message": "Yahoo Finance rate limit exceeded. Please try again in 1 minute."
    }

def get_recent_price_history(ticker: str, period: str = "3mo") -> str:
    """
    Returns a summary of recent price movement as a string for the agent.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return "No price history available."

        start_price = round(hist["Close"].iloc[0], 2)
        end_price = round(hist["Close"].iloc[-1], 2)
        pct_change = round(((end_price - start_price) / start_price) * 100, 2)
        high = round(hist["Close"].max(), 2)
        low = round(hist["Close"].min(), 2)
        avg_volume = int(hist["Volume"].mean())

        direction = "up" if pct_change > 0 else "down"

        return (
            f"Over the last {period}: stock is {direction} {abs(pct_change)}% "
            f"(from ${start_price} to ${end_price}). "
            f"Range: ${low} - ${high}. Avg daily volume: {avg_volume:,}."
        )

    except Exception as e:
        return f"Error fetching price history: {str(e)}"    

if __name__ == "__main__":
    data = get_company_financials("NVDA")
    print("=== COMPANY ===")
    print(data["company"])
    print("\n=== VALUATION ===")
    print(data["valuation"])
    print("\n=== FINANCIALS ===")
    print(data["financials"])
    print("\n=== PRICE HISTORY ===")
    print(get_recent_price_history("NVDA"))            
