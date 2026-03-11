import streamlit as st
import os
from datetime import datetime

from agents.financial_agents import run_financials_agent
from agents.news_agents import run_news_agent
from agents.sentiment_agents import run_sentiment_agent
from agents.memo_writer_agent import run_memo_writer_agent

st.set_page_config(
    page_title="Market Research Agent",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Multi-Agent Market Research System")
st.caption("Powered by OpenRouter · Financial Phrasebank · Yahoo Finance · Tavily")
st.divider()

with st.sidebar:
    st.header("Research Target")

    ticker = st.text_input(
        "Stock Ticker",
        value="NVDA",
        placeholder="e.g. AAPL, MSFT, BLK"
    ).upper().strip()

    company_name = st.text_input(
        "Company Name",
        value="NVIDIA",
        placeholder="e.g. Apple, Microsoft, BlackRock"
    ).strip()

    st.divider()
    st.markdown("### Agent Pipeline")
    st.markdown("""
    1. **Financials** — Yahoo Finance
    2. **News** — Tavily Search
    3. **Sentiment** — Kaggle Dataset
    4. **Memo Writer** — Synthesizes all
    """)

    st.divider()
    st.markdown("### Settings")
    show_raw = st.checkbox("Show raw agent outputs", value=False)

    run_button = st.button(
        "Generate Research Memo",
        type="primary",
        use_container_width=True
    )

if not run_button:
    st.markdown("""
    ### Welcome to the Multi-Agent Research System

    This system deploys **4 specialized AI agents** to research any
    publicly traded company and produce an institutional-grade
    investment memo in minutes.

    **How to use:**
    1. Enter a stock ticker and company name in the sidebar
    2. Click **Generate Research Memo**
    3. Watch each agent work in real time
    4. Download the final memo as a text file

    ---
    **Example companies to try:**
    - `NVDA` — NVIDIA
    - `BLK` — BlackRock
    - `AAPL` — Apple
    - `MS` — Morgan Stanley
    - `AQR` — AQR Capital
    """)

else:
    if not ticker or not company_name:
        st.error("Please enter both a ticker and company name.")
        st.stop()

    st.markdown(f"## Researching {company_name} ({ticker})")
    st.caption(f"Started at {datetime.now().strftime('%H:%M:%S')}")

    with st.status("Running Financials Agent...", expanded=True) as status:
        st.write("Fetching financial data from Yahoo Finance...")
        financials = run_financials_agent(ticker)

        if financials["status"] == "error":
            status.update(label="Financials Agent failed", state="error")
            st.error(financials["message"])
            st.stop()

        st.write("financial data fetched and analyzed")
        status.update(label="Financials Agent complete", state="complete")

    with st.status("Running News Agent...", expanded=True) as status:
        st.write("Searching for latest news and macro context...")
        news = run_news_agent(ticker, company_name, financials["sector"])

        if news["status"] == "error":
            status.update(label="News Agent failed", state="error")
            st.error(news["message"])
            st.stop()

        st.write(f"{len(news['raw_news'])} news articles analyzed")
        status.update(label="News Agent complete", state="complete")

    with st.status("Running Sentiment Agent...", expanded=True) as status:
        st.write("Analyzing sentiment against Financial Phrasebank dataset...")
        sentiment = run_sentiment_agent(ticker, company_name)

        if sentiment["status"] == "error":
            status.update(label="Sentiment Agent failed", state="error")
            st.error(sentiment["message"])
            st.stop()

        st.write(f"sentiment scored against {sentiment['baseline']['total_samples']:,} labeled sentences")
        status.update(label="Sentiment Agent complete", state="complete")

    with st.status("Writing Investment Memo...", expanded=True) as status:
        st.write("synthesizing all agent outputs...")
        memo = run_memo_writer_agent(financials, news, sentiment)

        if memo["status"] == "error":
            status.update(label="Memo Writer failed", state="error")
            st.error(memo["message"])
            st.stop()

        st.write("investment memo generated")
        status.update(label="Memo Writer complete", state="complete")

    st.success(f"Research complete — {company_name} ({ticker})")
    st.divider()

    raw = financials["raw_data"]
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Market Cap", f"${raw['valuation']['market_cap_B']}B")
    with col2:
        st.metric("Revenue", f"${raw['financials']['revenue_B']}B")
    with col3:
        st.metric("Operating Margin", f"{raw['financials']['operating_margin_pct']}%")
    with col4:
        st.metric("Analyst Target", f"${raw['analyst']['target_price']}")

    st.divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Investment Memo",
        "Financials",
        "News",
        "Sentiment",
        "Download"
    ])

    with tab1:
        st.markdown(memo["memo"])

    with tab2:
        st.markdown("### Financial Analysis")
        st.markdown(financials["analysis"])

        if show_raw:
            st.divider()
            st.markdown("### Raw Data")
            st.json(financials["raw_data"])

    with tab3:
        st.markdown("### News & Catalyst Analysis")
        st.markdown(news["analysis"])

        if show_raw:
            st.divider()
            st.markdown("### Raw News Items")
            for i, item in enumerate(news["raw_news"][:5], 1):
                with st.expander(f"[{i}] {item['title']}"):
                    st.write(item["content"])
                    st.caption(item["url"])

    with tab4:
        st.markdown("### Sentiment Analysis")

        ds = sentiment["dataset_signal"]
        bl = sentiment["baseline"]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Positive Sentiment",
                f"{float(ds['positive_pct']):.1f}%",
                delta=f"{float(ds['positive_pct']) - float(bl['positive_pct']):.1f}% vs baseline"
            )
        with col2:
            st.metric(
                "Negative Sentiment",
                f"{float(ds['negative_pct']):.1f}%",
                delta=f"{float(ds['negative_pct']) - float(bl['negative_pct']):.1f}% vs baseline",
                delta_color="inverse"
            )
        with col3:
            st.metric(
                "Neutral Sentiment",
                f"{float(ds['neutral_pct']):.1f}%",
                delta=f"{float(ds['neutral_pct']) - float(bl['neutral_pct']):.1f}% vs baseline"
            )

        st.divider()
        st.markdown(sentiment["analysis"])

        if show_raw:
            st.divider()
            st.markdown("### Similar Dataset Sentences")
            for item in sentiment["similar_sentences"][:5]:
                badge = "+" if item["sentiment"] == "positive" else \
                        "-" if item["sentiment"] == "negative" else "~"
                st.markdown(f"`[{badge}]` **{item['sentiment'].upper()}** — {item['text'][:150]}")

    with tab5:
        st.markdown("### Download Research Memo")
        st.caption(f"saved to: `{memo['saved_to']}`")

        st.download_button(
            label="Download Investment Memo (.txt)",
            data=memo["memo"],
            file_name=f"{ticker}_research_memo_{datetime.today().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )

        st.divider()
        st.caption("DISCLAIMER: This memo was generated by an AI multi-agent research system. All investment decisions require human review and approval.")