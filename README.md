---
title: Market Research Agent
emoji: 📈
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.41.0"
app_file: app.py
pinned: true
---

# Market Research Agent

A multi-agent AI system that researches any publicly traded company
and produces an institutional-grade investment memo — the kind a
junior analyst at a hedge fund would spend hours producing manually.

Built as a portfolio project to demonstrate production-grade AI
engineering for quantitative finance use cases.

**Live Demo:** [Hugging Face Space](#) ← replace after deployment

---

## What It Does

Type a stock ticker. The system deploys 4 specialized AI agents in
sequence, each doing one job well, then synthesizes everything into
a structured investment memo with a clear BUY/SELL/HOLD stance.

```
Input:  "Research Blackstone (BLK)"
Output: 10-section investment memo with recommendation,
        risks, valuation assessment, and monitoring checklist
```

---

## Architecture

```
User Input (ticker + company name)
            │
            ▼
    ┌───────────────────┐
    │  Financials Agent │  ← Yahoo Finance API
    │  Valuation, margins, FCF, price history
    └────────┬──────────┘
             │
             ▼
    ┌───────────────────┐
    │    News Agent     │  ← Tavily Search API
    │  Latest news, catalysts, macro context
    └────────┬──────────┘
             │
             ▼
    ┌───────────────────┐
    │  Sentiment Agent  │  ← Financial Phrasebank (Kaggle)
    │  NLP scoring anchored to 4,846 labeled sentences
    └────────┬──────────┘
             │
             ▼
    ┌───────────────────┐
    │  Memo Writer Agent│  ← LLM synthesis
    │  Structured 10-section investment memo
    └────────┬──────────┘
             │
             ▼
    Investment Memo (rendered in UI + saved to file)
```

Each agent is a standalone Python module — independently testable,
replaceable, and observable. The orchestration is intentionally
manual (sequential pipeline) rather than framework-based, keeping
the system transparent and debuggable. LangGraph refactor is planned
for v2 to enable conditional routing and parallel execution.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.11 |
| AI/LLM | OpenRouter API (model-agnostic routing) |
| LLM Models | GPT-5 Nano, Gemini 2.5 Flash Lite (auto-routed) |
| Financial Data | yfinance (Yahoo Finance) |
| Web Search | Tavily Search API |
| Sentiment Dataset | Financial Phrasebank (Kaggle, 4,846 sentences) |
| Frontend | Streamlit |
| Environment | GitHub Codespaces |

---

## Key Design Decisions

**Model-agnostic via OpenRouter**
Rather than hardcoding a single LLM provider, the system routes
through OpenRouter's `auto` model, which dynamically selects the
best available model at runtime. This means zero vendor lock-in
and automatic cost optimization — during development the system
self-selected GPT-5 Nano and Gemini 2.5 Flash Lite on free tier.

**Separation of retrieval and reasoning**
`tools/` handles all data fetching. `agents/` handles all reasoning.
Neither layer knows about the other's implementation — clean
separation that makes each component independently testable
and replaceable.

**Grounded sentiment scoring**
The sentiment agent doesn't rely purely on LLM judgment. It anchors
its scoring against 4,846 labeled financial sentences from the
Financial Phrasebank dataset, comparing current news sentiment
against a statistical baseline. This reduces hallucination risk and
produces a defensible, data-backed signal.

**Keyword matching vs embeddings (deliberate tradeoff)**
Current similarity search uses keyword matching — lightweight,
zero infrastructure, works well for MVP. The natural upgrade path
is sentence embeddings with FAISS or Pinecone for semantic
similarity. Noted as TODO in the codebase.

**Audit trail by default**
Every memo is saved as a timestamped `.txt` file in `output/memos/`.
In a regulated environment like a hedge fund, auditability is
non-negotiable — this is built in from day one rather than
retrofitted.

---

## Project Structure

```
market-research-agent/
├── agents/
│   ├── financials_agent.py   # valuation + financial quality analysis
│   ├── news_agent.py         # news intelligence + catalyst analysis
│   ├── sentiment_agent.py    # NLP sentiment vs dataset baseline
│   └── memo_writer_agent.py  # synthesizes all agents into memo
├── tools/
│   ├── finance_tools.py      # yfinance data fetcher
│   ├── search_tools.py       # tavily news + macro search
│   └── llm_client.py         # openrouter LLM wrapper
├── data/
│   └── kaggle_sentiment/     # Financial Phrasebank dataset (gitignored)
├── output/
│   └── memos/                # generated memos, timestamped (gitignored)
├── app.py                    # streamlit UI
├── main.py                   # CLI entry point
└── requirements.txt
```

---

## Sample Output

Running `python main.py BLK "Blackstone"` produces:

```
═══════════════════════════════════════════════════════════
INVESTMENT RESEARCH MEMO
═══════════════════════════════════════════════════════════
Company:        Blackstone, Inc. (BLK)
Sector:         Financial Services
Date:           March 07, 2026
Prepared by:    Multi-Agent Research System v1.0
Classification: CONFIDENTIAL — FOR INTERNAL USE ONLY
═══════════════════════════════════════════════════════════

1. EXECUTIVE SUMMARY
   Bullish conviction. Despite a recent 9.53% pullback, forward P/E
   of 15.5 vs trailing P/E of 27.0 signals strong earnings growth
   expectations. $7.03B free cash flow and 36.7% operating margin
   confirm financial quality. Current price near 52W low represents
   a potential entry point.

2. INVESTMENT THESIS ...
3. FINANCIAL SNAPSHOT ...
...
9. RECOMMENDATION:  BUY  |  Target: $1,250 - $1,350
10. MONITORING CHECKLIST ...
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- GitHub Codespaces (recommended) or local environment
- API keys: OpenRouter, Tavily
- Kaggle Financial Phrasebank dataset

### Setup

```bash
# Clone the repo
git clone https://github.com/arti-awasthi/market-research-agent
cd market-research-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your API keys to .env

# Download Financial Phrasebank from Kaggle
# Place all-data.csv in data/kaggle_sentiment/
```

### Run via CLI

```bash
# Default (NVIDIA)
PYTHONPATH=$(pwd) python main.py

# Any company
PYTHONPATH=$(pwd) python main.py AAPL "Apple"
PYTHONPATH=$(pwd) python main.py BLK "Blackstone"
PYTHONPATH=$(pwd) python main.py MS "Morgan Stanley"
```

### Run via Streamlit UI

```bash
PYTHONPATH=$(pwd) streamlit run app.py
```

---

## Roadmap

### v2 — LangGraph Orchestration
Replace the sequential pipeline with a LangGraph state graph,
enabling:
- **Conditional routing** — trigger deeper risk analysis when
  sentiment score drops below threshold
- **Parallel execution** — run news and sentiment agents
  simultaneously, cutting pipeline time ~50%
- **Human in the loop** — pause for PM approval before
  finalising memo
- **Retry logic** — automatic agent retry on API failures

### v3 — Production Hardening
- Vector database (FAISS/Pinecone) for semantic similarity
  in sentiment agent — replacing keyword matching
- Embeddings-based company similarity search
- Nightly batch processing via Airflow for watchlist coverage
- Postgres storage for memo history and trend analysis
- REST API layer (FastAPI) for integration with fund systems

### v4 — Signal Validation
- Backtest sentiment scores against 30/60/90 day price returns
- Validate whether news sentiment is a statistically significant
  leading indicator
- Build confidence intervals around BUY/SELL/HOLD recommendations

---

## Limitations

- Sentiment similarity uses keyword matching, not embeddings —
  semantic nuance is lost
- No historical backtesting of whether sentiment signal predicts
  price movement
- LLM outputs are non-deterministic — same input may produce
  slightly different memos
- yfinance data has occasional gaps for smaller/international tickers
- Free tier LLMs via OpenRouter may have rate limits under
  heavy usage

---

## Part of a Larger Portfolio

This project is one of three AI/data engineering systems built
to demonstrate production-grade technical skills for quantitative
finance roles:

| Project | Focus | Stack |
|---|---|---|
| **Market Research Agent** (this) | Multi-agent AI, RAG | LangGraph, OpenRouter, Streamlit |
| **Alternative Data Pipeline** *(in progress)* | Data engineering | Databricks, Delta Lake, dbt, Airflow |
| **Quant Backtesting Framework** *(in progress)* | ML, signal research | Databricks, MLflow, Python |

---

## Author

**Arti Awasthi**

[LinkedIn](https://linkedin.com/in/arti-awasthi) ·
[GitHub](https://github.com/arti-awasthi)