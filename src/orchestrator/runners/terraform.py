import os, subprocess as sp, zipfile, io

HELLO_CODE = (
    "def lambda_handler(event, context):\n"
    "    return {'statusCode': 200, 'body': 'hello from lambda'}\n"
)

def _ensure_lambda_zip(ws: str):
    """Create function.zip with a minimal lambda_function.py if missing."""
    zpath = os.path.join(ws, "function.zip")
    if os.path.exists(zpath):
        return
    # write an in-memory zip to avoid stray files
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("lambda_function.py", HELLO_CODE)
    with open(zpath, "wb") as f:
        f.write(buf.getvalue())

def _run(cmd, cwd, env=None):
    return sp.run(cmd, cwd=cwd, text=True, capture_output=True, env=env)

def plan(ws, db_user="appuser", db_pass="StrongP@ssw0rd!", localstack=False):
    _ensure_lambda_zip(ws)

    env = os.environ.copy()
    # keep these for ECS/RDS path (ignored for free-tier)
    env["TF_VAR_db_user"] = db_user
    env["TF_VAR_db_pass"] = db_pass

    if localstack:
        env.setdefault("AWS_ACCESS_KEY_ID", "test")
        env.setdefault("AWS_SECRET_ACCESS_KEY", "test")
        env.setdefault("AWS_DEFAULT_REGION", "us-east-1")

    out = {}
    out["fmt"] = _run(["terraform", "fmt"], ws).stdout
    init = _run(["terraform", "init", "-input=false"], ws, env=env)
    out["init"] = init.stdout + "\n" + init.stderr
    val = _run(["terraform", "validate"], ws, env=env)
    out["validate"] = val.stdout + "\n" + val.stderr
    pl = _run(["terraform", "plan", "-input=false", "-no-color"], ws, env=env)
    out["plan"] = pl.stdout + "\n" + pl.stderr

    # save a copy of plan text
    with open(os.path.join(ws, "plan.txt"), "w", encoding="utf-8") as f:
        f.write(out["plan"])
    return out
