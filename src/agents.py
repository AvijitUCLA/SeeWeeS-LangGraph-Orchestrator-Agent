from __future__ import annotations
from typing import Dict, Any
from langchain_google_vertexai import ChatVertexAI
from prompts import PDF_CONTEXT_PROMPT, OPS_ANALYSIS_PROMPT, PLANNER_PROMPT, REPORT_PROMPT, AUDIT_PROMPT

llm = ChatVertexAI(
    model_name="gemini-2.5-flash",
    temperature=0.2,
    tags=["msba-demo", "multi-agent"],
    metadata={"repo": "MSBA_AI_Agents_Demo"}
)


def run_context_agent(snippets: str) -> str:
    return llm.invoke(PDF_CONTEXT_PROMPT.format_messages(snippets=snippets)).content

def run_ops_agent(summary: Dict[str, Any], kpis: Dict[str, Any], anomalies_md: str) -> str:
    return llm.invoke(OPS_ANALYSIS_PROMPT.format_messages(
        summary=summary, kpis=kpis, anomalies_md=anomalies_md
    )).content

def run_planner_agent(business_context: str, ops_insights: str, weather_risk: Dict[str, Any], audit_feedback: str = "") -> str:
    return llm.invoke(PLANNER_PROMPT.format_messages(
        business_context=business_context,
        ops_insights=ops_insights,
        weather_risk=weather_risk,
        audit_feedback=audit_feedback
    )).content

def run_audit_agent(business_context: str, dispatch_plan: str) -> str:
    return llm.invoke(AUDIT_PROMPT.format_messages(
        business_context=business_context,
        dispatch_plan=dispatch_plan
    )).content

def run_report_agent(
    business_context: str,
    kpis: Dict[str, Any],
    anomaly_highlights: str,
    weather_risk: Dict[str, Any],
    dispatch_plan: str,
) -> str:
    return llm.invoke(REPORT_PROMPT.format_messages(
        business_context=business_context,
        kpis=kpis,
        anomaly_highlights=anomaly_highlights,
        weather_risk=weather_risk,
        dispatch_plan=dispatch_plan
    )).content
