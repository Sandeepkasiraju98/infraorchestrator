def run(state):
    if state.get("free_tier", False):
        # Free-tier stack: API GW + Lambda + DynamoDB (no RDS/ECS/ALB)
        plan = {
            "stack": "free_tier",
            "service_name": "api",
            "lambda_runtime": "python3.11",
            "table_name": "infraorchestrator_demo",
            "tags": {"owner": "platform", "env": "dev"},
        }
    else:
        # ECS + RDS default
        plan = {
            "stack": "ecs_rds",
            "service_name": "api",
            "cpu": 256,
            "memory": 512,
            "replicas": 2,
            "db_instance": "db.t3.micro",
            "db_storage_gb": 20,
            "public": False,
            "tags": {"owner": "platform", "env": "dev"},
        }
    print(f"[Planner] stack={plan['stack']}")
    return {"plan": plan}
