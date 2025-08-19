# src/orchestrator/agents/cost_agent.py
PRICES = {
    "rds": {"db.t3.micro": {"hourly": 0.021}},
    "storage_gb_month": 0.10,
}

def estimate_rds(db_instance: str, storage_gb: int) -> float:
    hourly = PRICES["rds"][db_instance]["hourly"]
    storage = storage_gb * PRICES["storage_gb_month"]
    return hourly * 24 * 30 + storage

def run(state):
    plan = state.get("plan", {})
    budget = state.get("budget", 50)

    if plan.get("stack") == "free_tier":
        # Lambda + DynamoDB (simulated free), estimate $0
        est = 0.0
        over = False
    else:
        # ECS + RDS
        db_instance = plan.get("db_instance", "db.t3.micro")
        storage_gb = plan.get("db_storage_gb", 20)
        est = estimate_rds(db_instance, storage_gb)
        over = est > budget

    state.setdefault("reports", {}).setdefault("cost", {})
    state["reports"]["cost"].update({"estimate": round(est, 2), "over_budget": over})
    return {}
