import os
import io
import zipfile
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# templates/<cloud> directory (…/src/templates/aws)
TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "aws"


def _ensure_lambda_zip(ws: str):
    """
    Create function.zip with a minimal Lambda handler if it's missing.
    Terraform expects 'function.zip' alongside your .tf files.
    """
    zpath = os.path.join(ws, "function.zip")
    if os.path.exists(zpath):
        return
    code = (
        "def lambda_handler(event, context):\n"
        "    return {'statusCode': 200, 'body': 'hello from lambda'}\n"
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("lambda_function.py", code)
    with open(zpath, "wb") as f:
        f.write(buf.getvalue())


def run(state):
    if "plan" not in state:
        raise ValueError("Missing 'plan' in state")

    ws = state["tf_workspace"]
    plan = state["plan"]
    use_local = state.get("localstack", False)

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

    def write(template_name: str):
        out_path = os.path.join(ws, template_name.replace(".j2", ""))
        rendered = env.get_template(template_name).render(**plan)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(rendered)

    # --- Provider (required) ---
    provider = "provider_localstack.tf.j2" if use_local else "provider_aws.tf.j2"
    provider_path = TEMPLATES_DIR / provider
    if not provider_path.exists():
        raise FileNotFoundError(f"Missing provider template: {provider_path.name}")
    write(provider)

    # --- Stack-specific templates ---
    if plan.get("stack") == "free_tier":
        # Lambda + DynamoDB (no ECS/RDS/ALB)
        plan.setdefault("lambda_runtime", "python3.11")
        plan.setdefault("table_name", "infraorchestrator_demo")
        for t in ["variables_free_tier.tf.j2", "lambda.tf.j2", "dynamodb.tf.j2"]:
            write(t)
        # ensure the lambda package exists
        _ensure_lambda_zip(ws)
    else:
        # ECS + RDS stack
        for t in ["vpc.tf.j2", "ecs_service.tf.j2", "rds_postgres.tf.j2", "variables.tf.j2", "outputs.tf.j2"]:
            write(t)

    return {"iac_workspace": ws}
