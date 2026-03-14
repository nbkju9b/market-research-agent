LangGraph Refactor Attempt
===========================
Explored refactoring the sequential multi-agent pipeline into
a LangGraph StateGraph workflow for better state management,
parallel execution, and production-grade observability.

Why this was abandoned for v1:
-------------------------------
1. Sequential pipeline was the right call for v1 — easier to
   debug, reason about, and demonstrate clearly
2. LangGraph's StateGraph adds abstraction that obscures 
   agent boundaries — important to understand the flow 
   before abstracting it away
3. Framework overhead not justified at current scale —
   4 agents, 1 ticker at a time
4. Wanted working demo first, architecture upgrade second

Why LangGraph is the right choice for v2:
------------------------------------------
1. Parallel execution — financials + news run simultaneously
   cutting research time from ~45s to ~20s per ticker
2. Built-in state management via TypedDict ResearchState —
   NO MANUAL DATA PASSING between agents
3. Native checkpointing — agent remembers previous research
   sessions across runs
4. Conditional routing — agent adapts path based on what
   it observes, not hardcoded sequence
5. LangSmith integration — full observability and tracing
   out of the box

   Planned v2 architecture:
-------------------------
- LangGraph StateGraph replacing sequential pipeline
- FastMCP exposing tools as MCP server
- FAISS vector store upgrading keyword sentiment matching
- LangSmith for agent observability and tracing
- Parallel agent execution for 500+ ticker scaling

See v2/ folder for scaffolded architecture.

from typing import TypedDict, Optional

# v2 ResearchState — replaces manual data passing in v1

class ResearchState(TypedDict):
    ticker: str
    company: str
    financials: dict
    news: str
    sentiment: dict
    memo: str
    confidence_score: float
    messages: list
    error: Optional[str]

# TODO: implement after completing HF Agents Course Unit 2
# from langgraph.graph import StateGraph
# from langgraph.prebuilt import create_react_agent
# from langgraph.checkpoint.memory import MemorySaver


raise NotImplementedError(
        "v2 LangGraph workflow in progress. "
        "See v2/ folder for scaffolded architecture. "
        "Currently using v1 sequential pipeline — run main.py"
    )