import os
import pandas as pd
from dotenv import load_dotenv
from tools.search_tools import search_company_news
from tools.llm_client import call_llm


load_dotenv()

DATASET_PATH = "data/kaggle_sentiment/all-data.csv"

def load_sentiment_dataset() -> pd.DataFrame:
    """
    Loads the Financial Phrasebank dataset.
    Returns a clean dataframe with columns: sentiment, text
    """
    df = pd.read_csv(DATASET_PATH, encoding="latin-1", header=None)
    df.columns = ["sentiment", "text"]
    
    return df

def get_sentiment_distribution(df: pd.DataFrame) -> dict:
    """
    Returns the overall sentiment distribution of the dataset.
    Used as a baseline reference for comparison.
    """
    counts = df["sentiment"].value_counts()
    total = len(df)
    return {
        "positive_pct": round(float(counts.get("positive", 0) / total * 100), 1),
        "negative_pct": round(float(counts.get("negative", 0) / total * 100), 1),
        "neutral_pct": round(float(counts.get("neutral", 0) / total * 100), 1),
        "total_samples": total
    }  

def find_similar_sentences(query_headlines: list[str], df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Finds semantically similar sentences from the dataset
    using simple keyword matching.
    # TODO: replace with sentence embeddings + FAISS for semantic search
    """
    keywords = []
    for headline in query_headlines:
        words = [w.lower() for w in headline.split() if len(w) > 4]
        keywords.extend(words)

    # Score each row by keyword matches
    def score_row(text):
        text_lower = text.lower()
        return sum(1 for kw in keywords if kw in text_lower)  
    df = df.copy()
    df["match_score"] = df["text"].apply(score_row)
    top_matches = df[df["match_score"] > 0].sort_values("match_score", ascending=False).head(top_n)

    return top_matches


def run_sentiment_agent(ticker: str, company_name: str) -> dict:
    """
    Sentiment Agent — combines Kaggle financial sentiment dataset
    with live news headlines to produce a data-backed sentiment
    analysis for the investment memo.
    """

    print(f"\nSentiment Agent starting for {company_name} ({ticker})")

    # Step 1 — Load dataset and get baseline distribution
    df = load_sentiment_dataset()
    baseline = get_sentiment_distribution(df)

    # Step 2 — Fetch live headlines for this company
    news_items = search_company_news(company_name, ticker)
    headlines = [item["title"] for item in news_items if "error" not in item]
    if not headlines:
        return {"status": "error", "message": "No headlines found"}

    # Step 3 — Find similar sentences from dataset
    similar = find_similar_sentences(headlines, df, top_n=10)



    # Calculate sentiment distribution of similar sentences
    if not similar.empty:
        sim_counts = similar["sentiment"].value_counts()
        sim_total = len(similar)
        dataset_signal = {
            "positive_pct": round(float(sim_counts.get("positive", 0) / sim_total * 100), 1),
            "negative_pct": round(float(sim_counts.get("negative", 0) / sim_total * 100), 1),
            "neutral_pct": round(float(sim_counts.get("neutral", 0) / sim_total * 100), 1),
            "sample_count": sim_total
        }
        similar_sentences = similar[["sentiment", "text"]].to_dict("records")
    else:
        dataset_signal = baseline
        similar_sentences = []

    # Step 4 — Format for LLM prompt
    headlines_text = "\n".join([f"- {h}" for h in headlines[:10]])
    similar_text = "\n".join([
        f"[{s['sentiment'].upper()}] {s['text'][:120]}"
        for s in similar_sentences[:8]
    ])
    # Step 5 — LLM synthesizes a data-backed sentiment view
    prompt = f"""
You are a quantitative analyst at a hedge fund specializing in sentiment analysis.
Analyze the sentiment for {company_name} ({ticker}) using the following data.

## LIVE NEWS HEADLINES (today)
{headlines_text}

## SIMILAR SENTENCES FROM FINANCIAL PHRASEBANK DATASET
(These are labeled financial sentences similar in theme to current headlines.
Use this as a reference signal for how the market typically interprets such language.)
{similar_text}

## DATASET SENTIMENT SIGNAL
From {dataset_signal['sample_count']} similar financial sentences found in dataset:
- Positive: {dataset_signal['positive_pct']}%
- Negative: {dataset_signal['negative_pct']}%
- Neutral: {dataset_signal['neutral_pct']}%

## MARKET BASELINE (full 4,846 sentence dataset)
- Positive: {baseline['positive_pct']}%
- Negative: {baseline['negative_pct']}%
- Neutral: {baseline['neutral_pct']}%

---
Provide your sentiment analysis in the following structure:

### OVERALL SENTIMENT
(Positive / Negative / Neutral — with a confidence level: High / Medium / Low)

### SENTIMENT SCORE
(Score from -10 to +10, where -10 = extremely bearish, 0 = neutral, +10 = extremely bullish.
Format: SCORE: X/10 — one sentence justification.)

### SENTIMENT DRIVERS
(List the 3 most sentiment-impacting headlines and explain why each is positive/negative/neutral.)

### DATASET COMPARISON
(How does current sentiment compare to the dataset baseline?
Is this company's news more positive or negative than typical financial news?)

### SENTIMENT TREND RISK
(What could flip the sentiment from current levels? 2-3 specific triggers.)

### QUANT ANALYST NOTE
(One sharp paragraph suitable for inclusion in an investment memo.
Combine the dataset signal with live news into a single data-backed view.)

Be specific, reference actual headlines, and back every claim with data.
"""

    analysis = call_llm(prompt)

    print(f"Sentiment Agent complete for {company_name}")

    return {
        "ticker": ticker,
        "company_name": company_name,
        "headlines": headlines,
        "dataset_signal": dataset_signal,
        "baseline": baseline,
        "similar_sentences": similar_sentences,
        "analysis": analysis,
        "status": "success"
    }



if __name__ == "__main__":
    result = run_sentiment_agent("NVDA", "NVIDIA")
    if result["status"] == "success":
        print(f"\n{'='*60}")
        print(f"SENTIMENT ANALYSIS — {result['company_name']}")
        print(f"{'='*60}")
        print(f"\n Dataset Signal: {result['dataset_signal']}")
        print(f"Baseline: {result['baseline']}")
        print(f"\n{result['analysis']}")
    else:
        print(f"Error: {result['message']}")
