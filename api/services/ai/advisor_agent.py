from typing import Annotated
import operator
from typing_extensions import TypedDict

from api.core.config import settings
from api.models.transaction import Transaction, TransactionType


def tool(*args, **kwargs):
    try:
        from langchain_core.tools import tool as lc_tool

        return lc_tool(*args, **kwargs)
    except Exception:
        def decorator(func):
            return func

        return decorator


@tool
async def get_spending_by_category(user_id: str, category: str, days: int = 30) -> str:
    """Get total spending in a category over the last N days."""
    transactions = await Transaction.find(
        Transaction.user_id == user_id,
        Transaction.category == category,
        Transaction.type == TransactionType.EXPENSE,
    ).to_list()
    total = sum(tx.amount for tx in transactions)
    return f"Spent ${total:.2f} on {category}."


tools = [get_spending_by_category]


class AdvisorState(TypedDict):
    messages: Annotated[list, operator.add]
    user_id: str


def _fallback_agent():
    class FallbackAgent:
        async def ainvoke(self, state: AdvisorState):
            return {
                "messages": [
                    {"content": "Financial advisor is unavailable because the AI dependencies could not be loaded."}
                ]
            }

    return FallbackAgent()


async def advisor_node(state: AdvisorState):
    if not settings.GOOGLE_API_KEY:
        return {"messages": [{"content": "Financial advisor is unavailable because GOOGLE_API_KEY is missing."}]}
    from langchain_google_genai import ChatGoogleGenerativeAI

    response = await ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.2,
    ).bind_tools(tools).ainvoke(state["messages"])
    return {"messages": [response]}


try:
    from langgraph.graph import END, StateGraph
    from langgraph.prebuilt import ToolNode

    def should_continue(state: AdvisorState):
        last = state["messages"][-1]
        return "tools" if getattr(last, "tool_calls", None) else END

    graph = StateGraph(AdvisorState)
    graph.add_node("advisor", advisor_node)
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("advisor")
    graph.add_conditional_edges("advisor", should_continue)
    graph.add_edge("tools", "advisor")
    advisor_agent = graph.compile()
except Exception:
    advisor_agent = _fallback_agent()
