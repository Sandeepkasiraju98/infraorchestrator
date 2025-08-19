import os, tempfile, json
import click
from pathlib import Path
from .graph import app
from .runners.terraform import plan as tf_plan
from .runners.opa import free_tier_check

@click.command()
@click.argument("prompt", nargs=-1)
@click.option("--budget", default=50, help="Monthly budget in USD")
@click.option("--apply", is_flag=True, help="Apply terraform (dangerous). Off by default.")
@click.option("--db-user", default="appuser", help="DB username for Terraform (ECS/RDS stack)")
@click.option("--db-pass", default="StrongP@ssw0rd!", help="DB password for Terraform (ECS/RDS stack)")
@click.option("--free-tier", is_flag=True, help="Use Free Tier stack (API Gateway + Lambda + DynamoDB)")
@click.option("--localstack", is_flag=True, help="Target LocalStack instead of real AWS")
@click.option("--strict/--no-strict", default=True, help="Fail on any policy violation")
@click.option("--skip-tf", is_flag=True, help="Skip terraform (useful for CI)")
def main(prompt, budget, apply, db_user, db_pass, free_tier, localstack, strict, skip_tf):
    """Natural language → Terraform → (policy, cost) → plan. Safe by default."""
    prompt = " ".join(prompt)
    state = {
        "prompt": prompt,
        "context": {},
        "tf_workspace": tempfile.mkdtemp(prefix="iac_ws_"),
        "reports": {"policy": {}, "cost": {}},
        "budget": budget,
        "apply": apply,
        "free_tier": free_tier,
        "localstack": localstack,
    }

    # Run the LangGraph app (planner -> builder -> policy/cost placeholders)
    final = app.invoke(state)
    ws = final.get("iac_workspace") or final.get("tf_workspace")

    # Free-tier policy gate (blocks ECS/RDS/ALB when --free-tier is on)
    if free_tier:
        pol_dir = str(Path(__file__).resolve().parents[2] / "policies")
        os.makedirs(pol_dir, exist_ok=True)
        ft = free_tier_check(ws, pol_dir)
        if ft.get("violations"):
            print("\n❌ Free-tier policy violations:")
            for v in ft["violations"]:
                print(" -", v)
            if strict:
                print("\nAborting due to --strict.")
                print("\n=== SUMMARY ===")
                print(json.dumps(final.get("reports", {}), indent=2))
                print("Terraform workspace:", ws)
                return

    # Terraform (fmt/init/validate/plan). Apply is intentionally NOT automatic here.
    tf_result = {}
    if not skip_tf:
        try:
            tf_result = tf_plan(ws, db_user=db_user, db_pass=db_pass, localstack=localstack)
        except Exception as e:
            tf_result = {"error": str(e)}

    # Output summary
    print("\n=== SUMMARY ===")
    print(json.dumps(final.get("reports", {}), indent=2))
    print("Terraform workspace:", ws)
    if skip_tf:
        print("\n[terraform] skipped (--skip-tf)")
    elif "error" in tf_result:
        print("\n[terraform] error:", tf_result["error"])
    else:
        print("\nTerraform plan saved to:", os.path.join(ws, "plan.txt"))
        if apply:
            print("\n[info] --apply is acknowledged, but apply is intentionally disabled in CLI for safety.\n"
                  "       Run `terraform apply` manually inside the workspace if you want to create resources.")

if __name__ == "__main__":
    main()
