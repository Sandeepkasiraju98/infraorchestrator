from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph
from .agents import planner, iac_builder, policy_agent, cost_agent, reporter

class OrchestratorState(TypedDict, total=False):
    prompt: str
    context: Dict[str, Any]
    tf_workspace: str
    iac_workspace: str
    reports: Dict[str, Any]
    budget: int
    apply: bool
    free_tier: bool
    localstack: bool
    plan: Dict[str, Any]

graph = StateGraph(OrchestratorState)

graph.add_node("plan", planner.run)
graph.add_node("build_iac", iac_builder.run)
graph.add_node("policy_check", policy_agent.run)
graph.add_node("cost_check", cost_agent.run)
graph.add_node("report", reporter.run)   # no-op is fine

graph.add_edge("plan", "build_iac")
graph.add_edge("build_iac", "policy_check")
graph.add_edge("policy_check", "cost_check")
graph.add_edge("cost_check", "report")

graph.set_entry_point("plan")
app = graph.compile()
