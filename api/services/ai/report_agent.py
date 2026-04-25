from datetime import datetime

from typing_extensions import TypedDict

from api.core.config import settings
from api.services.email import send_email


class ReportState(TypedDict, total=False):
    email: str
    period: str
    summary: dict
    insights: list[str]
    recommendations: list[str]
    html: str


async def _summarize_node(state: ReportState) -> ReportState:
    return state


async def _insights_node(state: ReportState) -> ReportState:
    if not settings.GOOGLE_API_KEY:
        insights = [
            "Income and expenses were summarized without AI because GOOGLE_API_KEY is missing.",
        ]
        return {"insights": insights}

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        model = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.2,
        )
        prompt = (
            "Given this finance summary, return JSON with insights and recommendations arrays.\n"
            f"Period: {state['period']}\nSummary: {state['summary']}"
        )
        response = await model.ainvoke(prompt)
        content = getattr(response, "content", "")
        text = content if isinstance(content, str) else str(content)
        insights = [text]
        return {"insights": insights, "recommendations": []}
    except Exception as exc:
        return {"insights": [f"AI report insights unavailable: {exc}"], "recommendations": []}


async def _recommendations_node(state: ReportState) -> ReportState:
    recommendations = state.get("recommendations") or [
        "Review the highest expense category and set a target reduction for next month.",
        "Compare recurring expenses against income to protect savings rate.",
    ]
    return {"recommendations": recommendations}


async def _email_node(state: ReportState) -> ReportState:
    html = f"""
    <h2>Finora Monthly Report</h2>
    <p><strong>Period:</strong> {state['period']}</p>
    <pre>{state['summary']}</pre>
    <p>{'<br/>'.join(state.get('insights', []))}</p>
    <p>{'<br/>'.join(state.get('recommendations', []))}</p>
    <small>Generated at {datetime.utcnow().isoformat()}Z</small>
    """
    if state.get("email"):
        await send_email(state["email"], f"Finora report for {state['period']}", html)
    return {"html": html}


class _FallbackReportAgent:
    async def ainvoke(self, state: ReportState) -> ReportState:
        next_state = dict(state)
        next_state.update(await _summarize_node(next_state))
        next_state.update(await _insights_node(next_state))
        next_state.update(await _recommendations_node(next_state))
        next_state.update(await _email_node(next_state))
        return next_state


try:
    from langgraph.graph import END, StateGraph

    graph = StateGraph(ReportState)
    graph.add_node("summarize", _summarize_node)
    graph.add_node("insights", _insights_node)
    graph.add_node("recommendations", _recommendations_node)
    graph.add_node("email", _email_node)
    graph.set_entry_point("summarize")
    graph.add_edge("summarize", "insights")
    graph.add_edge("insights", "recommendations")
    graph.add_edge("recommendations", "email")
    graph.add_edge("email", END)
    report_agent = graph.compile()
except Exception:
    report_agent = _FallbackReportAgent()
